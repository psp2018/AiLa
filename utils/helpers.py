import re
import textwrap
import json


def extract_article_number(text: str) -> str:
    match = re.search(r"article\s+(\d{1,3})\b", text, re.IGNORECASE)
    print(
        f"📄 HELPERS: Retrieved article number: {match.group(1)}"
        if match
        else "📄 No article number found."
    )
    return f"Article {match.group(1)}" if match else None


def normalize_article_id(article_id: str) -> str:
    return article_id.strip().lower().replace(" ", "").replace(":", "")


def extract_answer(response: dict, width: int = 90) -> str:
    """Extract and format the answer text from the response object."""
    raw_result = response.get("result", "")

    if isinstance(raw_result, dict):
        answer_text = raw_result.get("output_text", "")
    elif isinstance(raw_result, str):
        answer_text = raw_result
    else:
        return "⚠️ Unexpected response format."
    return format_answer(answer_text)


def format_answer_old(answer, width: int = 90) -> str:
    if not isinstance(answer, str):
        return "⚠️ Unable to format answer (not a string)"

    # Bold article references
    answer = re.sub(r"(Article\s\d+)", r"**\1**", answer)

    # Soft wrap for readability
    wrapped = textwrap.fill(answer, width=width)
    return wrapped


def format_answer(answer) -> str:
    """
    Formats the answer with clean markdown bullet points, preserving existing structure.
    Avoids adding redundant bullets to lines that already appear to be list items.
    """
    if not answer:
        return "No answer provided."

    if isinstance(answer, dict):
        answer = answer.get("result", "")
    if not isinstance(answer, str):
        answer = str(answer)

    answer = answer.strip()

    # Split into logical blocks
    paragraphs = [p.strip() for p in answer.split("\n") if p.strip()]
    formatted = []

    bullet_pattern = re.compile(
        r"""^(
        [\-\*\•]         |   # dash, asterisk or bullet
        \d+[\.\)]        |   # numbered list (1. or 2)
        [a-zA-Z][\.\)]       # a) or A.
    )\s""",
        re.VERBOSE,
    )

    for para in paragraphs:
        if bullet_pattern.match(para):
            formatted.append(para)
        else:
            formatted.append(f"- {para}")

    return "\n".join(formatted)


def extract_article_title(text):
    match = re.search(r"(Article\s+\d+)", text)
    return match.group(1) if match else None


def extract_sources(response: dict, max_preview_chars: int = 300) -> list:
    """
    Extract and format source documents from the RAG response.
    Returns a list of (title, preview, full_text) tuples.
    """
    sources = response.get("source_documents", [])
    formatted = []

    for i, doc in enumerate(sources):
        content = doc.page_content.strip().replace("\n", " ")
        preview = content[:max_preview_chars].strip()

        article = doc.metadata.get("article", f"Source {i + 1}")
        title = doc.metadata.get("title", "").strip()
        chapter = doc.metadata.get("chapter", "").strip()
        source = doc.metadata.get("source", "Unknown").upper()

        label = f"[{source}] {article}"
        if title:
            label += f" – {title}"
        if chapter:
            label += f" (Chapter {chapter})"

        formatted.append((label, preview, content))

    return formatted


def format_sources(sources):
    formatted = []
    for i, doc in enumerate(sources):
        content = doc.page_content.strip().replace("\n", " ")
        title = extract_article_title(content) or f"Source {i+1}"
        formatted.append((title, content[:300]))
    return formatted


def display_token_usage(callback_data, show=True):
    if show:
        return f"Tokens used: {callback_data.total_tokens} (Prompt: {callback_data.prompt_tokens}, Completion: {callback_data.completion_tokens}) | Cost: ${callback_data.total_cost:.4f}"
    return ""


def load_articles(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

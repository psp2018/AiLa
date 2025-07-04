import re

# """ def format_answer(answer) -> str:
#     """
#     Format the answer using markdown-style bullets where possible.
#     Tries to split dense legal rights into readable bullets.
#     """
#     if not answer:
#         return "No answer provided."

#     if isinstance(answer, dict):
#         answer = answer.get("result") or answer.get("output_text") or ""

#     if not isinstance(answer, str):
#         answer = str(answer)

#     answer = answer.strip()
#     if not answer:
#         return "No answer provided."

#     # Handle numbered or bulleted lists
#     lines = [line.strip() for line in answer.splitlines() if line.strip()]
#     is_list = all(
#         line.startswith(("-", "*", "•")) or re.match(r"^\d+[\.\)]\s", line)
#         for line in lines
#     )

#     if is_list:
#         return "\n".join(f"- {re.sub(r'^[-*•\d\.\)\s]+', '', line)}" for line in lines)

#     # Handle semicolon-separated phrases
#     if ";" in answer and len(answer) < 1000:
#         items = [item.strip() for item in answer.split(";") if item.strip()]
#         if len(items) > 2:
#             return "\n".join(f"- {item}" for item in items)

#     # Handle dense paragraphs with multiple sentence rights
#     # Split on ". " but preserve abbreviation like "e.g." or "Art."
#     sentence_candidates = re.split(r'(?<!\b\w\.\w)(?<=\.|\?)\s+', answer)
#     sentence_candidates = [s.strip() for s in sentence_candidates if s.strip()]
#     if len(sentence_candidates) >= 3:
#         return "\n".join(f"- {s}" for s in sentence_candidates)

#     return answer """


def format_answer(response):
    """
    Extracts and formats the answer and appends source references clearly.
    """
    result_text = (
        response.get("output_text", "") if isinstance(response, dict) else str(response)
    )
    sources = response.get("source_documents", [])

    if not sources:
        return result_text.strip()

    unique_sources = set()
    for doc in sources:
        article = doc.metadata.get("article", "").strip()
        source = doc.metadata.get("source", "").strip().upper()
        if article and source:
            unique_sources.add(f"• {article} [{source}]")

    sources_formatted = "\n".join(sorted(unique_sources))
    return f"{result_text.strip()}\n\n📚 **Sources:**\n{sources_formatted}"

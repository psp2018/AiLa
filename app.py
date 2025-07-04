import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.callbacks.manager import get_openai_callback
from chains.qa_chain_refine import build_qa_chain
from utils.helpers import extract_answer, extract_sources
import json

load_dotenv()

st.set_page_config(page_title="GDPR & FADP Assistant", layout="wide")

GA_MEASUREMENT_ID = "G-NVP6YKYWW5"  # Replace this with your actual ID

GA_SCRIPT = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{ dataLayer.push(arguments); }}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
"""

st.markdown(GA_SCRIPT, unsafe_allow_html=True)
st.title("📜 GDPR & FADP Assistant")

qa_chain = build_qa_chain()

# --- Tabs for interaction and exploration ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Ask data protection questions",
        "Browse articles",
        "Understand how it works",
        "Dev",
        "Legal Glossary",
    ]
)

with tab1:
    # st.subheader("Ask a question about GDPR or FADP")
    st.markdown("### 🤖 Ask a Question about GDPR or FADP")
    # st.markdown("---")

    query = st.text_input(
        "🔍 Type your question:",
        placeholder="e.g., What are the responsibilities of a data controller?",
    )

    if query:
        with st.spinner("🤔 AILA is thinking..."):
            with get_openai_callback() as cb:
                response = qa_chain(query)
                formatted_answer = extract_answer(response)

                st.markdown("### 💬 Answer:")
                st.markdown(formatted_answer)

                sources = extract_sources(response)
                st.markdown("---")
                if sources:
                    st.markdown("### 📚 Sources:")
                    for title, preview, full_text in sources:
                        with st.expander(f"📌 {title}"):
                            st.markdown(f"**Preview:** {preview}...")
                            st.markdown("---")
                            st.markdown("**Full Text:**")
                            st.write(full_text)
                else:
                    st.info("No sources returned for this answer.")

with tab2:
    # st.markdown("### 📚 Browse Articles")

    selected_regulation = st.selectbox("Choose a regulation", ["GDPR", "FADP"])
    filepath = (
        "data/gdpr_articles.json"
        if selected_regulation == "GDPR"
        else "data/swiss_fadp_articles.json"
    )

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        articles = []

    articles = sorted(articles, key=lambda x: x.get("article", ""))

    for entry in articles:
        with st.expander(f"{entry.get('article')} – {entry.get('title', '')}"):
            st.markdown(f"**Chapter:** {entry.get('chapter', '–')}")
            st.write(entry.get("body", "").strip())

            # Optional Ask AILA button
            if st.button(
                f"Ask AILA about {entry.get('article')}", key=entry["article"]
            ):
                st.session_state["preset_query"] = (
                    f"Explain {entry.get('article')} of {selected_regulation}"
                )
                st.experimental_rerun()
with tab3:
    # st.subheader("🛠️ AILA Under the Hood")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "app_assets/images/Aila_Architecture.png",
            caption="AILA System Architecture",
            use_container_width=True,
        )

    with col2:
        st.markdown(
            """
  AILA (AI Legal Assistant) is powered by a **Retrieval-Augmented Generation (RAG)** pipeline that ensures answers are precise, grounded in legal text, and fully explainable.

  ### 🧩 Key Components:
  - **User Query**: The user submits a GDPR/FADP question.
  - **Document Retrieval**: Relevant articles are fetched using a vector-based retriever (FAISS).
  - **LLM + Refine Chain**: An OpenAI model answers using *only* the retrieved documents.
  - **Formatting + Citations**: The output is formatted with bullet points and source previews.
  - **Indexing**: Articles are preprocessed into metadata-rich chunks stored in a combined index.

  ---

  ### 🔍 What is RAG?

  **RAG (Retrieval-Augmented Generation)** is a technique that blends:

  - **Search**: to retrieve the most relevant context (e.g., legal articles),
  - **Generation**: to create an answer based solely on that context.

  This design reduces hallucinations and ensures answers stay aligned with official GDPR/FADP content.
  """
        )

with tab4:
    # st.subheader("🛠 AILA Dev Panel")

    st.markdown("### ✅ Weekly Plan – Phase 2")
    st.markdown(
        """
    - [x] Beautify sources section
    - [ ] Enhance UI layout (padding, font size, spinner)
    - [ ] Add legal glossary section
    - [ ] Track usage with analytics
    - [ ] Add multi-turn chat
    """
    )

    st.markdown("### 🔍 Deployment Info")
    import subprocess

    try:
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
        branch_name = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode()
            .strip()
        )
    except Exception:
        commit_hash = "Unavailable"
        branch_name = "Unavailable"

    st.markdown(f"- **Branch:** `{branch_name}`")
    st.markdown(f"- **Commit:** `{commit_hash}`")
    st.markdown(f"- **Mode:** `Development`")

with tab5:
    st.subheader("📘 Legal Glossary – Key Terms in GDPR & FADP")

    glossary_terms = {
        "Personal Data": "Any information relating to an identified or identifiable natural person.",
        "Data Subject": "The individual to whom personal data relates.",
        "Controller": "The entity that determines the purposes and means of processing personal data.",
        "Processor": "The entity that processes data on behalf of the controller.",
        "Processing": "Any operation performed on personal data, whether automated or not.",
        "Consent": "Freely given, specific, informed, and unambiguous indication of the data subject's wishes.",
        "Data Protection Officer (DPO)": "An expert appointed to ensure compliance with data protection laws.",
        "Pseudonymisation": "Processing of data in such a way that it can no longer be attributed to a specific individual without additional information.",
        "Profiling": "Automated processing to evaluate personal aspects of an individual.",
        "Right to Access": "Data subject’s right to obtain confirmation and access to their personal data.",
        "Right to Erasure (Right to be Forgotten)": "Allows individuals to request deletion of their personal data.",
        "FDPIC": "Federal Data Protection and Information Commissioner (Switzerland).",
    }

    for term, definition in glossary_terms.items():
        with st.expander(term):
            st.write(definition)


# --- Simulated Bottom Bar ---
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    model = "GPT-3.5 / GPT-4"
    st.markdown(f"**Model:** {model}")

with col2:
    st.markdown("**Data Sources:** GDPR (EU), FADP (Switzerland)")

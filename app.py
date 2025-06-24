import os
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from chains.qa_chain_refine import build_qa_chain
from utils.helpers import extract_answer, extract_sources
import json

load_dotenv()

st.set_page_config(page_title="GDPR & FADP Assistant", layout="wide")
st.title("📜 GDPR & FADP Assistant")

qa_chain = build_qa_chain()

# --- Tabs for interaction and exploration ---
tab1, tab2, tab3 = st.tabs(["🤖 Ask GDPR questions", "📖 Browse GDPR Articles", "📖 Aila under the hood"])

with tab1:
    st.subheader("Ask a question about GDPR or FADP")
    query = st.text_input("🔍 Type your question:")

    if query:
        with get_openai_callback() as cb:
            response = qa_chain(query)
            formatted_answer = extract_answer(response)

            st.markdown("### 💬 Answer:")
            st.markdown(formatted_answer)

            sources = extract_sources(response)
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
    st.markdown("### 📚 Browse Articles")

    selected_regulation = st.selectbox("Choose a regulation", ["GDPR", "FADP"])
    filepath = "data/gdpr_articles.json" if selected_regulation == "GDPR" else "data/swiss_fadp_articles.json"

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
            if st.button(f"Ask AILA about {entry.get('article')}", key=entry["article"]):
                st.session_state["preset_query"] = f"Explain {entry.get('article')} of {selected_regulation}"
                st.experimental_rerun()
with tab3:
        #st.subheader("🛠️ AILA Under the Hood")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image("app_assets/images/AILA_Architecture.png", caption="AILA System Architecture",
                     use_container_width=True)

        with col2:
            st.markdown("""
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
  """)

# --- Simulated Bottom Bar ---
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    model = "GPT-3.5 / GPT-4"
    st.markdown(f"**Model:** {model}")

with col2:
    st.markdown("**Data Sources:** GDPR (EU), FADP (Switzerland)")

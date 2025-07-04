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
tab1, tab2, tab3, tab5 = st.tabs(
    [
        "Ask data protection questions",
        "Browse articles",
        "Lets get you started",
        # "Legal Glossary",
        "Under the hood",
    ]
)

with tab1:
    # st.subheader("Ask a question about GDPR or FADP")
    st.markdown(
        "### 🤖 Ask a Question about GDPR or FADP or head to -lets get you started- tab for some common questions"
    )
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
    # st.subheader("🛠 AILA Dev Panel")

    st.markdown(
        "### ✅ These are some common questions that get asked. We hope they help you get started!"
    )
    st.markdown(
        """
    #### **Category 1: The Basics & Applicability**
    *For users asking "Does this even apply to me?"*
    - I'm a US-based company with a website that gets some traffic from Europe. Does GDPR apply to me?
    - What is the main difference between the EU's GDPR and Switzerland's new FADP?
    - My company is in Germany, but we have many Swiss customers. Which law is more important for me to follow?
    - What exactly counts as "personal data"? Does an IP address or a user ID qualify?
    - What does the principle of "privacy by design" mean for my startup's new product?

    ---

    #### **Category 2: Website, Cookies & Marketing**
    *For marketers and front-end developers*
    - Do I really need a cookie banner? What are the specific rules for it to be compliant?
    - Can I still use Google Analytics? If so, how must I configure it to be compliant with GDPR?
    - Can my sales team send cold marketing emails to a list of business contacts?
    - What information is absolutely required in my website's privacy policy?
    - A user signed up for my newsletter. Can I use their email for other marketing purposes?

    ---

    #### **Category 3: User Rights & Data Handling**
    *For product managers and support teams*
    - A user has requested a copy of all their data. What do I have to provide and how quickly?
    - What is the "right to be forgotten" and are there any situations where I can refuse to delete a user's data?
    - How do I handle a data access request from a user in Switzerland under the FADP?
    - What is a "Data Processing Record" or "ROPA" and does my small business need to maintain one?
    - What is "data minimization" and can you give me a practical example for an e-commerce store?

    ---

    #### **Category 4: Tech Stack, Vendors & International Transfers**
    *For CTOs and technical leads*
    - My entire platform is built on AWS. Does their compliance mean my company is compliant?
    - What is a Data Processing Addendum (DPA) and do I need one with my SaaS vendors like Stripe or Mailchimp?
    - I use a software tool from a company based in the USA. What do I need to ensure that data transfer is legal?
    - What are the technical security measures (like encryption and pseudonymization) that are recommended under GDPR?
    - Does the new Swiss FADP have the same strict rules on transferring data outside of Switzerland as GDPR?

    ---

    #### **Category 5: Risk, Breaches & Enforcement**
    *For founders and management*
    - What are the very first steps I must take if I discover my company has had a data breach?
    - When is a company legally required to appoint a Data Protection Officer (DPO)?
    - Are the fines under the new FADP as high as the fines under GDPR?
    - Do I need to appoint a representative in Switzerland if my business is based in the EU?
    - What is the most common mistake a small business makes that leads to a privacy fine?
    - How can I ensure my employees are trained on data protection best practices?
    """
    )

# with tab4:
#     st.subheader("📘 Legal Glossary – Key Terms in GDPR & FADP")

#     glossary_terms = {
#         "Personal Data": "Any information relating to an identified or identifiable natural person.",
#         "Data Subject": "The individual to whom personal data relates.",
#         "Controller": "The entity that determines the purposes and means of processing personal data.",
#         "Processor": "The entity that processes data on behalf of the controller.",
#         "Processing": "Any operation performed on personal data, whether automated or not.",
#         "Consent": "Freely given, specific, informed, and unambiguous indication of the data subject's wishes.",
#         "Data Protection Officer (DPO)": "An expert appointed to ensure compliance with data protection laws.",
#         "Pseudonymisation": "Processing of data in such a way that it can no longer be attributed to a specific individual without additional information.",
#         "Profiling": "Automated processing to evaluate personal aspects of an individual.",
#         "Right to Access": "Data subject’s right to obtain confirmation and access to their personal data.",
#         "Right to Erasure (Right to be Forgotten)": "Allows individuals to request deletion of their personal data.",
#         "FDPIC": "Federal Data Protection and Information Commissioner (Switzerland).",
#     }

#     for term, definition in glossary_terms.items():
#         with st.expander(term):
#             st.write(definition)

with tab5:
    # st.subheader("🛠️ AILA Under the Hood")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "app_assets/images/Aila_architecture.png",
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
# --- Simulated Bottom Bar ---
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    model = "GPT-3.5 / GPT-4"
    st.markdown(f"**Model:** {model}")

with col2:
    st.markdown("**Data Sources:** GDPR (EU), FADP (Switzerland)")

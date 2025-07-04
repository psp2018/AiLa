import os
from langchain.llms import OpenAI
from langchain.chains import RefineDocumentsChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from utils.loader import load_and_split_documents
from utils.formatting import format_answer
from utils.helpers import extract_article_number

from vectorcode import build_vectorstore


def detect_regulation(query, override=None):
    if override and override.lower() in ["gdpr", "fadp"]:
        return override.upper()
    query = query.lower()
    if "gdpr" in query or "european" in query:
        return "GDPR"
    elif "fadp" in query or "swiss" in query or "switzerland" in query:
        return "FADP"
    return None


def build_qa_chain():
    index_path = "faiss_index_combined"
    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(
            index_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True
        )
    else:
        docs_gdpr = load_and_split_documents(
            "data/gdpr_articles.json", source_label="GDPR"
        )
        docs_fadp = load_and_split_documents(
            "data/swiss_fadp_articles.json", source_label="FADP"
        )
        docs = docs_gdpr + docs_fadp
        vectorstore = build_vectorstore(docs, persist_path=index_path)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

    initial_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a GDPR or FADP legal assistant. Use only the context below to answer the user's question.
Be precise and answer solely based on the relevant article(s) present in the context.

❗ Do NOT refer to or summarize other articles unless the question explicitly asks for them.

Context:
{context}

Question:
{question}

Answer:""",
    )

    refine_prompt = PromptTemplate(
        input_variables=["context", "existing_answer"],
        template="""You have already provided an answer based on a previous context.

Now, consider the new context below. Refine the existing answer **only if** the new context offers **more relevant or clearer information**.

🚫 Do NOT introduce information from outside the new context. Avoid referring to unrelated articles.

Existing answer:
{existing_answer}

New context:
{context}

If the new context improves the answer, rewrite it. Otherwise, return the original.

Refined answer:""",
    )

    llm = OpenAI(temperature=0)
    refine_chain = RefineDocumentsChain(
        initial_llm_chain=LLMChain(llm=llm, prompt=initial_prompt),
        refine_llm_chain=LLMChain(llm=llm, prompt=refine_prompt),
        document_variable_name="context",
        initial_response_name="existing_answer",
    )

    def is_gdpr_query(query):
        keywords = [
            "article",
            "gdpr",
            "fadp",
            "data protection",
            "privacy",
            "personal data",
            "controller",
            "processor",
            "data subject",
            "rights",
            "law",
            "regulation",
            "data minimisation",
            "data minimization",
            "jurisdictions",
            "institutional beneficiaries",
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    def invoke(query, regulation_override=None):
        if not is_gdpr_query(query):
            return {
                "result": "⚠️ This assistant only answers questions related to data protection laws such as GDPR and FADP. Please ask a legal or privacy-related question.",
                "source_documents": [],
            }

        all_documents = retriever.get_relevant_documents(query)
        if not all_documents:
            return {"result": "No relevant documents found.", "source_documents": []}

        target_article = extract_article_number(query)
        print("QA_CHAIN_REFINE: target article", target_article)
        regulation = detect_regulation(query, override=regulation_override)
        print("QA_CHAIN_REFINE: regulation", regulation)

        filtered_docs = all_documents
        if regulation:
            filtered_docs = [
                doc
                for doc in all_documents
                if doc.metadata.get("source", "").lower() == regulation.lower()
            ]

        documents = filtered_docs or all_documents

        # Show articles retrieved for debug
        print("QA_CHAIN_REFINE: Retrieved articles:")
        for doc in documents:
            print(f"- {doc.metadata.get('article')} [{doc.metadata.get('source')}]")

        # Normalize target_article
        target_article_norm = target_article.strip().lower() if target_article else ""

        if target_article:
            exact_match = [
                doc
                for doc in documents
                if doc.metadata.get("article", "").strip().lower()
                == f"article {target_article_norm}".strip()
            ]

            if exact_match:
                documents = exact_match
            else:
                partial_match = [
                    doc
                    for doc in documents
                    if target_article_norm in doc.page_content.lower()
                    or target_article_norm in doc.metadata.get("article", "").lower()
                ]
                if partial_match:
                    documents = partial_match
                else:
                    print(f"📛 No documents found matching '{target_article}'")
                    print("📄 QA_CHAIN_REFINE: Available articles in retrieved docs:")
                    for doc in documents:
                        print(
                            f"- {doc.metadata.get('article')} [{doc.metadata.get('source')}]"
                        )
                    return {
                        "result": f"No article found matching {target_article}. Please check the article number.",
                        "source_documents": [],
                    }

        result = refine_chain.invoke({"input_documents": documents, "question": query})

        formatted = format_answer(result)

        return {"result": formatted, "source_documents": documents}

    return invoke

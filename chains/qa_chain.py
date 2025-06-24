from langchain.llms import OpenAI
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from utils.formatting import format_answer
from utils.helpers import extract_article_number

from utils.loader import load_and_split_documents
from vectorcode import build_vectorstore

def build_qa_chain():
    docs = load_and_split_documents("data/gdpr_articles.txt")
    vectorstore = build_vectorstore(docs)
    retriever = vectorstore.as_retriever()

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=""""
You are a GDPR legal assistant. Use only the context below to answer the question. Be accurate and concise.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""""
    )

    llm = OpenAI(temperature=0)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    qa_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context"
    )

    def invoke(query):
        all_documents = retriever.get_relevant_documents(query)
        if not all_documents:
            return {
                "result": "No relevant documents found.",
                "source_documents": []
            }

        # Try filtering by article number if present
        target_article = extract_article_number(query)
        if target_article:
            filtered_docs = [
                doc for doc in all_documents
                if target_article.lower() in doc.page_content.lower()
            ]
            documents = filtered_docs or all_documents  # fallback if no match found
        else:
            documents = all_documents

        result = refine_chain.invoke({
            "input_documents": documents,
            "question": query
        })

        formatted = format_answer(result)

        return {
            "result": formatted,
            "source_documents": documents
        }
    return invoke

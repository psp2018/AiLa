import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def build_vectorstore(documents, persist_path="faiss_index"):
    print(f"🔢 Building vector store from {len(documents)} documents")
    from langchain.vectorstores import FAISS
    from langchain.embeddings import OpenAIEmbeddings

    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())
    vectorstore.save_local(persist_path)
    return vectorstore

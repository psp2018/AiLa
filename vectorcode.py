import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def build_vectorstore(documents, persist_path="faiss_index"):
    print(f"🔢 Building vector store from {len(documents)} documents")

    # Instantiate embeddings using the new API
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Build and persist the FAISS vector store
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(persist_path)
    return vectorstore

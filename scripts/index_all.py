from dotenv import load_dotenv

from utils.loader import load_and_split_documents
from vectorcode import build_vectorstore

load_dotenv()

gdpr_docs = load_and_split_documents("data/gdpr_articles.json", source_label="GDPR")
fadp_docs = load_and_split_documents("data/swiss_fadp_articles.json", source_label="FADP")
all_docs = gdpr_docs + fadp_docs
print(f"📦 Indexed {len(gdpr_docs)} GDPR documents")
print(f"📦 Indexed {len(fadp_docs)} FADP documents")

vectorstore = build_vectorstore(all_docs, persist_path="faiss_index_combined")
print("✅ Combined FAISS index saved")

print(f"Loaded {len(gdpr_docs)} GDPR chunks")
print(f"Loaded {len(fadp_docs)} FADP chunks")
print(f"Total chunks to index: {len(all_docs)}")

import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


def load_and_split_documents(
    json_path, chunk_size=300, chunk_overlap=50, source_label=None
):
    print(f"📖 LOADER: Loading from {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"📄 Loaded {len(data)} articles")
    documents = []
    for entry in data:
        article_id = entry.get("article", "Unknown")
        chapter = entry.get("chapter", "Unknown")
        title = entry.get("title", "")
        body = entry.get("body", "").strip()

        # Build clean metadata
        metadata = {"article": article_id, "chapter": chapter}
        if source_label:
            metadata["source"] = source_label.upper()
        text = f"{article_id}\n{title}\n\n{body}"
        # documents.append(Document(page_content=body, metadata=metadata))
        documents.append(Document(page_content=text, metadata=metadata))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    split_docs = []

    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for chunk in chunks:
            # Clean chunk with consistent header
            header = f"{doc.metadata['article']}\nChapter: {doc.metadata['chapter']}\n"
            if header.strip() not in chunk:
                chunk_with_header = f"{header.strip()}\n\n{chunk.strip()}"
            else:
                chunk_with_header = chunk.strip()
            if len(chunk.strip()) < 20:
                print(f"⚠️ Short chunk: {repr(chunk_with_header[:100])}")
            split_docs.append(
                Document(page_content=chunk_with_header, metadata=doc.metadata)
            )
            # for doc in split_docs:
            #    if "article 2" in doc.page_content.lower():
            #        print("✅ Chunk contains Article 2:\n", doc.page_content[:200])
    print("✅ LOADER: Indexed article list:")
    indexed_articles = {doc.metadata["article"] for doc in split_docs}
    for article in sorted(indexed_articles):
        print("-", article)

    return split_docs

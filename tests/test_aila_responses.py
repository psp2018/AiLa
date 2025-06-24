import os
import datetime
import csv

from dotenv import load_dotenv

from chains.qa_chain_refine import build_qa_chain

load_dotenv()

def load_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_results(results, output_dir="test_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"aila_test_results_{timestamp}.csv")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query", "Answer", "Source Articles", "Note"])
        for result in results:
            writer.writerow(result)
    print(f"✅ Test results saved to {output_file}")


def summarize_sources(sources):
    if not sources:
        return ""
    return "; ".join(doc.metadata.get("article", "Unknown") for doc in sources)


def run_batch_test(question_file):
    qa_chain = build_qa_chain()
    questions = load_questions(question_file)
    results = []

    for i, query in enumerate(questions, start=1):
        print(f"\n🔍 Query {i}: {query}")
        response = qa_chain(query)
        answer = response.get("result", "")
        sources = response.get("source_documents", [])
        source_info = summarize_sources(sources)
        #note = "OK" if answer and "no article found" not in answer.lower() else "CHECK"
        error_keywords = [
            "no article found",
            "no documents matched article",
            "please check the article number",
            "no relevant documents found"
        ]

        note = "OK"
        if not answer.strip():
            note = "MISSING"
        elif any(k in answer.lower() for k in error_keywords):
            note = "MISSING"
        elif not query.lower().split()[0] in answer.lower():
            note = "POSSIBLE MISMATCH"

        results.append([query, answer, source_info, note])

    write_results(results)


if __name__ == "__main__":
    question_path = "tests/test_queries.txt"
    run_batch_test(question_path)

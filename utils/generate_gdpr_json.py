import json
import os

OUTPUT_FILE = "../data/swiss_fadp_articles.json"

def generate_gdpr_json(num_articles=99):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    articles = []
    for i in range(1, num_articles + 1):
        article = {
            "article": f"Article {i}",
            "title": f"",
            "body": ""  # Leave this blank for manual paste
        }
        articles.append(article)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(articles)} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_gdpr_json()
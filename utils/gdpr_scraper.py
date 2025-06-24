import requests
from bs4 import BeautifulSoup
import json
import os

GDPR_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"
OUTPUT_FILE = "../data/gdpr_articles.json"

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_articles(html):
    soup = BeautifulSoup(html, "html.parser")

    # Look for each article header and text body
    article_elements = soup.find_all("div", class_="ti-art")

    articles = []
    for elem in article_elements:
        title_tag = elem.find("h3")
        body_tag = elem.find("div", class_="normal")

        if title_tag and body_tag:
            article_num = title_tag.get_text(strip=True)
            article_text = body_tag.get_text(separator="\n", strip=True)

            articles.append({
                "article": article_num,
                "text": article_text
            })

    return articles

def fetch_article(article_number):
    url = BASE_URL.format(article_number)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h1", class_="entry-title")
        content_div = None

        # Try multiple known class names
        for class_name in ["entry-content", "texte", "post-content"]:
            content_div = soup.find("div", class_=class_name)
            if content_div:
                print(f"✅ Found content using class: '{class_name}'")
                break

        if not title_tag or not content_div:
            print(f"⚠️ Skipped Article {article_number}: Content not found")
            return None

        title = title_tag.text.strip()
        content = content_div.get_text(separator="\n").strip()

        return {
            "article": f"Article {article_number}",
            "title": title,
            "text": content
        }

    except requests.RequestException as e:
        print(f"❌ Failed to fetch Article {article_number}: {e}")
        return None



def save_to_json(data, filepath):
    """Save extracted articles to a JSON file."""
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)


    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(data)} articles to {filepath}")

def run():
    print("🔍 Fetching GDPR content...")
    html = fetch_html(GDPR_URL)
    print("🧠 Extracting articles...")
    articles = extract_articles(html)
    print(f"💾 Saving {len(articles)} articles to {OUTPUT_FILE}")
    save_to_json(articles, OUTPUT_FILE)
    print("✅ Done.")

if __name__ == "__main__":
    run()
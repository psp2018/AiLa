import json

def generate_article_suggestions(gdpr_path="data/gdpr_articles.json", fadp_path="data/swiss_fadp_articles.json"):
    suggestions = []

    def load_titles(path, prefix):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for article in data:
                    article_num = article.get("article", "").strip()
                    title = article.get("title", "").strip()
                    if article_num:
                        suggestions.append(f"What does {article_num} of the {prefix} say?")
                        if title:
                            suggestions.append(f"Summarize '{title}' from the {prefix}")
        except Exception as e:
            print(f"⚠️ Error loading {path}: {e}")

    load_titles(gdpr_path, "GDPR")
    load_titles(fadp_path, "FADP")

    return sorted(set(suggestions))  # Remove duplicates

# Example usage:
# suggestions = generate_article_suggestions()
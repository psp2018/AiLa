import json
with open("data/gdpr_articles.json") as f:
    data = json.load(f)
    print([d["article"] for d in data if "99" in d["article"]])
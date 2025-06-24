import json
import os

FILE_PATH = "../data/gdpr_articles.json"

def add_missing_chapter_field(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return

    modified = False
    for article in data:
        if "chapter" not in article:
            article["chapter"] = ""
            modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Added missing 'chapter' fields to {filepath}")
    else:
        print(f"ℹ️ All articles already contain a 'chapter' field. No changes made.")

def patch_source_field(filepath, source_label):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return

    modified = False
    for article in data:
        if "source" not in article:
            article["source"] = source_label.upper()
            modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Added 'source: {source_label.upper()}' to missing entries in {filepath}")
    else:
        print(f"ℹ️ All entries already have a 'source' field. No changes made.")

if __name__ == "__main__":
    #add_missing_chapter_field(FILE_PATH)
    patch_source_field(FILE_PATH, "GDPR")
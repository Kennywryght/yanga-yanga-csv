# backend/utils/rules.py

import json
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
CATEGORY_KEYWORDS_PATH = os.path.join(ASSETS_DIR, 'category_keywords.json')

def load_category_keywords():
    """
    Load category keywords from JSON file.
    JSON format example:
    {
      "pawapay": "Betting",
      "topup": "Bundles",
      "water": "Water Bill",
      "escom": "Electricity (ESCOM)"
    }
    """
    try:
        with open(CATEGORY_KEYWORDS_PATH, 'r', encoding='utf-8') as f:
            category_map = json.load(f)
        return category_map
    except Exception as e:
        print(f"Error loading category keywords: {e}")
        return {}

def auto_categorize(detail, category_map):
    """
    Simple keyword matching:
    If any keyword is found in the transaction detail, return its category.
    If none found, return None (to be categorized manually).
    """
    detail_lower = detail.lower()
    for keyword, category in category_map.items():
        if keyword.lower() in detail_lower:
            return category
    return None

import json
import os
import pandas as pd

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
MEMORY_MAP_PATH = os.path.join(ASSETS_DIR, 'memory_map.json')

def load_memory():
    """Load memory map of previous user-labeled descriptions."""
    if os.path.exists(MEMORY_MAP_PATH):
        try:
            with open(MEMORY_MAP_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load memory: {e}")
    return {}

def apply_memory(df: pd.DataFrame, memory_map: dict) -> pd.DataFrame:
    """
    Apply learned memory map to DataFrame, 
    filling in category for known transaction details.
    """
    def match_memory(detail):
        return memory_map.get(detail.lower())

    df['Category'] = df.apply(
        lambda row: match_memory(row['Details']) if pd.isna(row['Category']) else row['Category'],
        axis=1
    )
    return df

def update_memory(df: pd.DataFrame, memory_map: dict):
    """
    Update the memory map with new user-defined or detected categories,
    then save it to disk.
    """
    updated = False
    for _, row in df.iterrows():
        detail = str(row['Details']).strip().lower()
        category = str(row['Category']).strip()
        if detail and category and detail not in memory_map:
            memory_map[detail] = category
            updated = True

    if updated:
        try:
            with open(MEMORY_MAP_PATH, 'w', encoding='utf-8') as f:
                json.dump(memory_map, f, indent=2)
            print("✅ Memory updated successfully.")
        except Exception as e:
            print(f"❌ Failed to save memory: {e}")

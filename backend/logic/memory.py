import json
import os

MEMORY_PATH = "ml/memory.json"

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def update_memory(memory, corrections):
    for desc, category in corrections.items():
        memory[desc.lower()] = category
    save_memory(memory)

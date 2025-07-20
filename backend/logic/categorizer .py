import os
import pickle
from logic.memory import load_memory

MODEL_PATH = "ml/model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"

# Load ML model and vectorizer
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

def predict_category(description: str) -> str:
    """Use ML model to predict the category of a description."""
    X = vectorizer.transform([description])
    return model.predict(X)[0]

def apply_memory(description: str, memory: dict) -> str:
    """Return category from memory if known."""
    return memory.get(description.lower(), None)

def auto_categorize(descriptions: list[str]) -> list[str]:
    """Try to apply memory or model for each description."""
    memory = load_memory()
    categories = []
    for desc in descriptions:
        cat = apply_memory(desc, memory)
        if cat is None:
            cat = predict_category(desc)
        categories.append(cat)
    return categories

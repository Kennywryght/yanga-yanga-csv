import joblib
import os
import pandas as pd

# Predefined manual tagging map
MEMORY_MAP = {
    "airtel": "Airtime",
    "tnm": "Airtime",
    "zodiak": "Media",
    "school": "Education",
    "bet": "Betting",
    "escom": "Electricity",
    "waterboard": "Water",
    "hospital": "Health",
    "clinic": "Health",
    "mpamba": "Mobile Money",
    "mo626": "Bank Transfer",
    "ulendo": "Transport",
    "fuel": "Transport",
    "shoprite": "Groceries",
    "chipiku": "Groceries",
    "restaurant": "Dining",
    "lunch": "Dining",
    "withdraw": "Cash Withdrawal",
    "agent": "Agent Withdrawal",
    "transfer": "Peer Transfer"
}

# ✅ Correct path to ml folder (assuming model_utils.py is in backend/utils/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # this goes from utils/ → backend/
ML_DIR = os.path.join(BASE_DIR, "ml")
MODEL_PATH = os.path.join(ML_DIR, "model.pkl")
VEC_PATH = os.path.join(ML_DIR, "vectorizer.pkl")

def get_model():
    """
    Load the trained ML model and vectorizer from disk.
    """
    try:
        print(f"[DEBUG] Loading model from: {MODEL_PATH}")
        print(f"[DEBUG] Loading vectorizer from: {VEC_PATH}")
        model = joblib.load(MODEL_PATH)
        vec = joblib.load(VEC_PATH)
        return model, vec
    except Exception as e:
        raise RuntimeError(f"Error loading model/vectorizer: {e}")

def predict_category(model, vec, text: str) -> str:
    """
    Predict the category of a transaction using the trained model.
    """
    try:
        X = vec.transform([text])
        return model.predict(X)[0]
    except Exception as e:
        print("⚠️ Prediction failed:", e)
        return "Uncategorized"

def apply_memory(df: pd.DataFrame, memory_map: dict = MEMORY_MAP) -> pd.DataFrame:
    """
    Apply hardcoded keyword mapping to transactions before ML.
    """
    for keyword, category in memory_map.items():
        df.loc[
            df["Details"].str.contains(keyword, case=False, na=False, regex=False),  # ✅ updated here
            "Category"
        ] = category
    return df

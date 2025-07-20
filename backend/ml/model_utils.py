import joblib
import os

# This file is in backend/ml/, so go one level up to get to backend/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VEC_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

print(f"[DEBUG] Loading model from: {MODEL_PATH}")
print(f"[DEBUG] Loading vectorizer from: {VEC_PATH}")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    if not os.path.exists(VEC_PATH):
        raise FileNotFoundError(f"Vectorizer file not found at {VEC_PATH}")

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VEC_PATH)
    return model, vectorizer

def predict_category(model, vectorizer, text):
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

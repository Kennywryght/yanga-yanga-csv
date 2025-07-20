import os
import uuid
import hashlib
from io import StringIO
from typing import Optional, Dict
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.db.db import get_db
from backend.db.models import Transaction
from backend.models.transaction_response import TransactionUploadResponse
from backend.utils.rules import auto_categorize, load_category_keywords
from backend.utils.memory import load_memory, apply_memory, update_memory
from backend.utils.categorizer import get_model, predict_category, MEMORY_MAP
from backend.utils.export_pdf import generate_pdf_report
from backend.ml.model_utils import load_model
from urllib.parse import quote

# ─── Load ML Model ─────────────────────────────────────────────────
model, vectorizer = load_model()
# uploads 
UPLOAD_DIR = "./uploads"
# ─── App Initialization ────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CATEGORY_MAP = load_category_keywords()
MEMORY_MAP = load_memory()

# ─── Root ───────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "📦 Yanga Yanga API running!"}


# ─── Get Recent Transactions ───────────────────────────────────────
@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    latest_file_id = (
        db.query(Transaction.file_id)
        .order_by(desc(Transaction.timestamp))
        .limit(1)
        .scalar()
    )
    if not latest_file_id:
        return []
    txns = db.query(Transaction).filter(Transaction.file_id == latest_file_id).all()
    return [
        {
            "id": t.id,
            "file_id": t.file_id,
            "details": t.details,
            "amount": t.amount,
            "category": t.category,
            "timestamp": t.timestamp.isoformat(),
            "needs_confirmation": t.needs_confirmation
        }
        for t in txns
    ]


# ─── Upload Transactions ───────────────────────────────────────────
@app.post("/transactions", response_model=TransactionUploadResponse)
async def upload_transactions(*, file: UploadFile = File(...), db: Session = Depends(get_db)) -> TransactionUploadResponse:
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")

        with open(file_path, "wb") as f:
            f.write(await file.read())

        df = pd.read_csv(file_path)

        if "Details" not in df.columns or "Amount (MWK)" not in df.columns:
            raise HTTPException(400, "CSV must have 'Details' and 'Amount (MWK)' columns.")

        df["Details"] = df["Details"].astype(str).str.strip()
        df["Amount (MWK)"] = (
            df["Amount (MWK)"].astype(str)
            .str.replace(",", "")
            .str.replace("K", "000")
        )
        df["Amount (MWK)"] = pd.to_numeric(df["Amount (MWK)"], errors='coerce')

        def parse_date(row):
            try:
                return datetime.strptime(f"{row['Date']} {row['Time']}", "%d/%m/%y %I:%M %p")
            except:
                return pd.NaT

        df["transaction_date"] = df.apply(parse_date, axis=1)
        df["Timestamp"] = df["transaction_date"]
        df = df.dropna(subset=["transaction_date", "Details", "Amount (MWK)"])

        df = apply_memory(df, MEMORY_MAP)

        df["Category"] = df.apply(
            lambda row: row["Category"]
            if pd.notna(row.get("Category")) and row["Category"] != ""
            else auto_categorize(str(row["Details"]), CATEGORY_MAP),
            axis=1
        )

        def final_categorize(row):
            cat = row["Category"]
            if pd.isna(cat) or cat == "" or cat == "Uncategorized":
                return predict_category(model, vectorizer, str(row["Details"]))
            return cat

        df["Category"] = df.apply(final_categorize, axis=1)

        ambiguous_keywords = ["withdraw", "agent", "transfer", "peer"]
        df["Needs_Confirmation"] = df["Details"].str.lower().apply(
            lambda detail: any(kw in detail for kw in ambiguous_keywords)
        )

        # ✅ Save categorized version of the file
        categorized_path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
        df.to_csv(categorized_path, index=False)

        added_count = 0
        for index, row in df.iterrows():
            existing = db.query(Transaction).filter(
                Transaction.details == row["Details"],
                Transaction.amount == row["Amount (MWK)"],
                Transaction.transaction_date == row["transaction_date"]
            ).first()

            if existing:
                continue

            txn = Transaction(
                file_id=file_id,
                details=row["Details"],
                amount=row["Amount (MWK)"],
                category=row["Category"],
                timestamp=row["Timestamp"],
                transaction_date=row["transaction_date"],
                needs_confirmation=row["Needs_Confirmation"]
            )
            db.add(txn)
            added_count += 1

        db.commit()

        return TransactionUploadResponse(
            message=f"Uploaded and stored {added_count} transactions (deduplicated).",
            file_id=file_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# ─── Uncategorized Rows ─────────────────────────────────────────────
@app.get("/uncategorized/{file_id}")
def get_uncategorized(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
    if not os.path.exists(path):
        raise HTTPException(404, "Categorized file not found.")
    df = pd.read_csv(path)
    unc = df[df["Category"].isnull()][["Details", "Amount (MWK)"]]
    return JSONResponse(content=unc.to_dict(orient="records"))


# ─── Manual Category Update ─────────────────────────────────────────
@app.post("/categorize/{file_id}")
def update_categories(file_id: str, corrections: Dict[str, str] = Body(...)):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
    if not os.path.exists(path):
        raise HTTPException(404, "File not found.")
    df = pd.read_csv(path)
    for i, row in df.iterrows():
        if row["Details"] in corrections:
            df.at[i, "Category"] = corrections[row["Details"]]
    update_memory(df, MEMORY_MAP)
    df.to_csv(path, index=False)
    return {"message": "Manual categories applied and memory updated."}


# ─── Summary ────────────────────────────────────────────────────────
@app.get("/summary/{file_id}")
def get_summary(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found at {path}")
    return {"message": f"File found: {path}"}


# ─── Dashboard ──────────────────────────────────────────────────────
@app.get("/dashboard/{file_id}")
def get_dashboard(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
    if not os.path.exists(path):
        raise HTTPException(404, "File not found.")

    df = pd.read_csv(path)

    # Ensure Amount column is numeric
    df['Amount (MWK)'] = (
        df['Amount (MWK)']
        .astype(str)
        .str.replace(",", "")
        .str.replace("K", "000")
    )
    df['Amount (MWK)'] = pd.to_numeric(df['Amount (MWK)'], errors='coerce')
    df.dropna(subset=['Amount (MWK)'], inplace=True)

    df['Category'] = df['Category'].fillna("Uncategorized")

    # Compute total income (positive values) and total spent (negative values, made positive)
    df['is_income'] = df['Amount (MWK)'] > 0
    total_income = df[df['is_income']]['Amount (MWK)'].sum()
    total_spent = df[~df['is_income']]['Amount (MWK)'].abs().sum()

    # Group category breakdown by spending only
    spending_df = df[~df['is_income']].copy()
    spending_df['Amount (MWK)'] = spending_df['Amount (MWK)'].abs()

    breakdown = spending_df.groupby('Category')['Amount (MWK)'].sum().reset_index()
    breakdown['Percentage'] = round((breakdown['Amount (MWK)'] / total_spent) * 100, 2)

    # Optional: Get monthly trend data
    df['Month'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.to_period('M').astype(str)
    monthly_trend = (
        df.groupby(['Month'])
        .agg({
            'Amount (MWK)': 'sum'
        })
        .reset_index()
        .rename(columns={'Amount (MWK)': 'Net Amount'})
    )

    return JSONResponse(content={
        "total_income": round(float(total_income), 2),
        "total_spent": round(float(total_spent), 2),
        "category_breakdown": breakdown.to_dict(orient="records"),
        "monthly_trends": monthly_trend.to_dict(orient="records")
    })

# ─── Export PDF ─────────────────────────────────────────────────────
@app.get("/export/pdf/{file_id}")
def export_pdf(file_id: str):
    path = os.path.join(UPLOAD_DIR, f"{file_id}_categorized.csv")
    if not os.path.exists(path):
        raise HTTPException(404, "File not found.")
    df = pd.read_csv(path)
    df["Category"] = df["Category"].fillna("Uncategorized")
    total_income = df[df["Amount (MWK)"] > 0]["Amount (MWK)"].sum()
    spent = df[df["Amount (MWK)"] < 0].copy()
    spent["Amount (MWK)"] = spent["Amount (MWK)"].abs()
    total_spent = spent["Amount (MWK)"].sum()
    summary = spent.groupby("Category")["Amount (MWK)"].sum().reset_index()
    summary["Percentage"] = (summary["Amount (MWK)"] / total_spent * 100).round(2)
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}_report.pdf")
    generate_pdf_report(summary.to_dict(orient="records"), total_income, total_spent, pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"YangaYanga_Report_{file_id}.pdf")


# ─── WhatsApp Share ─────────────────────────────────────────────────
@app.get("/share/whatsapp/{file_id}")
def whatsapp_share(file_id: str):
    base = "http://127.0.0.1:8000/export/pdf"
    url = f"{base}/{file_id}"
    msg = quote(f"Check out my spending report: {url}")
    return RedirectResponse(f"https://wa.me/?text={msg}")

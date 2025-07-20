from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.db import SessionLocal
from backend.db.models import Transaction


def delete_duplicate_transactions():
    db: Session = SessionLocal()

    try:
        print("🔍 Scanning for duplicates...")

        # Group by details + amount + timestamp, count how many
        duplicates = (
            db.query(
                Transaction.details,
                Transaction.amount,
                Transaction.timestamp,
                func.count(Transaction.id).label("count")
            )
            .group_by(Transaction.details, Transaction.amount, Transaction.timestamp)
            .having(func.count(Transaction.id) > 1)
            .all()
        )

        total_deleted = 0

        for dup in duplicates:
            # Fetch all duplicates for the group
            txns = (
                db.query(Transaction)
                .filter(
                    Transaction.details == dup.details,
                    Transaction.amount == dup.amount,
                    Transaction.timestamp == dup.timestamp
                )
                .order_by(Transaction.id)
                .all()
            )

            # Keep the first, delete the rest
            for txn in txns[1:]:
                db.delete(txn)
                total_deleted += 1

        db.commit()
        print(f"✅ Done. {total_deleted} duplicate transactions deleted.")
    
    except Exception as e:
        print("❌ Error during deduplication:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    delete_duplicate_transactions()

# create_tables.py

from db.db import engine, Base
from models.transaction import Transaction

# Create all tables registered with Base
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")

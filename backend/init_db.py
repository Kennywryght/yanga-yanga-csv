from db import engine, Base
import models.transaction  # Import models to register them with Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized!")

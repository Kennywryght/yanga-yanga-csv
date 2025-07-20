# backend/schemas.py
from pydantic import BaseModel

class TransactionUploadResponse(BaseModel):
    message: str
    file_id: str

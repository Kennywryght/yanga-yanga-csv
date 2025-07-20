import os

# Folder to store uploaded and categorized CSVs
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Create folder if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

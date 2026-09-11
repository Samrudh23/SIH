import os
import shutil
import pytesseract

from fastapi import FastAPI, UploadFile, File

# Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "OCR API is running"
    }


@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):

    # Create uploads folder
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded image
    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text using Tesseract
    extracted_text = pytesseract.image_to_string(file_path)

    return {
        "filename": file.filename,
        "text": extracted_text
    }
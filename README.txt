# OCR Backend for Packaged Commodities Compliance System

This module provides OCR functionality for extracting text from images of packaged commodities.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Tesseract OCR
- pytesseract
- Pillow

## Features

- Upload product/package images
- Extract text from product labels
- Return extracted text through an API
- Supports further processing for compliance checking

## Project Structure

ocr_backend/
│
├── main.py
├── requirements.txt
├── README.md
│
└── uploads/

## Installation

Install the Python dependencies:

python -m pip install -r requirements.txt

## Tesseract Installation

Tesseract OCR must be installed separately.

Default Windows installation path:

C:\Program Files\Tesseract-OCR\tesseract.exe

## Running the API

Run:

python -m uvicorn main:app --host 127.0.0.1 --port 8000

The API will run at:

http://127.0.0.1:8000

## API Endpoints

### GET /

Checks whether the OCR API is running.

Response:

{
  "message": "OCR API is running"
}

### POST /ocr

Uploads an image and extracts text using Tesseract OCR.

Response:

{
  "filename": "product.jpg",
  "text": "Extracted text from the product label"
}
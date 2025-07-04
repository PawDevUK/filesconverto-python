from flask import Flask, request
from flask_cors import CORS
from pdf2docx import Converter
from pdf2image import convert_from_path
import pytesseract
from docx import Document
import tempfile
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Configure tesseract cmd path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route("/", methods=["GET"])
def index():
    return "PDF to DOCX Converter is running. Use POST /convert to convert files."

@app.route("/convert", methods=["POST"])
def convert_pdf():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return {"error": "Invalid file type, PDF required"}, 400

    def fileExtension(filename):
        return tempfile.NamedTemporaryFile(suffix="."+filename , delete=False)
    
    temp_pdf = fileExtension("pdf")
    temp_docx = fileExtension("docx")
    temp_pdf.close()
    temp_docx.close()

    print("Saving uploaded file...")
    file.save(temp_pdf.name)
    print("Saved PDF to", temp_pdf.name)

    try:
        print("Starting pdf2docx conversion...")
        cv = Converter(temp_pdf.name)
        cv.convert(temp_docx.name)
        cv.close()
        print("pdf2docx conversion done.")
        with open(temp_docx.name, "rb") as f:
            if len(f.read()) < 100:
                print("DOCX is empty, raising for OCR fallback.")
                raise Exception("Empty DOCX, trying OCR")
    except Exception as e:
        print("Falling back to OCR...", e)
        # OCR fallback for scanned PDFs
        images = convert_from_path(temp_pdf.name)
        doc = Document()
        for image in images:
            text = pytesseract.image_to_string(image)
            print("OCR text:", text)
            doc.add_paragraph(text)
        doc.save(temp_docx.name)
        print("OCR DOCX saved.")

    with open(temp_docx.name, "rb") as f:
        docx_content = f.read()

    # Now it's safe to delete
    os.unlink(temp_pdf.name)
    os.unlink(temp_docx.name)

    return app.response_class(
        response=docx_content,
        status=200,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.pdf', '.docx')}"}
    )

if __name__ == "__main__":
    app.run(debug=True)

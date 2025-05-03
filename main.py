from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    # Extract text from PDF
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Create UI DOCX
    ui_doc = Document()
    ui_doc.add_heading("UI Troubleshooting", level=1)
    ui_doc.add_paragraph(text)
    ui_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
    ui_doc.save(ui_doc_path)

    # Create Full DOCX
    full_doc = Document()
    full_doc.add_heading("UI Troubleshooting", level=1)
    full_doc.add_paragraph(text)
    full_doc.add_heading("Backend Troubleshooting", level=1)
    full_doc.add_paragraph("This document was auto-generated based on the uploaded ticket.")
    full_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
    full_doc.save(full_doc_path)

    # Upload to your server or return static links if hosted
    return jsonify({
        "ui_doc_link": f"https://docgen-flask.onrender.com/download/{os.path.basename(ui_doc_path)}",
        "full_doc_link": f"https://docgen-flask.onrender.com/download/{os.path.basename(full_doc_path)}"
    })

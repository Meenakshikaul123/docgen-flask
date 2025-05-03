from flask import Flask, request, jsonify, send_file
from docx import Document
from PyPDF2 import PdfReader
import tempfile
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        # Save uploaded PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file.save(temp_pdf.name)

        # Extract text
        reader = PdfReader(temp_pdf.name)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Create UI-only document
        ui_doc = Document()
        ui_doc.add_heading("UI Checklist", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.add_paragraph("This document was auto-generated based on the uploaded ticket.")

        # Create UI + Backend document
        full_doc = Document()
        full_doc.add_heading("UI + Backend Troubleshooting", level=1)
        full_doc.add_paragraph(text)
        full_doc.add_paragraph("This document was auto-generated based on the uploaded ticket.")

        # Save both files
        ui_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        full_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        ui_doc.save(ui_path.name)
        full_doc.save(full_path.name)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_path.name)}",
            "full_doc_link": f"/download?file={os.path.basename(full_path.name)}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("file")
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

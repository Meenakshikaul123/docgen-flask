from flask import Flask, request, jsonify, send_from_directory
from docx import Document
from PyPDF2 import PdfReader
import os
import uuid

app = Flask(__name__)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded."}), 400

        # Read PDF
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Generate unique filenames
        ui_name = f"{uuid.uuid4()}_ui.docx"
        full_name = f"{uuid.uuid4()}_full.docx"

        # UI Doc
        ui_doc = Document()
        ui_doc.add_heading("UI Summary", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.save(os.path.join(STATIC_DIR, ui_name))

        # Full Doc
        full_doc = Document()
        full_doc.add_heading("UI + Backend Troubleshooting", level=1)
        full_doc.add_paragraph(text)
        full_doc.save(os.path.join(STATIC_DIR, full_name))

        base_url = request.url_root.rstrip('/')
        return jsonify({
            "ui_doc_link": f"{base_url}/static/{ui_name}",
            "full_doc_link": f"{base_url}/static/{full_name}"
        })

    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route("/static/<filename>")
def serve_file(filename):
    return send_from_directory(STATIC_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

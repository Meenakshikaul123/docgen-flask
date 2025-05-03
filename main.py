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
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        # Read PDF content
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Generate filenames
        ui_filename = f"{uuid.uuid4()}_ui.docx"
        full_filename = f"{uuid.uuid4()}_full.docx"

        # Create UI doc
        ui_doc = Document()
        ui_doc.add_heading("UI Checklist", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.add_paragraph("Auto-generated UI checklist based on the uploaded ticket.")
        ui_doc_path = os.path.join(STATIC_DIR, ui_filename)
        ui_doc.save(ui_doc_path)

        # Create full doc
        full_doc = Document()
        full_doc.add_heading("UI + Backend Report", level=1)
        full_doc.add_paragraph(text)
        full_doc.add_paragraph("Auto-generated full troubleshooting document.")
        full_doc_path = os.path.join(STATIC_DIR, full_filename)
        full_doc.save(full_doc_path)

        base_url = request.url_root.rstrip("/")
        return jsonify({
            "ui_doc_link": f"{base_url}/static/{ui_filename}",
            "full_doc_link": f"{base_url}/static/{full_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: Just a backup endpoint if needed
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(STATIC_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

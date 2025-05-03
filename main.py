from flask import Flask, request, jsonify, send_file
from docx import Document
import pdfplumber
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

        # Save PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file.save(temp_pdf.name)

        # Use pdfplumber to extract text
        text = ""
        with pdfplumber.open(temp_pdf.name) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            return jsonify({"error": "Unable to extract text from PDF."}), 400

        # UI document
        ui_doc = Document()
        ui_doc.add_heading("UI-Friendly Version", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.add_paragraph("Auto-generated document based on uploaded ticket.")

        # Full document
        full_doc = Document()
        full_doc.add_heading("Full Ticket Summary", level=1)
        full_doc.add_paragraph(text)
        full_doc.add_paragraph("Auto-generated document based on uploaded ticket.")

        ui_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        full_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        ui_doc.save(ui_path)
        full_doc.save(full_path)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_path)}",
            "full_doc_link": f"/download?file={os.path.basename(full_path)}"
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("file")
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify, send_file
from docx import Document
import pdfplumber
import tempfile
import base64
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        data = request.get_json()
        if "file_data" not in data:
            return jsonify({"error": "No file_data found"}), 400

        # Decode base64 PDF
        pdf_bytes = base64.b64decode(data["file_data"], validate=True)
        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Extract text using pdfplumber
        text = ""
        with pdfplumber.open(temp_pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            return jsonify({"error": "No extractable text found in PDF."}), 400

        # Save UI doc
        ui_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        ui_doc = Document()
        ui_doc.add_heading("UI Document", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.save(ui_path)

        # Save Full doc
        full_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        full_doc = Document()
        full_doc.add_heading("UI + Backend Troubleshooting", level=1)
        full_doc.add_paragraph(text)
        full_doc.save(full_path)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_path)}",
            "full_doc_link": f"/download?file={os.path.basename(full_path)}"
        })

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("file")
    path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

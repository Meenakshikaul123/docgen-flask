from flask import Flask, request, jsonify, send_file
from docx import Document
import tempfile
import os
import base64
import pdfplumber

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        data = request.get_json()

        if not data or "file_data" not in data:
            return jsonify({"error": "Missing base64-encoded file data."}), 400

        try:
            # Decode the base64 string
            pdf_bytes = base64.b64decode(data["file_data"], validate=True)
        except Exception as e:
            return jsonify({"error": f"Invalid base64 input: {str(e)}"}), 400

        # Save PDF to temp file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(temp_pdf.name, "wb") as f:
            f.write(pdf_bytes)

        # Extract text using pdfplumber
        extracted_text = ""
        with pdfplumber.open(temp_pdf.name) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

        if not extracted_text.strip():
            return jsonify({"error": "Unable to extract any text from the PDF."}), 400

        # Create UI-only DOCX
        ui_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        ui_doc = Document()
        ui_doc.add_heading("UI Document", level=1)
        ui_doc.add_paragraph(extracted_text)
        ui_doc.save(ui_doc_path)

        # Create Full DOCX
        full_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        full_doc = Document()
        full_doc.add_heading("UI + Backend Troubleshooting", level=1)
        full_doc.add_paragraph(extracted_text)
        full_doc.save(full_doc_path)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_doc_path)}",
            "full_doc_link": f"/download?file={os.path.basename(full_doc_path)}"
        })

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("file")
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

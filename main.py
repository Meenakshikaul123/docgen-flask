from flask import Flask, request, jsonify, send_file
from docx import Document
import tempfile
import os
import base64
from PyPDF2 import PdfReader

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
            pdf_bytes = base64.b64decode(data["file_data"], validate=True)
        except Exception as e:
            return jsonify({"error": f"Base64 decode failed: {str(e)}"}), 400

        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Extract text from PDF
        try:
            reader = PdfReader(temp_pdf_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return jsonify({"error": f"Failed to extract text from PDF: {str(e)}"}), 500

        # Generate UI DOC
        ui_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        ui_doc = Document()
        ui_doc.add_heading("UI-Friendly Version", level=1)
        ui_doc.add_paragraph(text)
        ui_doc.save(ui_doc_path)

        # Generate Full DOC
        full_doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        full_doc = Document()
        full_doc.add_heading("Full Report Version", level=1)
        full_doc.add_paragraph(text)
        full_doc.save(full_doc_path)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_doc_path)}",
            "full_doc_link": f"/download?file={os.path.basename(full_doc_path)}"
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def download_file():
    filename = request.args.get("file")
    path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

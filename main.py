from flask import Flask, request, jsonify, send_file
from docx import Document
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
            return jsonify({"error": "No file data provided."}), 400

        # Decode base64 string to binary
        file_content = base64.b64decode(data["file_data"])

        # Save PDF temporarily
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_pdf.write(file_content)
        temp_pdf.close()

        # Create documents (just sample content for now)
        ui_doc = Document()
        ui_doc.add_heading("UI Document", level=1)
        ui_doc.add_paragraph("Auto-generated content from the uploaded PDF.")

        full_doc = Document()
        full_doc.add_heading("Full UI + Backend Document", level=1)
        full_doc.add_paragraph("Full content based on PDF input.")

        # Save files
        ui_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        full_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
        ui_doc.save(ui_path)
        full_doc.save(full_path)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_path)}",
            "full_doc_link": f"/download?file={os.path.basename(full_path)}"
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

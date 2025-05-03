from flask import Flask, request, jsonify, send_file
from docx import Document
import tempfile
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        data = request.get_json()
        if not data or "ticket_text" not in data:
            return jsonify({"error": "Missing ticket_text in request."}), 400

        ticket_text = data["ticket_text"]

        # Create UI Document
        ui_doc = Document()
        ui_doc.add_heading("UI Checklist", level=1)
        ui_doc.add_paragraph(ticket_text)
        ui_doc.add_paragraph("This document was auto-generated based on the uploaded ticket.")

        # Create Full Document
        full_doc = Document()
        full_doc.add_heading("UI + Backend Troubleshooting", level=1)
        full_doc.add_paragraph(ticket_text)
        full_doc.add_paragraph("This document was auto-generated based on the uploaded ticket.")

        # Save both documents
        ui_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        full_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        ui_doc.save(ui_file.name)
        full_doc.save(full_file.name)

        return jsonify({
            "ui_doc_link": f"/download?file={os.path.basename(ui_file.name)}",
            "full_doc_link": f"/download?file={os.path.basename(full_file.name)}"
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

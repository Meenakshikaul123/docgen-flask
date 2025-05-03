from flask import Flask, request, jsonify, send_from_directory
from docx import Document
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DOC_FOLDER = "generated_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOC_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return "Doc Generator API is live."

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Simplified issue detection
    issue_type = "generic"
    if "whatsapp" in text.lower():
        issue_type = "whatsapp"
    elif "apn" in text.lower() or "push" in text.lower():
        issue_type = "push"
    elif "journey" in text.lower():
        issue_type = "journey"
    elif "email" in text.lower():
        issue_type = "email"

    # Use dummy checklist items (can be made smarter later)
    def generate_doc(title, sections, file_suffix):
        doc = Document()
        doc.add_heading(title, level=1)
        doc.add_paragraph("This document was auto-generated based on the uploaded ticket.
")
        for sec in sections:
            doc.add_paragraph(f"{sec['title']}:", style='List Number')
            for bullet in sec['bullets']:
                doc.add_paragraph(bullet, style='List Bullet')
        out_name = f"{uuid.uuid4().hex}_{file_suffix}.docx"
        out_path = os.path.join(DOC_FOLDER, out_name)
        doc.save(out_path)
        return out_name

    # Example content templates
    ui_sections = [{"title": "Basic UI Checks", "bullets": ["Verify user-facing filters", "Ensure UI element is active"]}]
    backend_sections = [{"title": "Backend Log Checks", "bullets": ["Check logs", "Validate API response"]}]

    if issue_type == "whatsapp":
        ui_sections = [{"title": "Template Checks", "bullets": ["Verify WhatsApp template status", "Check placeholder values"]}]
        backend_sections = [{"title": "API Logs", "bullets": ["Inspect WhatsApp API errors", "Check token status"]}]
    elif issue_type == "push":
        ui_sections = [{"title": "Campaign Status", "bullets": ["Ensure campaign is not expired", "Confirm cutoff settings"]}]
        backend_sections = [{"title": "Push Logs", "bullets": ["Check APNs logs", "Validate device tokens"]}]
    elif issue_type == "email":
        ui_sections = [{"title": "Audience Settings", "bullets": ["Check segment count", "Review campaign schedule"]}]
        backend_sections = [{"title": "Delivery Logs", "bullets": ["Check SMTP logs", "Validate from/reply-to headers"]}]
    elif issue_type == "journey":
        ui_sections = [{"title": "Journey Conditions", "bullets": ["Ensure conditions are met", "Validate wait blocks"]}]
        backend_sections = [{"title": "Execution Trace", "bullets": ["Review journey execution logs", "Validate trigger points"]}]

    ui_filename = generate_doc("Smartech UI Checklist", ui_sections, "ui")
    backend_filename = generate_doc("Smartech Backend Troubleshooting Guide", backend_sections, "backend")

    return jsonify({
        "ui_doc_url": f"/download/{ui_filename}",
        "backend_doc_url": f"/download/{backend_filename}"
    })

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(DOC_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

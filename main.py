from flask import Flask, request, send_from_directory, jsonify
from docx import Document
import tempfile
import os

app = Flask(__name__)

OUTPUT_DIR = "generated_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        data = request.json
        ui_info = data.get("ui", "No UI info provided.")
        backend_info = data.get("backend", "No backend info provided.")

        doc = Document()
        doc.add_heading('UI Document', level=1)
        doc.add_paragraph(ui_info)
        doc.add_heading('Backend Document', level=1)
        doc.add_paragraph(backend_info)

        filename = "generated_doc.docx"
        filepath = os.path.join(OUTPUT_DIR, filename)
        doc.save(filepath)

        # Return URL string
        return jsonify({"url": f"https://docgen-flask.onrender.com/download/{filename}"})

    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

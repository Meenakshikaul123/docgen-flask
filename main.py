from flask import Flask, request, send_file
from docx import Document
import tempfile

app = Flask(__name__)

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

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(temp.name)
        return send_file(
            temp.name,
            as_attachment=True,
            download_name="generated_doc.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

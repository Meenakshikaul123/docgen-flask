from flask import Flask, request, send_file
from docx import Document
from io import BytesIO

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Server is live", 200

@app.route("/generate-docx", methods=["POST"])
def generate_docx():
    try:
        data = request.json
        print("GPT SENT:", data)

        ui_info = data.get("ui", "No UI info provided.")
        backend_info = data.get("backend", "No backend info provided.")

        doc = Document()
        doc.add_heading('UI Document', level=1)
        doc.add_paragraph(ui_info)
        doc.add_heading('Backend Document', level=1)
        doc.add_paragraph(backend_info)

        # Create an in-memory file
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        return send_file(
            file_stream,
            as_attachment=True,
            download_name="generated_doc.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}, 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

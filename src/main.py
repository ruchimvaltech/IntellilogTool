import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyzer import analyze_logs_with_llama

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def form_ui():
    return """
<html>
    <head>
        <title>Intellilog Log Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; background: #f3f4f6; }
            h2 { color: #2563eb; }
            form { background: white; padding: 20px; border-radius: 8px; }
            input[type=file] { margin-bottom: 10px; }
            input[type=submit] { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            input[type=submit]:hover { background: #1d4ed8; }
        </style>
    </head>
    <body>
        <h2>Intellilog - Upload Log File</h2>
        <form action="/analyze" enctype="multipart/form-data" method="post">
            <input name="file" type="file" required>
            <br>
            <input type="submit" value="Upload and Analyze">
        </form>
    </body>
</html>
    """

@app.post("/analyze")
async def analyze_log(file: UploadFile):
    contents = await file.read()
    log_text = contents.decode()

    try:
        summary = analyze_logs_with_llama(log_text)
    except Exception as e:
        return HTMLResponse(content=f"<h3>Error: {e}</h3>", status_code=500)

    summary_path = "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    return FileResponse(summary_path, filename="summary.txt")
import sys
import os

# Add the current directory (where this file is) to the Python path.
# This helps ensure other files like `analyzer.py` can be imported correctly.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the core analysis function from analyzer.py
from analyzer import analyze_logs_with_llama

# FastAPI for web server, UploadFile to handle file uploads
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

# Create a FastAPI app instance
app = FastAPI()

# Route for home page (GET request) that returns a file upload form
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
        <!-- HTML form to upload a log file -->
        <form action="/analyze" enctype="multipart/form-data" method="post">
            <input name="file" type="file" required>
            <br>
            <input type="submit" value="Upload and Analyze">
        </form>
    </body>
</html>
    """

# Route to handle file upload and analysis (POST request)
@app.post("/analyze")
async def analyze_log(file: UploadFile):
    # Read file content
    contents = await file.read()

    # Convert bytes to string
    log_text = contents.decode()

    try:
        # Analyze the log content using your LLaMA-based analyzer
        summary = analyze_logs_with_llama(log_text)
    except Exception as e:
        # If error occurs during analysis, return error message on browser
        return HTMLResponse(content=f"<h3>Error: {e}</h3>", status_code=500)

    # Save the generated summary to a text file
    summary_path = "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    # Return the file as a download
    return FileResponse(summary_path, filename="summary.txt")

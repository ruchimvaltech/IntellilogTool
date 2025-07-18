import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from analyzer import analyze_logs_with_llama

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "summary": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_log(request: Request, file: UploadFile):
    log_data = await file.read()
    summary = analyze_logs_with_llama(log_data.decode())

    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

        # Extract issues and suggestions from structured summary
    lines = summary.splitlines()
    issues, suggestions = [], []
    in_root, in_remedy = False, False

    for line in lines:
        line = line.strip()
        if "root cause" in line.lower():
            in_root, in_remedy = True, False
            continue
        if "remedial action" in line.lower():
            in_remedy, in_root = True, False
            continue

        if line.startswith("*"):
            if in_root:
                issues.append(line.strip("* ").strip())
            elif in_remedy:
                suggestions.append(line.strip("* ").strip())



    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "summary": summary,
        "issues": issues,
        "suggestions": suggestions
    })

@app.get("/download-summary", response_class=FileResponse)
async def download_summary():
    return FileResponse("summary.txt", filename="summary.txt")

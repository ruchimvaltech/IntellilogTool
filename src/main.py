import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from gpt4connection import call_gpt_summary
# Import the logfile function from fetchlatestlogfile.py
from fetchlatestlogfile import fetch_latest_log
from fetchlatestlogfile import parse_log

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "summary": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_log(request: Request, file: UploadFile):
    log_data = await file.read()
    summary = call_gpt_summary(log_data.decode())

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

# Route to handle latest log file analysis (POST request)

log_file = fetch_latest_log()
raw_log = parse_log(log_file)
@app.post("/analyzelatest")
async def analyzelatest_log():
    # Read file content
    #contents = await raw_log.read()

    # Convert bytes to string
    #log_text = raw_log.decode()
    try:
        # Analyze the log content using your LLaMA-based analyzer
       summary = call_gpt_summary(raw_log)
    except Exception as e:
        # If error occurs during analysis, return error message on browser
        return HTMLResponse(content=f"<h3>Error: {e}</h3>", status_code=500)

    # Save the generated summary to a text file
    summary_path = "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
     f.write(summary)

    # Return the file as a download
     return FileResponse(summary_path, filename="summary.txt")
@app.get("/download-summary", response_class=FileResponse)
async def download_summary():
    return FileResponse("summary.txt", filename="summary.txt")

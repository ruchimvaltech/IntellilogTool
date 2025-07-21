import os
import shutil
import json
from llama_cpp import Llama

# Load parameter config
with open("./src/parameter.json", "r") as f:
    params = json.load(f)

model_path = params["model_path"]
temp_dir = params["temp_dir"]
backup_dir = params["backup_dir"]
chunk_size = params["chunk_size"]

# ------------------------
# Initialize the LLaMA model
# ------------------------
llm = Llama(model_path=model_path)

def filter_out_info(lines):
    """Remove lines with INFO keyword to reduce irrelevant tokens."""
    return [line for line in lines if "INFO" not in line]

def split_lines_into_chunks(lines, chunk_size=params["chunk_size"]):
    """Break long logs into smaller manageable parts."""
    for i in range(0, len(lines), chunk_size):
        yield lines[i:i + chunk_size]

def clean_temp_folder(temp_dir, backup_dir):
    """Move oldest files from temp folder to backup folder."""
    os.makedirs(backup_dir, exist_ok=True)

    files = sorted(
        [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
         if os.path.isfile(os.path.join(temp_dir, f))],
        key=lambda x: os.path.getmtime(x)
    )

    old_files = files[:5]  # Move 5 oldest files
    for f in old_files:
        print(f"Moving {f} to backup folder")
        shutil.move(f, os.path.join(backup_dir, os.path.basename(f)))
    

def format_structured_summary(app_name, root_causes, remedies):
    return f"""The application or service '{app_name}' is experiencing issues due to a combination of {', '.join(root_causes)}.
Root Cause:
{''.join([f"* {r}\n" for r in root_causes])}
Remedial Actions:
{''.join([f"* {r}\n" for r in remedies])}
By addressing these issues, the application or service '{app_name}' can run smoothly and efficiently, providing a better user experience."""

def analyze_logs_with_llama(log_content: str) -> str:
    print("Starting analysis...")
    lines = log_content.strip().splitlines()
    filtered = filter_out_info(lines)
    chunks = list(split_lines_into_chunks(filtered))
    partial_summaries = []

    for idx, chunk in enumerate(chunks):
        chunk_text = "\n".join(chunk)
        prompt = f"""
You are an AI log analyzer. Examine this log snippet:

{chunk_text}

Identify:
1. Application/service name.
2. Exceptions or issues (e.g., null check, memory usage, disk space).
3. Root causes.
4. Fix recommendations.
Format the response in a bullet format.
"""
        result = llm(prompt, max_tokens=params["max_tokens"], stop=["</s>"])
        partial_summaries.append(result["choices"][0]["text"].strip())

    combined_prompt = f"""
You're an expert log summarizer. Combine the following partial summaries into one summary.

{''.join(partial_summaries)}

Use this format:
The application or service 'AppName' is experiencing issues due to a combination of...
Root Cause:
* ...
* ...
Remedial Actions:
* ...
* ...
"""
    output = llm(combined_prompt, max_tokens=params["final_tokens"], stop=["</s>"])
    final_summary = output["choices"][0]["text"].strip()

   
    # Trigger cleanup if certain issues detected
    if "high memory usage" in final_summary.lower() or "low disk space" in final_summary.lower():
        clean_temp_folder(temp_dir, backup_dir)
        print("Temp files cleaned and moved after detecting high memory usage or low disk space.")

    return final_summary

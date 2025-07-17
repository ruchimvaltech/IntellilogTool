import os
import shutil
import json
from llama_cpp import Llama

# ------------------------
# Load configuration parameters from JSON file
# ------------------------
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
    """
    Remove lines containing 'INFO' keyword.
    This helps to focus only on warnings, errors, and critical issues.
    """
    return [line for line in lines if "INFO" not in line]

def split_lines_into_chunks(lines, chunk_size=50):
    """
    Split the list of lines into smaller chunks.
    Each chunk is analyzed separately to avoid context window limitations.
    """
    for i in range(0, len(lines), chunk_size):
        yield lines[i:i + chunk_size]

def clean_temp_folder(temp_dir, backup_dir):
    """
    Move the most recent files from temp_dir to backup_dir.
    This is triggered automatically when certain issues are detected.
    """
    os.makedirs(backup_dir, exist_ok=True)

    files = sorted(
        [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )

    recent_files = files[:5]  # Example: move 5 most recent files

    for f in recent_files:
        print(f"Moving {f} to {backup_dir}")
        shutil.move(f, os.path.join(backup_dir, os.path.basename(f)))

def analyze_logs_with_llama(log_content: str) -> str:
    """
    Main function to analyze log content using LLaMA.
    Steps:
    1. Filter out INFO lines.
    2. Split logs into smaller chunks.
    3. Summarize each chunk separately.
    4. Merge partial summaries into a final detailed summary.
    5. Check for 'high memory usage' or 'low disk space' and trigger cleanup if found.
    """
    print("Model initialized!")

    # Preprocessing
    lines = log_content.strip().splitlines()
    filtered_lines = filter_out_info(lines)

    # Split into chunks
    line_chunks = list(split_lines_into_chunks(filtered_lines, chunk_size=chunk_size))
    print(f"Total chunks: {len(line_chunks)}")

    partial_summaries = []

    for idx, chunk_lines in enumerate(line_chunks):
        chunk_text = "\n".join(chunk_lines)
        print(f"Summarizing chunk {idx + 1}/{len(line_chunks)}...")

        prompt = (
            f"""
            Analyze the following logs to determine the main application or service experiencing the issue:
            {chunk_text}
            Please provide:
            1. Main application or service name
            2. Exceptions occurred
            3. Root cause for the failure
            4. Remedial Actions
            """
        )

        output = llm(prompt, max_tokens=300, stop=["</s>"])
        result_text = output["choices"][0]["text"].strip()
        partial_summaries.append(result_text)

    # Combine partial summaries into final summary
    final_prompt = (
        "You are an expert log analysis AI. "
        "Combine the following partial summaries into one clear overall summary with root causes and fixes. "
        "Explain any missing null checks, high memory usage issues, low disk space issues, or code-level improvements clearly.\n\n"
        + "\n\n".join(partial_summaries)
        + "\n\nFinal Summary:"
    )

    output = llm(final_prompt, max_tokens=400, stop=["</s>"])
    final_summary = output["choices"][0]["text"].strip()

    # Trigger cleanup if certain issues detected
    if "high memory usage" in final_summary.lower() or "low disk space" in final_summary.lower():
        clean_temp_folder(temp_dir, backup_dir)
        print("Temp files cleaned and moved after detecting high memory usage or low disk space.")

    return final_summary

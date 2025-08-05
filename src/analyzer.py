import os
import shutil
import json
import re

# ---------------------------------------------
# Load parameter configuration from JSON file
# ---------------------------------------------
with open("./parameter.json", "r") as f:
    params = json.load(f)

model_path = params["model_path"]
temp_dir = params["temp_dir"]
backup_dir = params["backup_dir"]
chunk_size = params["chunk_size"]

# -----------------------------------------------------
# Step 1: Preprocessing - Filter out unnecessary logs
# -----------------------------------------------------

def filter_out_info(lines):
    """Remove lines with INFO keyword to reduce irrelevant tokens."""
    return [line for line in lines if "INFO" not in line]

# ------------------------------------------------------------------
# Step 2: Chunking - Split long log files into smaller, analyzable parts
# ------------------------------------------------------------------

def split_lines_into_chunks(lines, chunk_size=params["chunk_size"]):
    """Break long logs into smaller manageable parts."""
    for i in range(0, len(lines), chunk_size):
        yield lines[i:i + chunk_size]

# ---------------------------------------------------------
# Step 3: Cleanup - Move oldest temp files to backup folder
# ---------------------------------------------------------
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
    
# ------------------------------------------------------------
# Step 4: Formatter - Create a readable, structured summary
# ------------------------------------------------------------
def format_structured_summary(app_name, root_causes, remedies):
    return f"""The application or service '{app_name}' is experiencing issues due to a combination of {', '.join(root_causes)}.
Root Cause:
{''.join([f"* {r}\n" for r in root_causes])}
Remedial Actions:
{''.join([f"* {r}\n" for r in remedies])}
By addressing these issues, the application or service '{app_name}' can run smoothly and efficiently, providing a better user experience."""

# ------------------------------------------------------------
# ensure  directory exist
# ------------------------------------------------------------
def ensure_directories_exist(*paths):
    """Ensure each path exists. Create folders if missing."""
    for path in paths:
        os.makedirs(path, exist_ok=True)


# Extract clean JSON array
def extract_json_array(text):
        """Extract the first JSON array from the text using a regex pattern."""
        match = re.search(r"\[\s*{.*?}\s*]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError as e:
                print("❌ JSON decoding failed:", e)
                print("🔎 Raw match:", match.group())
                return []
        print("❌ No JSON array found in text.")
        return []
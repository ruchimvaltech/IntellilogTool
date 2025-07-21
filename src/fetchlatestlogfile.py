import json
import re
import os

# ------------------------
# Load configuration parameters from JSON file
# ------------------------
with open("./parameter.json", "r") as f:
    params = json.load(f)
log_dir = params["log_folder_path"]


def fetch_latest_log():
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"❌ Log directory '{log_dir}' does not exist.")

    logs = [
        os.path.join(log_dir, f)
        for f in os.listdir(log_dir)
        if "logs" in f.lower() or "log" in f.lower() and f.lower().endswith('.txt')
    ]

    if not logs:
        raise FileNotFoundError(f"❌ No '.txt' log files found in '{log_dir}'.")

    latest_log_path = max(logs, key=os.path.getmtime)
    # Remove the .txt extension but keep full path
    return latest_log_path
    

def parse_log(file_path):
    with open(file_path, 'r') as f:
        return f.read()
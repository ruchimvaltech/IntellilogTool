from openai import AzureOpenAI
from analyzer import filter_out_info
from analyzer import split_lines_into_chunks
from analyzer import clean_temp_folder
import json
client = AzureOpenAI(
    api_key="995bG4KqqLjDNhtX6kT7RpQdEAR0dWyTx0vtuamAk5LCkTLvg5UuJQQJ99BGACfhMk5XJ3w3AAAAACOGEasD",
    api_version="2025-01-01-preview",
    azure_endpoint="https://ragha-mdcwxj9l-swedencentral.openai.azure.com/"
)
# Load parameter config
with open("./parameter.json", "r") as f:
    params = json.load(f)

temp_dir = params["temp_dir"]
backup_dir = params["backup_dir"]
chunk_size = params["chunk_size"]

def call_gpt_summary(logs: str) -> str:
    print("Starting analysis...")
    lines = logs.strip().splitlines()
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
Analyze the logs below and return a JSON array, even if there's only one event.
Return a summary in JSON format with these fields:
- timestamp
- level (INFO, WARNING, ERROR)
- event_summary
- action_needed (Yes/No)
- recommended_action
"""
    result = client.chat.completions.create(
        model="log-summarizer",  # This is the *deployment name*, not the model family name
        messages=[
            {"role": "system", "content": "You are an expert in application log analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    partial_summaries.append(result.choices[0].message.content.strip())

    combined_prompt = f"""
You're an expert log summarizer. Combine the following partial summaries into one summary.

{''.join(partial_summaries)}
Analyze the logs below and return a JSON array, even if there's only one event.
Return a summary in JSON format with these fields:
- timestamp
- level (INFO, WARNING, ERROR)
- event_summary
- action_needed (Yes/No)
- recommended_action
"""

    response = client.chat.completions.create(
        model="log-summarizer",  # This is the *deployment name*, not the model family name
        messages=[
            {"role": "system", "content": "You are an expert in application log analysis."},
            {"role": "user", "content": combined_prompt}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    final_summary = response.choices[0].message.content
  # Trigger cleanup if certain issues detected
    if "high memory usage" in final_summary.lower() or "low disk space" in final_summary.lower():
        clean_temp_folder(temp_dir, backup_dir)
        print("Temp files cleaned and moved after detecting high memory usage or low disk space.")

        # Try to extract a JSON array from possibly messy text
    
    
    return final_summary

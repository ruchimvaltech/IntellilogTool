from openai import AzureOpenAI
from analyzer import filter_out_info
from analyzer import split_lines_into_chunks
from analyzer import clean_temp_folder
import json
from notifier import send_mail_via_sendgrid
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
recipients = params["email"]["recipients"]
sender_email = params["email"]["sender"]

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

    # ✅ Check for CPU-related issues and send alert if needed
    trigger_cpu_alert_if_needed(final_summary)

  # Try to extract a JSON array from possibly messy text
    return final_summary


#Generates an email subject and HTML-formatted body using GPT based on a log summary.
def generate_email_content(log_summary: str) -> dict:
    prompt = f"""
You are an AI assistant writing alert emails.

Based on the log summary below, generate:
- A short and urgent **email subject** (max 12 words)
- A readable and professional **HTML-formatted body** (max 150 words)

Log Summary:
{log_summary}

Return output in this JSON format:
{{
  "subject": "Your subject here",
  "body": "Your HTML-formatted body here"
}}
"""

    try:
        response = client.chat.completions.create(
            model="log-summarizer",  # your Azure OpenAI deployment name
            messages=[
                {"role": "system", "content": "You write clear and concise alert emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("❌ GPT failed to generate email content:", e)
        return {
            "subject": "🚨 CPU Alert from IntelliLog",
            "body": f"<pre>{log_summary}</pre>"
        }
#Checks if the log summary contains CPU-related alert keywords and sends an email alert.
def trigger_cpu_alert_if_needed(final_summary: str):
    cpu_alert_keywords = [
        "high cpu usage", "cpu usage exceeded", "high cpu load", "cpu threshold breach"
    ]

    if not any(keyword in final_summary.lower() for keyword in cpu_alert_keywords):
        return  # No alert condition met

    print("⚠️ High CPU usage detected. Generating email...")

    # Let GPT create subject & HTML body
    email_content = generate_email_content(final_summary)

    for recipient in recipients:
        clean_email = recipient.strip()
        print(f"📨 Sending alert to: {clean_email}")
        success = send_mail_via_sendgrid(
        sender_mail=sender_email,
        recipient_email=clean_email,
        subject=email_content["subject"],
        body_html=email_content["body"]
        )

    if success:
        print("✅ CPU alert email sent.")
    else:
        print("❌ Email sending failed.")

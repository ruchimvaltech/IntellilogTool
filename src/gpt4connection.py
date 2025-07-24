from openai import AzureOpenAI
from analyzer import filter_out_info
from analyzer import split_lines_into_chunks
from analyzer import clean_temp_folder
import json
import re
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
    trigger_memory_or_disk_alert_if_needed(final_summary)

    # ✅ Check for CPU-related issues and send alert if needed
    trigger_cpu_alert_if_needed(final_summary)

  # Try to extract a JSON array from possibly messy text
    return final_summary


#Generates an email subject and HTML-formatted body using GPT based on a log summary.
def generate_email_content(log_summary: str) -> dict:
    prompt = f"""
You are an AI assistant writing alert emails for system performance issues.

The following log summary indicates a **CPU usage problem**. Based on it, generate:
- A short, urgent **email subject** (max 12 words) that clearly reflects a CPU issue.
- A professional, clear **HTML-formatted body** (max 150 words) that:
  - Describes the high CPU usage problem.
  - Highlights potential impact (e.g., system slowdown or overload).
  - Advises checking high-CPU processes or scaling resources.

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

# Checks if the log summary contains CPU-related alert keywords and sends an email alert.
def trigger_cpu_alert_if_needed(final_summary: str):
    def is_cpu_alert(summary: str) -> bool:
        lowered = summary.lower()

        # CPU-specific keywords
        cpu_keywords = [
            "cpu usage", "high cpu", "cpu utilization", "processor usage", "core usage",
            "cpu load", "cpu threshold", "cpu limit", "cpu saturation", "cpu spike",
            "cpu exceeded", "cpu overload", "processor load", "cpu overuse",
            "cpu and memory", "cpu & memory",
            "cpu-intensive", "high cpu processes"
        ]

        # Regex patterns for CPU-related usage, warnings, or limits
        cpu_patterns = [
            r"\b(cpu|processor)\b.*\b\d{2,3}%",                          # e.g., CPU at 95%
            r"(high|critical).*?\b(cpu|processor)\b",                   # e.g., high CPU
            r"\[(cpu|processor).*\b(high|usage|load|limit|warn)\b.*\]", # e.g., [CPU usage high]
            r"\(cpu.*(warn|load|limit|usage)\)"                         # e.g., (CPU load exceeded)
        ]

        if any(k in lowered for k in cpu_keywords):
            return True
        if any(re.search(p, lowered) for p in cpu_patterns):
            return True
        return False

    if not is_cpu_alert(final_summary):
        return  # No CPU alert condition met

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

# Checks if the log summary contains high memory and low disk related alert errors its sends an email alert and moves the last 5 file to backupdir.
def trigger_memory_or_disk_alert_if_needed(final_summary: str):
    lowered = final_summary.lower()

    # Regex patterns for memory and disk issues
    memory_patterns = [
        r"high memory (usage|consumption|utilization)",
        r"memory (limit|threshold|cap).*exceeded",
        r"memory usage.*(high|critical)",
    ]
    disk_patterns = [
        r"low disk space",
        r"disk space.*(low|critical)",
        r"insufficient (disk|storage) space",
        r"low space (on|available|remaining)",
    ]

    memory_issue = any(re.search(p, lowered) for p in memory_patterns)
    disk_issue = any(re.search(p, lowered) for p in disk_patterns)

    if memory_issue or disk_issue:
        clean_temp_folder(temp_dir, backup_dir)
        print("🧹 Temp files cleaned and moved after detecting high memory usage or low disk space.")

        # Construct GPT prompt
        prompt = f"""
You are an AI assistant writing system alert emails related to memory or disk issues.

Based on the log summary below, generate:
- A short, urgent **email subject** (max 12 words)
- A clear, professional **HTML-formatted body** (max 150 words) describing the issue and stating that temporary files are being cleaned up and moved to a backup location.

Return output in this JSON format:
{{
  "subject": "Your subject here",
  "body": "Your HTML-formatted body here"
}}

Log Summary:
{final_summary}
"""

        try:
            response = client.chat.completions.create(
                model="log-summarizer",
                messages=[
                    {"role": "system", "content": "You write alert emails for system health events."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )
            email_content = json.loads(response.choices[0].message.content)
        except Exception as e:
            print("❌ GPT failed to generate memory/disk alert email:", e)
            email_content = {
                "subject": "🚨 Memory/Disk Alert from IntelliLog",
                "body": f"<pre>{final_summary}</pre>"
            }

        for recipient in recipients:
            clean_email = recipient.strip()
            print(f"📨 Sending memory/disk alert to: {clean_email}")
            success = send_mail_via_sendgrid(
                sender_mail=sender_email,
                recipient_email=clean_email,
                subject=email_content["subject"],
                body_html=email_content["body"]
            )

        if success:
            print("✅ Memory/Disk alert email sent.")
        else:
            print("❌ Email sending failed.")



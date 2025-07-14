def clean_log(log_content: str) -> str:
    """
    Preprocess log content (e.g., remove empty lines or sensitive info).
    """
    lines = [line for line in log_content.splitlines() if line.strip()]
    return "\n".join(lines)
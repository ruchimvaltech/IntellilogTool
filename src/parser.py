def parse_log(log_content: str) -> dict:
    """
    Parse logs to count lines and show sample lines.
    """
    lines = log_content.splitlines()
    return {
        "line_count": len(lines),
        "first_lines_sample": lines[:5]
    }
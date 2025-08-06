import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder
from gpt4connection import call_gpt_summary
import plotly.express as px
from fetchlatestlogfile import fetch_latest_log, parse_log

# ----------- Utility Function to Format Summary Text -----------
def format_summary_text(summary):
    lines = []
    for i, item in enumerate(summary, 1):
        lines.append(f"Issue {i}:")
        lines.append(f"• Timestamp: {item.get('timestamp', '')}")
        lines.append(f"• Level: {item.get('level', '')}")
        lines.append(f"• Summary: {item.get('event_summary', '')}")
        lines.append(f"• Suggestion: {item.get('recommended_action', '')}")
        lines.append("")  # Add a blank line between issues
    return "\n".join(lines)

# ----------- Log File Reader -----------
def read_log_file(uploaded_file):
    return uploaded_file.read().decode("utf-8")

# ----------- Main Streamlit App Function -----------
def main():
    st.set_page_config(page_title="Log Summarizer", layout="wide")
    st.title("📊 Intellilog Dashboard")

    uploaded_file = st.file_uploader("📁 Upload your .log or .txt file", type=["log", "txt"])
    triggerlatestfile = st.button("Analyse Latest Log file")

    # ----------- If User Uploads a File -----------
    if uploaded_file:
        log_text = read_log_file(uploaded_file)
        st.text_area("📜 Raw Logs", log_text, height=200)

        with st.spinner("Analyzing logs ..."):
            summary = call_gpt_summary(log_text)

        try:
            json_start = summary.find("[")
            json_end = summary.rfind("]") + 1
            json_str = summary[json_start:json_end]
            summary = json.loads(json_str)
        except Exception as e:
            st.error("❌ GPT response could not be parsed as JSON.")
            st.text("Raw GPT response:")
            st.code(summary)
            st.text(f"Error: {e}")
            summary = []

        if summary:
            df = pd.DataFrame(summary)
            st.subheader("📌 Event Summary Table")

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(filter=True, sortable=True, editable=False)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_selection("single")
            grid_options = gb.build()

            AgGrid(df, gridOptions=grid_options, height=300, theme="streamlit")

            st.subheader("📊 Log Event Distribution")
            level_counts = df["level"].value_counts().reset_index()
            level_counts.columns = ["level", "count"]
            fig = px.bar(level_counts, x="level", y="count", color="level",
                         title="Log Events by Level", color_discrete_map={
                             "ERROR": "red", "WARNING": "orange", "INFO": "blue"
                         })
            st.plotly_chart(fig, use_container_width=True)

            summary_text = format_summary_text(summary)
            st.download_button(
                label="⬇️ Download Summary as TXT",
                data=summary_text,
                file_name="summary.txt",
                mime="text/plain"
            )

    # ----------- Analyze Latest File -----------
    if triggerlatestfile:
        log_file = fetch_latest_log()
        raw_log = parse_log(log_file)
        st.text_area("📜 Raw Logs", raw_log, height=200)

        with st.spinner("Analyzing logs with GPT-4.1..."):
            summary = call_gpt_summary(raw_log)

        try:
            json_start = summary.find("[")
            json_end = summary.rfind("]") + 1
            json_str = summary[json_start:json_end]
            summary = json.loads(json_str)
        except Exception as e:
            st.error("❌ GPT response could not be parsed as JSON.")
            st.text("Raw GPT response:")
            st.code(summary)
            st.text(f"Error: {e}")
            summary = []

        if summary:
            df = pd.DataFrame(summary)
            st.subheader("📌 Event Summary Table")

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(filter=True, sortable=True, editable=False)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_selection("single")
            grid_options = gb.build()

            AgGrid(df, gridOptions=grid_options, height=300, theme="streamlit")

            st.subheader("📊 Log Event Distribution")
            level_counts = df["level"].value_counts().reset_index()
            level_counts.columns = ["level", "count"]
            fig = px.bar(level_counts, x="level", y="count", color="level",
                         title="Log Events by Level", color_discrete_map={
                             "ERROR": "red", "WARNING": "orange", "INFO": "blue"
                         })
            st.plotly_chart(fig, use_container_width=True)

            summary_text = format_summary_text(summary)
            st.download_button(
                label="⬇️ Download Summary as TXT",
                data=summary_text,
                file_name="summary.txt",
                mime="text/plain"
            )

# ----------- Run App -----------
if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder
from gpt4connection import call_gpt_summary
import plotly.express as px
# Import the logfile function from fetchlatestlogfile.py
from fetchlatestlogfile import fetch_latest_log
from fetchlatestlogfile import parse_log



# ---- Functions ----
def read_log_file(uploaded_file):
    return uploaded_file.read().decode("utf-8")


    system_prompt = "You are a senior DevOps engineer analyzing logs."
    user_prompt = f"""
Analyze the logs below. Return a JSON array with:
- timestamp
- level (INFO, WARNING, ERROR)
- event_summary
- action_needed (Yes/No)
- recommended_action

Logs:
{log_text}
"""
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    content = response.choices[0].message["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        st.error("❌ GPT-4.1 response is not valid JSON.")
        st.code(content)
        return []

# ---- Streamlit UI ----
st.set_page_config(page_title="Log Summarizer", layout="wide")
st.title("📊 Intellilog Dashboard")

uploaded_file = st.file_uploader("📁 Upload your .log or .txt file", type=["log", "txt"])
triggerlatestfile = st.button("Analyse Latest Log file")

if uploaded_file:
    log_text = read_log_file(uploaded_file)
    st.text_area("📜 Raw Logs", log_text, height=200)

    with st.spinner("Analyzing logs ..."):
        summary = call_gpt_summary(log_text)
    try:
        # Clean content if needed
        json_start = summary.find("[")
        json_end = summary.rfind("]") + 1
        json_str = summary[json_start:json_end]
        summary= json.loads(json_str)
    except Exception as e:
        st.error("❌ GPT response could not be parsed as JSON.")
        st.text("Raw GPT response:")
        st.code(summary)
        st.text(f"Error: {e}")
        summary= []
    if summary:
        df = pd.DataFrame(summary)
        st.subheader("📌 Event Summary Table")

        # ---- AG Grid with Search ----
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(filter=True, sortable=True, editable=False)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_selection("single")
        grid_options = gb.build()

        AgGrid(df, gridOptions=grid_options, height=300, theme="streamlit")

        # ---- Bar Chart of Log Levels ----
        st.subheader("📊 Log Event Distribution")

        level_counts = df["level"].value_counts().reset_index()
        level_counts.columns = ["level", "count"]

        fig = px.bar(level_counts, x="level", y="count", color="level",
                     title="Log Events by Level", color_discrete_map={
                         "ERROR": "red", "WARNING": "orange", "INFO": "blue"
                     })

        st.plotly_chart(fig, use_container_width=True)



#Analyse latest file

if triggerlatestfile:
    log_file = fetch_latest_log()
    raw_log = parse_log(log_file)
    st.text_area("📜 Raw Logs", raw_log, height=200)

    with st.spinner("Analyzing logs with GPT-4.1..."):
        summary = call_gpt_summary(raw_log)
    try:
        # Clean content if needed
        json_start = summary.find("[")
        json_end = summary.rfind("]") + 1
        json_str = summary[json_start:json_end]
        summary= json.loads(json_str)
    except Exception as e:
        st.error("❌ GPT response could not be parsed as JSON.")
        st.text("Raw GPT response:")
        st.code(summary)
        st.text(f"Error: {e}")
        summary= []
    if summary:
        df = pd.DataFrame(summary)
        st.subheader("📌 Event Summary Table")

        # ---- AG Grid with Search ----
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(filter=True, sortable=True, editable=False)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_selection("single")
        grid_options = gb.build()

        AgGrid(df, gridOptions=grid_options, height=300, theme="streamlit")

        # ---- Bar Chart of Log Levels ----
        st.subheader("📊 Log Event Distribution")

        level_counts = df["level"].value_counts().reset_index()
        level_counts.columns = ["level", "count"]

        fig = px.bar(level_counts, x="level", y="count", color="level",
                     title="Log Events by Level", color_discrete_map={
                         "ERROR": "red", "WARNING": "orange", "INFO": "blue"
                     })

        st.plotly_chart(fig, use_container_width=True)
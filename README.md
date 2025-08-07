# Intellilog - AI Log Analyzer Tool

🚀 Python-based log analyzer using Azure AI Foundry gpt-4.1 .

## 💡 Features

- Analyze logs locally using gpt-4.1 model
- Preprocess and parse logs
- Visualize summary with errors, warning details and respective recommendations

############################################################################################

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

## Add some files in below folder in specific path

- "D:/Hackathon/TempDir"

## For analyzing the latest log please give your path in paramete.json

- "log_folder_path": "src/SampleLogs/"

#############################################################################################

## For Email triggering -

## you can configure secrets.toml file. Create a .streamlit directory in the root of your project and add a file named secrets.toml inside it. Define your secrets in this file using TOML syntax, for example: API_KEY = "your_api_key_here".

SENDGRID_API_KEY="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"

- Specify the valid recipient's email address in Parameter.json for email triggering.

#############################################################################################

## 📊 Run the app

Go to root folder
Run "streamlit run src/app.py"

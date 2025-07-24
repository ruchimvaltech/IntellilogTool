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
pip install openai
pip install streamlit pandas openai streamlit-aggrid plotly
```

## create .env under src and place your secret key under variable SENDGRID_API_KEY:

SENDGRID_API_KEY=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

## create below folders in specific path

- "D:/Hackathon/App_Data/logs",
- "D:/Hackathon/TempDir",
- "D:/Hackathon/BackupDir"

#############################################################################################

## 📊 Run the app

Go to "./src" folder
Run "streamlit run app.py"

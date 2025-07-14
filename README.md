# Intellilog - AI Log Analyzer Tool

🚀 Python-based log analyzer using LLaMA (local).

## 💡 Features

- Analyze logs locally using LLaMA (llama-cpp-python)
- Preprocess and parse logs
- Visualize summary word counts

## ⚙️ Setup

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🐴 LLaMA Model

- Download your GGUF model file (e.g., llama-2-7b.Q4_K_M.gguf)
  URL - https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf
- Place it in: `src/models/`

## 🚀 Run

```bash
python src/main.py
```

Make sure to add a `sample_log.txt` file in the root folder with log content.

## 📊 Visualization

Modify `visualizer.py` to add more advanced charts.

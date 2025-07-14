from llama_cpp import Llama
import math

# ✅ Make sure this path matches your actual model file name!
llm = Llama(model_path="./src/models/llama-2-7b-chat.Q4_K_M.gguf")

def split_text(text, max_chars=6000):
    """
    Split text into chunks of at most max_chars characters each.
    """
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def analyze_logs_with_llama(log_content: str) -> str:
    print("Model initialized!")

    # Split into chunks (roughly ~1500 tokens ≈ 6000 chars)
    chunks = split_text(log_content, max_chars=6000)
    print(f"Log split into {len(chunks)} chunks.")

    partial_summaries = []

    for idx, chunk in enumerate(chunks):
        print(f"Summarizing chunk {idx + 1}/{len(chunks)}")

        prompt = (
            "You are an expert log analysis AI. "
            "Summarize the following log section and suggest possible fixes:\n\n"
            f"{chunk}\n\n"
            "Summary:"
        )

        output = llm(prompt, max_tokens=300, stop=["</s>"])
        result_text = output["choices"][0]["text"].strip()
        partial_summaries.append(result_text)

    # Combine partial summaries
    final_prompt = (
        "You are an expert log analysis AI. Combine the following partial summaries into one concise overall summary with suggestions:\n\n"
        + "\n\n".join(partial_summaries)
        + "\n\nFinal Summary:"
    )

    output = llm(final_prompt, max_tokens=400, stop=["</s>"])
    final_summary = output["choices"][0]["text"].strip()

    return final_summary

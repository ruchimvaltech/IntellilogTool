import matplotlib.pyplot as plt

def show_summary_chart(summary_text: str):
    """
    Example: Show chart of word counts as a dummy visualization.
    """
    words = summary_text.split()
    word_counts = {w: words.count(w) for w in set(words)}
    top_words = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:10])

    plt.figure(figsize=(10, 5))
    plt.bar(top_words.keys(), top_words.values())
    plt.title("Top Words in Summary")
    plt.xticks(rotation=45)
    plt.show()
def word_count(text: str) -> int:
    return len([t for t in text.strip().split() if t])

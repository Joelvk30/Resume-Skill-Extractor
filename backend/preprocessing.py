import re


def normalize_text(text):
    """
    Clean and normalize input text.
    """

    # Convert all text to lowercase
    text = text.lower()

    # Replace line breaks and multiple spaces
    # with a single space
    text = re.sub(r"\s+", " ", text)

    # Keep letters, numbers and common programming symbols
    text = re.sub(r"[^a-zA-Z0-9+#.\- ]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text):
    """
    Split text into individual words.
    """

    return text.split()


def create_ngrams(tokens, n):
    """
    Create n-word combinations.

    Example:

    ["machine", "learning", "using", "python"]

    n = 2

    Returns:

    [
        "machine learning",
        "learning using",
        "using python"
    ]
    """

    ngrams = []

    for i in range(len(tokens) - n + 1):

        phrase = " ".join(tokens[i:i + n])

        ngrams.append(phrase)

    return ngrams
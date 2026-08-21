import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize
    words = nltk.word_tokenize(text)

    # Remove stopwords and lemmatize
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]

    return words


def get_response(user_input):

    words = preprocess_text(user_input)

    # Basic responses
    if "hello" in words or "hi" in words:
        return "Hello! How can I help you?"

    if "name" in words:
        return "I am an NLP chatbot."

    if "how" in words and "you" in words:
        return "I'm doing great! Thanks for asking."

    if "bye" in words or "goodbye" in words:
        return "Goodbye! Have a great day."

    return "I'm sorry, I don't understand that yet."
import re

from backend.preprocessing import (
    normalize_text,
    tokenize,
    create_ngrams
)

from backend.rules import (
    SKILLS,
    TECHNOLOGIES,
    PROGRAMMING_LANGUAGES,
    ALIASES
)


def apply_aliases(text):
    """
    Replace common abbreviations with their
    standard/full forms.

    Example:
        ml  -> machine learning
        ai  -> artificial intelligence
        nlp -> natural language processing
    """

    words = text.split()

    replaced_words = []

    for word in words:

        if word in ALIASES:
            replaced_words.extend(
                ALIASES[word].split()
            )

        else:
            replaced_words.append(word)

    return " ".join(replaced_words)


def find_matches(text, dictionary):
    """
    Search the input text for entities contained
    in our local NLP dictionary.

    Example:

        text:
        "i know python and machine learning"

        dictionary:
        {
            "python": "Python",
            "machine learning": "Machine Learning"
        }

        result:
        [
            "Python",
            "Machine Learning"
        ]
    """

    found = []

    for keyword, display_name in dictionary.items():

        # Escape special characters such as
        # + in C++.
        escaped_keyword = re.escape(keyword)

        # Match complete words/phrases rather than
        # matching part of another word.
        pattern = (
            r"(?<!\w)"
            + escaped_keyword
            + r"(?!\w)"
        )

        if re.search(pattern, text):

            found.append(display_name)

    return found


def remove_duplicates(items):
    """
    Remove duplicate values while preserving
    their original order.
    """

    return list(dict.fromkeys(items))


def extract_information(text):
    """
    Main NLP extraction pipeline.

    Input:
        Raw text

    Output:
        Dictionary containing:

        skills
        technologies
        languages
    """


    # NORMALIZATION
    

    cleaned_text = normalize_text(text)


    #  ALIAS HANDLING
    
    cleaned_text = apply_aliases(cleaned_text)


   
    #  TOKENIZATION
    

    tokens = tokenize(cleaned_text)


    
    #  N-GRAM GENERATION
    

    bigrams = create_ngrams(
        tokens,
        2
    )

    trigrams = create_ngrams(
        tokens,
        3
    )

    # to phrase-based extraction.
    phrases = bigrams + trigrams

    
    #  ENTITY EXTRACTION
    
    skills = find_matches(
        cleaned_text,
        SKILLS
    )

    technologies = find_matches(
        cleaned_text,
        TECHNOLOGIES
    )

    languages = find_matches(
        cleaned_text,
        PROGRAMMING_LANGUAGES
    )


    
# REMOVE DUPLICATES

    skills = remove_duplicates(skills)

    technologies = remove_duplicates(
        technologies
    )

    languages = remove_duplicates(
        languages
    )



    # CREATE STRUCTURED OUTPUT

    result = {
        "skills": skills,
        "technologies": technologies,
        "languages": languages
    }

    return result
import re
import nltk
import spacy

# Ensure NLTK has required datasets
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")  # Needed for lemmatization

# Load spaCy English model (for grammar parsing)
nlp = spacy.load("en_core_web_sm")

def analyze_text(text):
    """Compute various linguistic metrics without AI."""

    # Tokenization & Word Statistics
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    unique_words = len(set(words))
    type_token_ratio = unique_words / total_words if total_words > 0 else 0

    # Morpheme Estimation (Basic Heuristic)
    num_morphemes = sum(1 for word in words if re.search(r'(ed|ing|s|ly|er|est)$', word)) + total_words  

    # Clause Detection Using spaCy
    doc = nlp(text)
    num_clauses = sum(1 for sent in doc.sents)
    subordinate_clauses = sum(1 for token in doc if token.dep_ == "mark")

    syntactic_subordination_index = (
        subordinate_clauses / num_clauses if num_clauses > 0 else 0
    )

    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "type_token_ratio": round(type_token_ratio, 3),
        "num_morphemes": num_morphemes,
        "num_clauses": num_clauses,
        "subordinate_clauses": subordinate_clauses,
        "syntactic_subordination_index": round(syntactic_subordination_index, 3),
    }

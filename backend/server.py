import os
import re
import nltk
import spacy
from flask import Flask, request, jsonify
from flask_cors import CORS
from llama import analyze_story_grammar, analyze_cohesion

# ------------------------------
# Setup for non-AI text analysis
# ------------------------------
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")

# Load spaCy English model for grammar parsing
nlp = spacy.load("en_core_web_sm")

def analyze_text(text):
    """
    Compute various linguistic metrics without AI.
    """
    # Tokenization & word statistics
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    unique_words = len(set(words))
    type_token_ratio = unique_words / total_words if total_words > 0 else 0

    # Basic heuristic for morpheme estimation
    num_morphemes = sum(1 for word in words if re.search(r'(ed|ing|s|ly|er|est)$', word)) + total_words  

    # Clause detection using spaCy
    doc = nlp(text)
    num_clauses = sum(1 for sent in doc.sents)
    subordinate_clauses = sum(1 for token in doc if token.dep_ == "mark")
    syntactic_subordination_index = subordinate_clauses / num_clauses if num_clauses > 0 else 0

    # Placeholder for verb and word choice errors:
    # (Replace the following with your actual error detection logic)
    verb_errors = 0
    verb_errors_per_clause = verb_errors / num_clauses if num_clauses > 0 else 0
    word_choice_errors = 0
    word_choice_errors_per_word = word_choice_errors / total_words if total_words > 0 else 0

    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "type_token_ratio": round(type_token_ratio, 3),
        "num_morphemes": num_morphemes,
        "num_clauses": num_clauses,
        "subordinate_clauses": subordinate_clauses,
        "syntactic_subordination_index": round(syntactic_subordination_index, 3),
        "verb_errors": verb_errors,
        "verb_errors_per_clause": verb_errors_per_clause,
        "word_choice_errors": word_choice_errors,
        "word_choice_errors_per_word": word_choice_errors_per_word,
    }


# ------------------------------
# Flask app setup and endpoints
# ------------------------------
app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})

@app.route("/analyze", methods=["POST"])
def analyze():
    """Handles text analysis request with a properly weighted accuracy calculation."""
    data = request.get_json()
    text = data.get("text", "").strip()
    selected_options = data.get("options", {})

    if not text:
        return jsonify({"error": "No text provided"}), 400

    print(f"🟢 Flask received text: {text}")

    results = {}
    accuracy_scores = []
    total_selected_params = 0  # Count total selected options for proper weighting

    # Mapping between front-end keys and analyze_text keys
    key_map = {
        "totalWords": "total_words",
        "differentWords": "unique_words",
        "typeTokenRatio": "type_token_ratio",
        "numMorphemes": "num_morphemes",
        "numClauses": "num_clauses",
        "subordinateClauses": "subordinate_clauses",
        "subordinationIndex": "syntactic_subordination_index",
        "verbErrors": "verb_errors",
        "verbErrorsPerClause": "verb_errors_per_clause",
        "wordChoiceErrors": "word_choice_errors",
        "wordChoiceErrorsPerWord": "word_choice_errors_per_word"
    }


    # Non-AI Text Analysis using mapping
    text_metrics = analyze_text(text)
    for key, is_selected in selected_options.items():
        if key in key_map and is_selected:
            mapped_key = key_map[key]
            results[key] = text_metrics.get(mapped_key, "N/A")
            accuracy_scores.append(100)  # Non-AI tasks assumed 100% accurate
            total_selected_params += 1

    # AI-Based Story Grammar Analysis
    if selected_options.get("storyGrammar"):
        ai_response = analyze_story_grammar(text)
        if isinstance(ai_response, dict) and "analysis" in ai_response:
            results["story_grammar"] = ai_response.get("analysis", "N/A")
            ai_confidence = ai_response.get("confidence", 50)
            accuracy_scores.append(ai_confidence)
        else:
            results["story_grammar"] = "AI response failed."
            accuracy_scores.append(50)
        total_selected_params += 1

    # AI-Based Cohesion Analysis
    if selected_options.get("cohesion"):
        ai_response = analyze_cohesion(text)
        if isinstance(ai_response, dict) and "analysis" in ai_response:
            results["cohesion"] = ai_response.get("analysis", "N/A")
            ai_confidence = ai_response.get("confidence", 50)
            accuracy_scores.append(ai_confidence)
        else:
            results["cohesion"] = "AI response failed."
            accuracy_scores.append(50)
        total_selected_params += 1

    # Properly Weighted Accuracy Calculation
    if total_selected_params > 0:
        final_accuracy = sum(accuracy_scores) / total_selected_params
    else:
        final_accuracy = 100  # Default to 100% if nothing was selected

    return jsonify({"results": results, "accuracy": round(final_accuracy, 2)})

if __name__ == "__main__":
    app.run(debug=False, threaded=True, port=5000)

import os
import json
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Retrieve Hugging Face API token
ACCESS_TOKEN = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

# Ensure access token is provided
if not ACCESS_TOKEN:
    raise ValueError("HUGGINGFACE_ACCESS_TOKEN is not set. Please log in using 'huggingface-cli login' or set the token manually.")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=ACCESS_TOKEN)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, token=ACCESS_TOKEN)
llama_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

def extract_json(response_text):
    """Extract JSON from AI response."""
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        return json.loads(response_text[json_start:json_end])
    except Exception:
        return {"analysis": "AI response parsing failed.", "confidence": 50}

def analyze_story_grammar(text):
    """Analyze story grammar using LLaMA 2 with confidence estimation."""
    prompt = (
        f"Analyze the following text for story grammar elements "
        f"(setting, initiating event, internal response, attempt, consequence, resolution).\n\n"
        f"Text: {text}\n\n"
        f"Provide a JSON response with:\n"
        f"- 'analysis': Summary of story grammar\n"
        f"- 'confidence': Confidence percentage (out of 100)"
    )
    results = llama_pipeline(prompt, max_length=500)
    return extract_json(results[0]["generated_text"])

def analyze_cohesion(text):
    """Analyze text cohesion using LLaMA 2."""
    prompt = (
        f"Analyze the following text for cohesion (pronoun clarity, logical flow, temporal markers).\n\n"
        f"Text: {text}\n\n"
        f"Provide a JSON response with:\n"
        f"- 'analysis': Summary of cohesion\n"
        f"- 'confidence': Confidence percentage (out of 100)"
    )
    results = llama_pipeline(prompt, max_length=500)
    return extract_json(results[0]["generated_text"])

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"


def query_ollama(prompt, model="llama3.2:3b", temperature=0.7):
    """Send a prompt to a locally running Ollama model and return the response"""
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.RequestException as e:
        return f"[Error] failed to query Ollama: {e}"

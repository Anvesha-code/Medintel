import requests

class OllamaLLM:
    def __init__(self, model: str = "tinyllama:latest"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

        print(f"🧠 OllamaLLM initialized with model: {self.model}")

    def generate(self, prompt: str) -> str:
        print(f" Ollama generate() called with model: {self.model}")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            print(" Ollama error:", response.text)
            return "The document does not explicitly state this information."

        return response.json().get("response", "").strip()

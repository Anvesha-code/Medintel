import os
from openai import OpenAI


class OpenAILLM:
    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

#
# import requests
#
# class OllamaLLM:
#     def __init__(self, model: str = "tinyllama:latest"):
#         self.model = model
#         self.url = "http://localhost:11434/api/generate"
#
#         print(f"🧠 OllamaLLM initialized with model: {self.model}")
#
#     def generate(self, prompt: str) -> str:
#         print(f" Ollama generate() called with model: {self.model}")
#
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "stream": False
#         }
#
#         response = requests.post(self.url, json=payload)
#
#         if response.status_code != 200:
#             print(" Ollama error:", response.text)
#             return "The document does not explicitly state this information."
#
#         return response.json().get("response", "").strip()
#
#

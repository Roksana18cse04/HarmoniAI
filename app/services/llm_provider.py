# app/services/llm_provider.py

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    def __init__(self, provider: str, model):
        self.provider = provider.lower()
        self.model = model

    def generate_response(self, system_prompt, user_prompt):
        if self.provider == "chatgpt":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "grok":
            return self._call_groq(system_prompt, user_prompt)
        elif self.provider == "gemini":
            return self._call_google(system_prompt, user_prompt)
        else:
            return {"status": "error", "content": None, "error": f"Unsupported provider: {self.provider}"}

    def _call_openai(self, system_prompt, user_prompt):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                # model="gpt-4",
                model= self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            content = response.choices[0].message.content.strip()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "content": None, "error": str(e)}

    def _call_groq(self, system_prompt, user_prompt):
        print("call groq")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            # "model": "llama3-70b-8192",
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "content": None, "error": str(e)}

    def _call_google(self, system_prompt, user_prompt):
        print("call google")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent" # gemini-2.5-pro-preview-05-06
        headers = {"Content-Type": "application/json"}
        params = {"key": os.getenv("GEMINI_API_KEY")}
        payload = {
            "contents": [{
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt}
                ]
            }]
        }
        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "content": None, "error": str(e)}

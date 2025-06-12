# app/services/llm_provider.py

import os
import json
from openai import OpenAI
import requests

from dotenv import load_dotenv
load_dotenv()

class LLMProvider:
    def __init__(self, provider: str):
        self.provider = provider.lower()

    def generate_response(self, system_prompt, user_prompt):
        if self.provider == "chatgpt":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "grok":
            return self._call_groq(system_prompt, user_prompt)
        elif self.provider == "gemini":
            return self._call_google(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_openai(self, system_prompt, user_prompt):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def _call_groq(self, system_prompt, user_prompt):
        print("call groq")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]

    def _call_google(self, system_prompt, user_prompt):
        print("call google")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
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
        response = requests.post(url, headers=headers, params=params, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]



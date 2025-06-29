# app/services/llm_provider.py

import os
import requests
from openai import OpenAI
from app.services.extract_json_from_response import extract_json_from_llm
from dotenv import load_dotenv
import json

load_dotenv()

import json
import re




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
            print("row llm response--------------", response)
            content = response.choices[0].message.content
            print(content)
            result = extract_json_from_llm(content)
            return {"status": "success", "content": result}
        
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
            content = response['choices'][0]['message']['content'].strip()
            # Try to load as JSON only if it starts with { or [
            if content.startswith('{') or content.startswith('['):
                result = json.loads(content)
            else:
                result = content.strip('"')
            return {"status": "success", "content": result}
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
            # Try to load as JSON only if it starts with { or [
            if content.startswith('{') or content.startswith('['):
                result = json.loads(content)
            else:
                result = content.strip('"')
            return {"status": "success", "content": result}
        except Exception as e:
            return {"status": "error", "content": None, "error": str(e)}

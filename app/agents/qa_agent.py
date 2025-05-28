# qa_agent.py
import os
from openai import OpenAI
from serpapi import GoogleSearch
from dotenv import load_dotenv
import trafilatura

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_current_event(prompt: str) -> bool:
    keywords = ["today", "now", "latest", "current", "trending", "news"]
    return any(kw in prompt.lower() for kw in keywords)

def search_web_urls(prompt: str, limit: int = 3) -> list:
    search = GoogleSearch({
        "q": prompt,
        "api_key": os.getenv("SERPAPI_KEY")
    })
    results = search.get_dict()
    return [item["link"] for item in results.get("organic_results", [])[:limit]]

def extract_content_from_url(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return ""

def summarize_content(content: str, original_prompt: str) -> str:
    messages = [
        {"role": "system", "content": """You are a helpful assistant that reads web content and answers questions based on it. When providing temperature, adapt to the user's country if known: 
- For the US and similar countries, provide Fahrenheit primarily with Celsius in parentheses.
- For other countries, provide Celsius primarily with Fahrenheit in parentheses.
- If the user's location is unknown, provide both units equally, e.g. '20°C (68°F)'.
        """},
        {"role": "user", "content": f"Based on the following article, answer this user query: '{original_prompt}'\n\nArticle:\n{content}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def gpt_answer(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who answers questions clearly and factually.If the user mentions a specific domain (e.g., AI, medicine, law), prefer answering in that domain."},
            {"role": "user", "content": prompt} 
            
        ]
    )
    return response.choices[0].message.content.strip()

# Main agent function
def question_answer_agent(prompt: str) -> str:
    if is_current_event(prompt):
        urls = search_web_urls(prompt)
        print("response urls:----", urls)
        for url in urls:
            content = extract_content_from_url(url)
            if content and len(content) > 500:  # skip short or empty articles
                try:
                    return summarize_content(content, prompt)
                except Exception as e:
                    continue  # fallback to next URL if any issue
        return "Sorry, I couldn’t extract enough useful content to answer your question."
    else:
        return gpt_answer(prompt)

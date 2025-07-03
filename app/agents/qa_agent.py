# qa_agent.py
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
import trafilatura
from app.services.llm_provider import LLMProvider
from app.services.price_calculate import price_calculate
import requests

load_dotenv()
from bs4 import BeautifulSoup

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

def summarize_content(platform, model, content: str, original_prompt: str) -> str:
    system_prompt = """
You are a helpful assistant that reads and understands web content, and answers user questions accurately based only on the information found in the provided article.

Your responsibilities:
- Extract factual answers from the article with clarity and precision.
- If the article includes a specific date or day (e.g. today’s date), extract and use that when answering related questions.
- If a date is not mentioned and the question depends on it, state clearly that the information is not present.
- If the content includes temperature, adapt it based on the user's country if known:
    - Use Fahrenheit primarily with Celsius in parentheses for users in the US and similar countries.
    - Use Celsius primarily with Fahrenheit in parentheses for other regions.
    - If the user's location is unknown, provide both units equally (e.g., 20°C (68°F)).
- If the content includes names, places, stats, or breaking news, report them exactly as found in the article.
- Do not invent facts or make assumptions beyond what the content states.
- If the article is incomplete, ambiguous, or lacks detail, let the user know.
- Behave like multilingual

Be concise, informative, and neutral. Only answer based on what the article explicitly says.
"""

    user_prompt = f"Based on the following article, answer this user query: '{original_prompt}'\n\nArticle:\n{content}"
    llm = LLMProvider(platform, model)
    return llm.generate_response(system_prompt, user_prompt)

def llm_answer(platform, model, prompt: str) -> str:
    system_prompt = "You are a helpful assistant who answers questions clearly and factually. If the user mentions a specific domain (e.g., AI, medicine, law), prefer answering in that domain."
    llm = LLMProvider(platform, model)
    response = llm.generate_response(system_prompt, prompt)
    return response

def question_answer_agent(platform: str, model, prompt: str, full_prompt) -> str:  
    # get history message

    # Step 3: Check for current event
    if is_current_event(prompt):
        urls = search_web_urls(prompt)
        print("response urls:----", urls)
        for url in urls:
            content = extract_content_from_url(url)
            print(content)
            if content and len(content) > 500:
                try:
                    response = summarize_content(platform,model, content, prompt)
                    price = price_calculate(platform, model, prompt, response)
                    return {
                        "status": response['status'],
                        "output": response['content'],
                        "price": price['price'],
                        "input_token": price['input_token'],
                        "output_token": price['output_token']
                    }
                except Exception as e:
                    continue
        return "Sorry, I couldn’t extract enough useful content to answer your question."
    
    # Step 4: Answer using full context
    else:
        response = llm_answer(platform, model, full_prompt)
        price = price_calculate(platform,model, prompt, response)
        return {
            "status": response['status'],
            "output": response['content'],
            "price": price['price'],
            "input_token": price['input_token'],
            "output_token": price['output_token']
        }
    

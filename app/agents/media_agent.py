import os
from dotenv import load_dotenv
from openai import OpenAI
from app.services.media_content import query_weaviate_media
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# === MEDIA AGENT ===
def media_agent(user_prompt):
    relevant_items = query_weaviate_media(user_prompt, top_k=10)

    print("Relevant media items -----------", relevant_items)

    media_text = "\n".join([
        f"- Title: {m.get('title')}, Description: {m.get('description')}, Rating: {m.get('rating')}, Duration: {m.get('duration')}, Link: {m.get('link')}, Image: {m.get('image')}"
        for m in relevant_items
    ])

    prompt = f"""You are a helpful media assistant.  
Here is a list of relevant content items:  
{media_text}  

The user asks: "{user_prompt}"  

**Task:**  
1. Select **up to 5** best-matching items (fewer if not enough are relevant).  
2. Return them as a **valid JSON array** with each item containing:  
   - `title` (string)  
   - `description` (string)  
   - `rating` (number)  
   - `image` (string, URL/path)  
   - `link` (string, URL)  
   - `duration` (string)  

**Rules:**  
- Only include items that truly match the query.  
- If no items match, return an empty array `[]`.  
- Respond **ONLY with JSON**, no additional text.  

Example output format:  
```json
[
    {{
        "title": "Inception",
        "description": "A skilled thief enters people’s dreams to steal secrets.",
        "rating": 8.8,
        "image": "https://example.com/inception.jpg",
        "link": "https://example.com/inception",
        "duration": "128"
    }}
]
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw response:")
        print(response.choices[0].message.content)
        return {"error": "Invalid JSON returned from model"}

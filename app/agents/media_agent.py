
from app.services.media_content import query_weaviate_media
from app.services.price_calculate import price_calculate
from app.services.llm_provider import LLMProvider
import json

# === MEDIA AGENT ===
def media_agent(platform, user_prompt):
    relevant_items = query_weaviate_media(platform, user_prompt, top_k=10)

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
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.3,
    # )

    llm = LLMProvider(platform)
    response = llm.generate_response("", prompt)
    print(response)
    try:
        # response_text = json.loads( response.choices[0].message.content )
        response_text = json.loads (response)
        price =  price_calculate("chatgpt", user_prompt, response_text)
        return {
            "response": response_text,
            "price": price['price'],
            "input_token": price['input_token'],
            "output_token": price['output_token']
        }


    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw response:")
        return {"error": "Invalid JSON returned from model"}


from app.services.media_content import query_weaviate_media
from app.services.price_calculate import price_calculate
from app.services.llm_provider import LLMProvider
import json

# === MEDIA AGENT ===
def media_agent(platform, model, user_prompt):
    relevant_items = query_weaviate_media(user_prompt, top_k=10)

    # print("Relevant media items -----------", relevant_items)

    media_text = "\n".join([
        f"- Title: {m.get('title')}, Description: {m.get('description')}, Rating: {m.get('rating')}, Duration: {m.get('duration')}, Link: {m.get('link')}, Image: {m.get('image')}"
        for m in relevant_items
    ])

    prompt = f"""You are a helpful media assistant.  
        Here is a list of relevant content items:  
        {media_text}  

        The user asks: "{user_prompt}"  
        - Behave like as multilangual 

        **Task:**  
        1. Select **up to 3** best-matching items (fewer if not enough are relevant).  
        2. Return them as a **valid JSON array** with each item containing:  
            - `id` (string)
            - `title` (string)  
            - `description` (string)  
            - `rating` (number)  
            - `image` (string, URL/path)  
            - `link` (string, URL)  
            - `duration` (string)  

        ### Rules:
        - Only include items that are relevant to the user's query.
        - If no items are relevant, return an empty JSON array: `[]`.
        - Your response **must be valid JSON only** — no explanations, comments, or markdown formatting. 

        """
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.3,
    # )

    llm = LLMProvider(platform, model)
    response = llm.generate_response("", prompt)
    # print("llm_response---------------",response)
    try:
        # response_text = json.loads( response.choices[0].message.content )
        price =  price_calculate(platform,model, user_prompt, response)
        return {
            "status": response['status'],
            "output": response['content'],
            "price": price['price'],
            "input_token": price['input_token'],
            "output_token": price['output_token']
        }


    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw response:")
        return {"error": "Invalid JSON returned from model"}

import os
from dotenv import load_dotenv
from app.services.image_face_swap import face_swap
from app.services.image_style_change import style_change
from app.services.image_style_convert import image_style_and_color_change
from app.services.baby_face_generate import baby_face
from app.services.background_remove import background_remove
from app.services.blackwhite_to_color_image import draw_image_color
from app.services.dress_trail import dress_trial
from app.services.image_merge import image_merge
from app.services.product_photo_shot import product_photo_generate
from app.services.price_calculate import price_calculate
from app.services.llm_provider import LLMProvider

# Load environment and OpenAI client
load_dotenv()
def detect_image_edit_type(prompt: str, platform, llm_model) -> tuple[str, float]:
    system_prompt = """
        You are an intelligent image editing command classifier.

        Your task is to analyze the user's image edit request — regardless of the language — and return EXACTLY three outputs in the format below:

        prompt: <the translated prompt in English>  
        category: <one of the predefined categories below>  
        style_slug: <one valid style slug from the list, or None>  
        gender: <'girl', 'boy', or None>

        🛑 Your output MUST always be in English — even if the input is not.

        🧠 Definitions:
        - style_change: apply a new *style* to an image (anime, cartoon, etc.)
        - style_convert: apply the *style of one image* onto another
        - If nothing fits, choose category: other and describe briefly in prompt.

        🎯 Valid categories:
        - face_swap
        - baby_face
        - product-photo-shot
        - style_change
        - style_convert
        - background_remove
        - color_adjustment
        - image_merge
        - dress_trail
        - merge_image
        - other

        🎨 Valid style_slug values include:
        style_Change = [
            "3d", "realistic_style", "angel", "anime_style", "japanese_comics",
            "princess_style", "dreamy", "ink_style", "new_monet_garden", "monets_garden",
            "exquisite_comic", "cyber_machinery", "chinese_style", "romantic", "ugly_clay",
            "cute_doll", "3d_gaming", "animated_movie", "doll"
        ]
        custom-image-generation-v2 = [
            "ghibli-anime", "vintage-cartoon", "simpsons", "disney-animation", "chibi-art",
            "pixar-3d", "funko-pop", "yearbook-portrait", "ukiyo-e", "pop-art", "impressionist",
            "graffiti", "tattoo-art", "post-apocalyptic", "steampunk", "cyberpunk",
            "synthwave", "low-poly", "voxel-art", "claymation", "papercraft"
        ]

        📦 Example return (for a French prompt like "Fais ce selfie en style Pixar"):
        prompt: Turn this selfie into Pixar style.  
        category: style_change  
        style_slug: pixar-3d  
        gender: None
        """

    llm = LLMProvider(platform, llm_model)
    response = llm.generate_response(system_prompt, user_prompt=prompt)
    result_text = response['content']

    # Optionally log
    print("🧠 LLM Classification Response:\n", result_text)

    # Optional: You could extract `prompt:` line here to use as the "translated" prompt
    price = price_calculate(platform, llm_model, prompt, result_text)
    return result_text, price


# --- Routing logic ---
def call_function_by_style(style, gender, style_slug, prompt, image_urls: list[str]):
    print(f"Routing to handler for style: {style}")
    print(f"prompt: {prompt}, image_urls: {image_urls}, style_slug: {style_slug}")
    category_handlers = {
        "face_swap": lambda: face_swap(image_urls[0], image_urls[1]),
        "style_change": lambda: style_change(style_slug, image_urls[0]),
        "style_convert": lambda: image_style_and_color_change(prompt, image_urls[0], image_urls[1]),
        "background_remove": lambda: background_remove(image_urls[0]),
        "color_adjustment": lambda: draw_image_color(image_urls[0], prompt),
        "product-photo-shot": lambda: product_photo_generate(prompt, image_urls[0], image_urls[1]),
        "baby_face": lambda: baby_face(image_urls[0], gender, image_urls[1]),
        "merge_image": lambda: image_merge(prompt,image_urls[0], image_urls[1]),
        "dress_trail": lambda: dress_trial(style_slug, image_urls[0], image_urls[2], image_urls[3]),
        "other": lambda: f"Custom or undefined edit type: {prompt}"
    }
    handler = category_handlers.get(style, lambda: "Unsupported category.")
    
    return handler()

# --- Main image process ---
def image_to_image_process(prompt: str, image_urls: list[str],platform,llm_model):

    result,llm_price = detect_image_edit_type(prompt,platform,llm_model)
    print("Raw Output:\n", result)

    # Robust parsing: handle missing or malformed lines gracefully
    parsed = {}
    for line in result.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            parsed[key.strip()] = value.strip()
    new_prompt = parsed.get("prompt",prompt)
    style = parsed.get("category", "other")
    style_slug = parsed.get("style_slug")
    style_slug = style_slug if style_slug and style_slug.lower() != "none" else None
    gender = parsed.get("gender")
    gender = gender if gender and gender.lower() != "none" else None
    print(f"📊 Parsed → category: {style}, style_slug: {style_slug}, gender: {gender}, llm_price: {llm_price}")

    # --- Call appropriate image handler ---
    output = call_function_by_style(style, gender, style_slug, new_prompt, image_urls)

    # --- Normalize output ---
    if isinstance(output, tuple):
        result_data, model_info = output
    elif isinstance(output, dict) and "model" in output and "output" in output:
        result_data = output["output"]
        model_info = {k: v for k, v in output.items() if k != "output"}
    elif isinstance(output, tuple) and len(output) == 2 and isinstance(output[0], dict) and isinstance(output[1], dict):
        result_data, model_info = output
    else:
        result_data = output
        model_info = None
    # --- Return result ---
    print(f"📊 Output: \n{result_data}"
           f"Model Info:\n {model_info}"
           f"LLM Price:\n {llm_price}")
    return result_data, model_info, llm_price


# --- Run block ---
if __name__ == "__main__":
    platform = "chatgpt"
    llm_model = "gpt-4o"
    prompt = " Convert the first image  like a tiger skin pattern 2nd image like a leopard skin pattern"
    image_urls = [
        "https://storage.googleapis.com/magicpoint/inputs/flux-kontext-input-1.webp",
        "https://storage.googleapis.com/magicpoint/inputs/flux-kontext-input-2.webp"
    ]
    final_result, model_metadata,llm_price= image_to_image_process(prompt, image_urls,platform,llm_model)
    print("\n🟢 Final Result:", final_result)
    print(f"ℹ️ Model Metadata: {model_metadata}")
    print(f"llmprice---------------------{llm_price}")
    

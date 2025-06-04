from openai import OpenAI
import os
from dotenv import load_dotenv
from app.services.image_face_swap import face_swap
from app.services.image_style_change import style_change
from app.services.image_style_convert import image_style_and_color_change
from app.services.baby_face_generate import baby_face
from app.services.background_remove import background_remove
from app.services.blackwhite_to_color_image import draw_image_color

# Load environment and OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Function to detect image edit type ---
def detect_image_edit_type(prompt: str) -> str:
    system_prompt = """
You are an image editing command classifier. Given a user's instruction, return EXACTLY three outputs in this format:

category: <one of the predefined categories>  
style_slug: <one style slug from the list below if applicable, else None>  
gender: <'girl', 'boy', or None based on user prompt>

DO NOT include any explanation or extra characters. Strictly follow this format.

Valid categories:
- face_swap
- baby_face
- style_change
- style_convert
- background_change
- object_removal
- color_adjustment
- image_merge
- dress_trail
- other (if none of the above; return a short description of the custom edit)

Available style_slug options:

style_slug = {
    "style_Change": [
        "3d", "realistic_style", "angel", "anime_style", "japanese_comics",
        "princess_style", "dreamy", "ink_style", "new_monet_garden", "monets_garden",
        "exquisite_comic", "cyber_machinery", "chinese_style", "romantic", "ugly_clay",
        "cute_doll", "3d_gaming", "animated_movie", "doll"
    ],
    "custom-image-generation-v2": [
        "ghibli-anime", "vintage-cartoon", "simpsons", "disney-animation", "chibi-art",
        "pixar-3d", "funko-pop", "yearbook-portrait", "ukiyo-e", "pop-art", "impressionist",
        "graffiti", "tattoo-art", "post-apocalyptic", "steampunk", "cyberpunk",
        "synthwave", "low-poly", "voxel-art", "claymation", "papercraft"
    ]
}

Only return one matching style_slug if applicable. If not applicable, return None.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0,
        max_tokens=50,
    )

    return response.choices[0].message.content.strip().lower()

# --- Central routing handler ---
def call_function_by_style(style, gender, style_slug, prompt, image_urls: list[str]):
    category_handlers = {
        "face_swap": lambda: face_swap(image_urls[0], image_urls[1]),
        "style_change": lambda: style_change(style_slug, image_urls),
        "style_convert": lambda: image_style_and_color_change(prompt, image_urls[0], image_urls[1]),
        "background_change": lambda: background_remove(image_urls[0]),
        "color_adjustment": lambda: draw_image_color(image_urls[0], prompt),
        "baby_face": lambda: baby_face(image_urls[0], gender, image_urls[1]),
        "dress_trail": lambda: "Dress trail effect not yet implemented.",
        "other": lambda: f"Custom or undefined edit type: {prompt}"
    }
    return category_handlers.get(style, lambda: "Unsupported category.")()
if __name__ == "__main__":
    prompt = "make this anime style"
    image_urls = [
        "https://t4.ftcdn.net/jpg/02/14/74/61/240_F_214746128_31JkeaP6rU0NzzzdFC4khGkmqc8noe6h.jpg"
    ]

    result = detect_image_edit_type(prompt)
    print("Raw Output:\n", result)

    parsed = dict(line.split(": ") for line in result.splitlines())
    style = parsed["category"]
    style_slug = parsed["style_slug"] if parsed["style_slug"] != "none" else None
    gender = parsed["gender"] if parsed["gender"] != "none" else None

    print(f"Parsed -> style: {style}, style_slug: {style_slug}, gender: {gender}")

    output = call_function_by_style(style, gender, style_slug, prompt, image_urls)

    if isinstance(output, dict):
        print("Output:", output.get("output", "No result"))
    else:
        print("Output:", output)

from openai import OpenAI
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
from app.agents.chaining_agent import fetch_models
from app.services.fetch_models_info import fetch_models_info
from app.agents.classifier_agent import classify_prompt_agent


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
- background_remove
- color_adjustment
- image_merge
- dress_trail
- merge_image
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

MODEL_NAME_MAP = {
    "face_swap": "face-swap-new",
    "style_change": "bytedance",
    "style_convert": "multi-image-kontext",
    "background_remove": "eachlabs-bg-remover-v1",
    "color_adjustment": "sdxl-controlnet",
    "baby_face": "each-baby",
    "merge_image": "eachlabs-couple",
    "dress_trail": "idm-vton"
}

# --- Central routing handler ---
def call_function_by_style(style, gender, style_slug, prompt, image_urls: list[str]):
    print(image_urls[0])
    category_handlers = {
        "face_swap": lambda: face_swap(image_urls[0], image_urls[1]),
        "style_change": lambda: style_change(style_slug, image_urls[0]),
        "style_convert": lambda: image_style_and_color_change(prompt, image_urls[0], image_urls[1]),
        "background_remove": lambda: background_remove(image_urls[0]),
        "color_adjustment": lambda: draw_image_color(image_urls[0], prompt),
        "baby_face": lambda: baby_face(image_urls[0], gender, image_urls[1]),
        "merge_image": lambda: image_merge(image_urls[0], image_urls[1], prompt),
        "dress_trail": lambda: dress_trial(style_slug,image_urls[0],image_urls[2],image_urls[3]),
        "other": lambda: f"Custom or undefined edit type: {prompt}"
    }
    return category_handlers.get(style, lambda: "Unsupported category.")()

def image_to_image_process(prompt: str, image_urls: list[str]):
    result = detect_image_edit_type(prompt)
    print("Raw Output:\n", result)

    parsed = {}
    for line in result.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            parsed[key.strip()] = value.strip().lower()

    style = parsed.get("category")
    style_slug = parsed.get("style_slug") if parsed.get("style_slug") != "none" else None
    gender = parsed.get("gender") if parsed.get("gender") != "none" else None

    print(f"Parsed -> style: {style}, style_slug: {style_slug}, gender: {gender}")
    
    if not style:
        return {"result": "Unsupported category.", "price": 0.0}

    # 🔥 Get model name and price
    model_name = MODEL_NAME_MAP.get(style)
    models_info = fetch_models_info()
    categories_list = models_info["result"]["result"]["categories"]
    model_category = classify_prompt_agent(prompt, categories_list)
    
    matched_models = fetch_models(prompt, models_info, model_category)
    matched_model = next((m for m in matched_models if m["name"] == model_name), None)
    
    price = matched_model["price"] if matched_model else 0.0

    # 🔄 Call the actual image edit function
    result = call_function_by_style(style, gender, style_slug, prompt, image_urls)

    return {
        "result": result,
        "price": price
    }

if __name__ == "__main__":
    prompt = "image colorizations  of blue color rose"
    image_urls = [
        # "https://storage.googleapis.com/magicpoint/inputs/flux-kontext-input-1.webp",
        # "https://storage.googleapis.com/magicpoint/inputs/flux-kontext-input-2.webp"
        # "https://storage.googleapis.com/1019uploads/68dfc215-c535-4ec5-a625-131fcbc5dec3.png"
        # "https://t4.ftcdn.net/jpg/02/14/74/61/240_F_214746128_31JkeaP6rU0NzzzdFC4khGkmqc8noe6h.jpg",
        # "https://t4.ftcdn.net/jpg/03/37/76/73/240_F_337767352_vgswVhGx5tmc58JFa3CLZDDnb9vTn4sY.jpg"
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAJQBCAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAEAAIDBQYHAQj/xABEEAABAwMCAwUDBwkGBwAAAAABAAIDBAUREiEGMUETIlFhcQeBkRQyQlKhsdEVFiMkM0NiwfAlU3Ky4fEmNGNzgqLi/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwDn0A8lJUEBuUDFP5p01RkFBE+XvleCZCvOo5TmjZBK+TPVJhUeMnCIijQEQlGxAY5ISJmCCiW7BAWwgc+SjqI28whzPjZMfWDGEEUzMFewHOAg56vfZe09S3IJOzuR6H0QXTG5blRSuHLCh+UFrO8SPHO2Fp+F+Crnfw2pkPyWkPKWUbuHkEGZZG+SRrI2ue9xw1rRkk+i3dm9mNxq4BNX1cdFqGRHoL3j13AHxW6snDVq4dYHUkYfUEYM8u7v9FZurM/6IMbF7KaED9YutU8/9NjW/flSx+yqybl9fcXejmDH/qtPLWkDYnKj+WHGo7Y5jxQYy5+yRjmk2u6HlsyqZ1/xN/Bc94h4Iv1oJdVW974+ksI1t+zku8tuGGA6k+O66dw5B8vxxFj3Mc0gjo4EEIoM2XeuKuHbXxVROErI4KtozFUsaA4Hwd4grhzI3MlfDK0CSNxY4A5AIOCgFax2eSJhBCK7DZMDND+SB5j7iBlZurcFmhVdS5uvZAM8IWUot/zT6ISRu6Ad6aGqYxpBm6DyNqc8bKVkeyZI3CAKQd5JOlG6SA/VoTXvTnqJwQPjGrCnDdkPFzCMYNkDWMwQUXGNlE0bqUHG6AiPHVTEN07INsmE4zYBJOPNAyfbKAcJJJmxwsfJI491jAXOd6AbldC4e9m92vtK2prZBbKZ4BZ2jNUj2+Ibkaff8F1OwcN2jh2n7OhpI2vwNc793yHxJ/r3IOacCey19YWXHieN0UQdllCebx4vx9y6tJa7c1kbG0NOGRbMHZju+iJfUaW7O2Kr6muDGuJcPegEuFttNXI11VQ08jmYdksHRSvuQHcaA0DYADACqoHz1bJ/kjHyOMhBIGwx5nZOgtNfI7NXJDTs66nhzvgNvtQFSV+Rg9FB8pDg7JwTuE+SyU7hmO5vDupdFkfDI+9VNzoqmga2TWyaHo6LO3qDyQGumwQdXReGpyOfNUTKmSeQMi/SSOOA1o3KLr6eqomRuqWhuvbY5wfAoDZav9ER4IOWre3ZqBNT11Lxk/PqghulXXyxFlLK+I/Wad89FmaXhGvlgdN2rQ7Bd+kbjV7/ABK2DHN+cV7LUyyt0B3cGyDnkjJIe5LG9jvBwxlQOc1a3iuH+yMMa5+hwc4nfHn4rDdogfPUOVfJLupZnqDCBwdle6U5jML0oIy3ZN0qTUmE4QSxgY3UU2nfCa6TCHkk1HCCKY7pLxwyvUBjykmvT4ygTRuEVFyUOMbqWNwQSrzXhe52UL0CfNhbT2V8M/nDeXVVYNVBREF7T+8k5hp8uvwWFc3fkSegHVfRPs7sv5v8J0sMzNFXOO2nB55PIe4INPK/RsAAB0CraupDASTjKknlxkqhulRmXs2ncjbHigKqa4loEQLnHYAKIwtjZ2tbh7zyizt702Fgt4L55A+dw9zVT3OvdK9wDsBBY1V75siw1rdg1owB6YVW65zuf84481VSVDWg5dy6lU96vjqCASRxjLjhpcg2Da2To5E09UXuHakkA7Ll1qvz66oLa+7miwdttiuiWh1EynbprJapv94XA5+CC0jlp4KjtaeBjJnDHaDmi7gIq+ikgnIbkAtf9Rw6+nT4oWJtBMCGvdG7oQcpklDW9m99O6OqYNy1h73w6qCguNquFCwSyxtlh/vYjqA9fBVhn9611svLGHS489i0/dhe3WwW+7xvmt5bTVhGQG/McfMdCqMkyrxsiaeR0pxvuqqaGakqnQVMZjljOHNPRWVDJvnwQaGhpIdGZmh4bzB3+xGPt9hkikj/ACRSSPmaWvxAAS0+eM5yAchA0TwQ3vfBX9LHTyDIzq+tnqg4XxhY/wAgXZ1OwSmnkaJIHyDvObywT1IOx93iqRoXa/a1bo6rhI1OgOmo5GvY4D5oJDXe7B+wLizCgc1NenEqNxyUDSmOGFO1qZI1AI84XrGat0njvKeFuAga6LupKSYpIGFPjaodSnhQOl+YomE5GxRRZr5p8cAAQMZnHJPazVsvSNJwE9pwgKssLBeaDtG6mfKGZBHPcL6TqnbnPQ9F8zwT9hURTAE9m9r9vI5X0lDUx11DDVwfspmCRpPmEAU5dgkcvBZ10hN9jAALWguI9FeVMmHFZysnZTXESu37SMtz4FAy7VhMh1EZWcq6wDUS7A67qW61rdTiNzlUdvpJeI+IKW0RA9lI8PqHD6MQPfPw29SEF/aKCSsp/wAo1bSKZ2exjIx2v8X+HwWI40qHzXNtMw7MGT6ldi4jfHCwRwsbHGxulrW8mjoPguZW60MvF8ra6sOKCmce0dqwHEDl6IKOy8M1t0GuGNojbnVNKS1m3P19yv6O1Wy2PAl4mbA5p3ELMj45x9iGrLxVXST5JamspaBmWQsb3GgDcvdjPdaN8b9DucKppam3wyjsaB9cR+9qhq1eYbnA+0+aDoVG2olA/Jl1orizqCezcPvGfXCNtXEbRVupZHuhqoz3opdj/t5hYiG5az21rsdqbURAl0UlJpeW9S0tIDvgCpWcQ0V5qGwVsUlBORhrX6ZYQ7xBIDmE+8e9B1OeCgvTT2mIKofNlYN8+Y6hUhqai0VxpakaZGn5wOzweoVFbr4+hrfyfcy5j240uPe2PLfqPA/HdbG60rLvZ3OiH63ANbDjcjq34IKziFkd2oBWQxgVVLu/HN8fX1x+KEslPT1fcxz+kDyTbNXluzzluMOBHMdQobEHUd1fTSD9m4gH6zeh+CC7mo3W+bQ7JDhlrh1CPo5gPmknxx0Vz2MFxozFOAWnljm0+IWedBNRVbqaX57OvMOB5YQXlRBBdbbU0NW3VFUxmNwz0IXzvdLfPa6+qoKkfpqeQscfHwPvGD7136lncx4Ld8cyVyL2nPg/O2pdE7OuNhkA+vj8MIMn0TXHdLUvHb8kDmu3Xj37FMOwUZcUHvM5UzTgIcHdPzsg8kdkpJhO6SD1FwEeKCIOcIiDI5oDmkJ4dsoAV7nZA4uyV6CmgbpwCBwBOwXcOEGVdHwzQ0U5LnRszqByA07gZ8lxBqvbPcb1BEaW31FR2Mrg0tblzWk+fRB2iSm1scQ8EjYgHkVlOIInBpxkFvVH2B1Sx7oZA7VIztHl2xyMA/eprzATC7WM5QcwuMr98+8rTexeNj7rfJTkvZBC0eQc5+f8oWcvsfZudjkrr2MVgi4judJvmopBID/23f8A2g03FzxFqGDkZ6LLxUclNwLJK3nWa5SfInAWl461Mje525LSqq2S9v7O4ZGt70Ebhg9Sx2UGKpC2LhKsLGtE4k7EOHPDtOf68k+y2eV8UM8mlsDnPaSRvtg/zKKkFLarzNSVrHS2uvY2XLDvpO4c0+IyVcRWypihd8gd8up2DLez3dg+LfwQVcbqNzo5IIix+rMU734YSPToheNLOyJ3yyAY3DtvvUUVTCYzTQUzW1GdJiaNwfRG3gvo7I2kncZJw3AHPBOe6PuCDziyF1Zw3RXKMkT0hDC9vMxu2x7nYPxWj9mt/luVGIXyA1dMQHA/Sb0Kr6wRxcP3mhkx+qwGEuH1g0D/ADZWX9n1Q+DiYMjJDZYyHY8jt96DY3lpt9/qoWuABdrAB5B2+PtRlLI2a5xzNG5jwfMgql4qDqe/ukcSW1DQ8evIj+vFFWKbVUA+AwEHS7M8uYMqu4rBhutHKx3zoy1w9D/qjbK4aGjKpuMJnfnBStx3WwAj4lARC8j5r855riXGtQKjim4uYTgSaTnxAC7K2oZHA6WTk0ZOei4Xeahtddqyrjbhk0xe0eXL+SAMFPaV4GpHZAnlRlePevGnKB4SK9CcMII8JKQgJIJOy72cKRrFLpUUztPJB6HDOOqeED2pD0ZA4OCCQFe5XpbgJpKB7Tuuvex3sn2KuaRuKkZ25d3ZcgjPeC6P7Ia58VwrKH6EsXaAeBHX4YQdOnYxvIchzKprtIXxlrR0VlKC7O5z4Kvq49hvug5txBASXE9VQ8PXR/D/ABPQ3Bv7NsgjqG/WicQHfj6gLd32l1l5xt0XPL5SHErAMEtICDs3HFE6ajn0N1FgOR4rK8COFZwhWUWcvie9u/8AEMrc2m+WniKmY2jraeepELHSxNcC5mQM5HrkLP0dnbw3xDMI3/2fctgOkco3x6FBzaF4ulrhtMr2MraSQto5ZXaWlpO8bj033BO3jzXlNc660VToJ2y008Lv0kUmWkH+uo+KZxnSutPE1XEG4jkf2rNuhRNPxAyppIqa5UtNXxxjEZnaRIxv8MgIcPiUBFVxLWTt/wCYfuNw45+3morOHOqTebhpfRW86wHHaaYfMYPQ4cfAAeKDdFw+15l7S54zn5OOz0+nac8f+OUFc7sZ42RQsbBTRNIihjJwwdd+pPUnc9UBslYfzaqe1eXT1dQS4nYk6tTifU/ejvZhbH1V4lqtJDIm6QfMqmtVrrr3DSUlugfKcuLn47jcnmT7l2CwWuh4UsZNVK2OKFuueY9fEoOd+0e66uKoqSHOijh0Ox1c7c/yVzwlE+RjHkYJ3WNudb+dHFdVcIYBHFM8CNg5ho2BPmun8P0RiiboGANkGrtDMLO8ay/8QwtaMmOBrT7yT/Nay3x6GA+KwXEs/acQVcgOGsIaCfIAIA+Lbho4alaHaJJSGNx1zzXK5W6eS0t/uElfUcz2MWzB47bn3qgnagGBCjlOxTjsoZCgicvWFIAkr3CCUHZIFNavcIPS5JeFJBZghCz5KkZICmyYPJAAc68o6l+aonMGVLGNPJBPJJhqhD8leSZKUbdwgIYTkYV3w5d57Nd4K6IZDe7I36zDzVPCwnBRbdgMc0H0AyVssMcsZ1RvaHNI6goeUZcSRss57Or7FWWhltmcG1NJ3W5+mzpj05LVFrXjOeqChrqZ1Rk6d8clQV/DUVcQx2WuwcY6rdOYG8sIGYCnqYp3j9ED3yejepQcspGS8I8TU1yqIZZYIXHV2RwSDkf0F1WsdR8U8POmt1QHxTN/RyN5xvHLPgQUPf7E2sa7YOHpzWOtzbnwjcJJbeztaSR2ZqV5w13mD0KADiGKW5UgNzpWm7UALZonHHas+s0+B/FUdE3hirLRO6vt+eb2kTNH811+CosHETI3ExNn5dlUYbI0+H+yo7r7K7PVPc+kmqKOQnJ7NwLT7jsEFDbeDOFa3DmcUiYfUy1hWnpeBeErZEamoMUjGd8vqZwW4Cz8nsfcWn+1ZHDwMTfwQc3srlGls1bPJG07NzhqDRVvtH4QtbDT0ZknbHyZSw4YfQ8isNfrxfuOZWxspjSW5jsxwDYOPQuPUrT0HA9utpD5IY9fi85J9Mq8o7aZBiGB0UfLU8Yz6BBjuFOHXUbiZW6pM9F0y104jjYNPQc+q9obZFTgdT4lEVlbR2iHt62bRz0M+k/yAQe3m6x2ei7UgGV3djZ4n8AuSXmukllfDl2t7y6U+PVaV01Rfbm6qqnaWjaKMcmDwVLxnTRwVdPpwHOZvjrgoM3LtjAz4oGdrCjZN1W1r9GUFfVYadkE926IkJfuh3tPggcxwTshQjI5p7d0EoXjnYC9CZJyQNL16oSUkB7iRyT43H6ST24TWlBLgHknsamNUgcAg9Ld1KyMYzshzNvgoiJ4LUDw7Tsp4ml5G+ygYwl48EfG3S0ICKKoloamKppnlkkRy1w6LrNpvBmpoJKxrYpJGguGds+S5dZ6OSurY42sJaHAv25Bbesy1pwO6NsINh27ZHd3Tg8kPUtE0RYTseRWGhu9dQygwHMf1H7oocWyukzPTFoHRhyPtQaO0XyKlc23XBoa1ndimJ2x4H+SuZ7fS1g+ic8vBc5uF7t9U3cvDz00FD03E1ZQANoJJJGD906MkfbyQbKq4UjnkwwAeHVTUdrvNFhtNU5iHJjyXD7eSqbPx+HtDLnSPhk5ZZ32/iFc0nGdqnMmZex0H9+NOfMfBAdDSXmTvT3BsQP0Y4mk/Eountz25MtVUy56F2B8BhVLuNbLjaviwq+b2i2yOQtjjqZm4z2jGbA+G5CDTvo4ImSSOa1oAyfx8SucO9qOqsc2ns+qj16WSOm0uLepwAR7sqW9cc1lXTPprZA6m185nnLx44HJZCnoCSBpznchBbXniG53i4SmGomgpc4jijcWjHiccynUVHJM5r5HPkdyBedRHxU1vtbtu6VoqO36GtLRv1QeUUAhYXuGMLEcW1sdXdz2Dw+OOPTqHLKvON7yaCn+RwPxLKN/Jq55HMC/GUB79kBNB2hRkeXDJTi1qCtFG0FPNAHDkEbp3GylacDdBQ1FBpzsg3wFhyFopxqPkhHwAoKUnHNRuKNq4CM4QRGDgoIyknJID5SoWuXjn6l40FARG7KmxlpUDTjop4yCNyggc12pFUuSQF4QCVPAAwoDoWABSncjChjlaG4T2yjKDS8I3Bturg2YgQz91xPQ9Fta6AOb3QDkLlBn7pydlteE+J6eSKOhuMoZKzuskdyePDPigmqKLvY6ryGyufu7kVqmUsUg1luxGQenxUscTGtyOQ5eaCko+G4MFz2hyn/N2Mv5ANV4xw226qaSRrInOaBkAnc4QYTiWK22CmMtQ5plOzYm7uccZHp0Wf4QlffJ5m1L4I2w/pJDggtH8PwVDxTeKm8XiWadscejLGMjdqAA8+qq4Y376XuaDz0kjPqg29bX8Pw1LRDOakEZ1QNy0HwVzHYRPFFU05DoZGh7HY5grnDI9AWr4Z9oUllp22+5UvyqiaMRmMgPj/EINCyyuH7v7FJSUlE2s+TvmibUDGYy7B35Iq18fcNV7CJnyUMg+jMwkH0LcrHce3W03KWluFoqP1mJ/ZvBbpOBuHjyyg6RFQNYRgIDie8U9ht/avIMzu7HGObj+CpaX2kW2ks0TZHTVdxbC0Pwzuufjc59Vz25XCputU+rrZXPkccgZ2Z5DyQMudTNX1ElTO7VI8/DyVczuv3yjmEOGMKCoi0nIQHQyDsspvaICKbSMEqdr9SCczOC8NQeSjIz1URBzzQFCQFLIKFyQnseSUD5ImuB2VXWUzmnICt2lKZgkbuEGZcCDghJWFZSkE4CSCuBKMpwDzSSQPm2Oyj1EHmkkgKi3ARA+akkgjL3A80VTnPNJJBO4YbtsvYImva4EdcL1JBYwXm5W/T8mrZg1g2Y52pvwK2HCvEddcYy6o7LOcd1p/FJJBqhM4saTjJK5p7Sb3XtuItkUzoqUtJe2MkGTph3iPJJJBjWDvH1UzSQdkkkE4ORkoYtDpADyKSSB0bG6c464T3sADvJepIBJGhrdQG+OqlZ+zSSQOiKlkAPNJJAA9oHJSREpJICQvHBJJAx3JKPmEkkBDU87BJJAPV/NSSSQf/Z"
    ]

    # result = detect_image_edit_type(prompt)
    # print("Raw Output:\n", result)

    # parsed = dict(line.split(": ") for line in result.splitlines())
    # style = parsed["category"]
    # style_slug = parsed["style_slug"] if parsed["style_slug"] != "none" else None
    # gender = parsed["gender"] if parsed["gender"] != "none" else None

    # print(f"Parsed -> style: {style}, style_slug: {style_slug}, gender: {gender}")

    # output = call_function_by_style(style, gender, style_slug, prompt, image_urls)

    # if isinstance(output, dict):
    #     print("Output:", output.get("output", "No result"))
    # else:
    #     print("Output:", output)
    output = image_to_image_process(prompt, image_urls)
    print(output)

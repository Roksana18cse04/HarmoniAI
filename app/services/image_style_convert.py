import requests
import os
import time

from openai import OpenAI
from dotenv import load_dotenv
from app.services.image_get_prediction import get_prediction

# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_KEY = os.getenv("EACHLABS_API_KEY")
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
def image_style_enhanche_create_prediction(prompt: str, source_image: str, style_image: str):
    # Get image from user
    response = requests.post(
        "https://api.eachlabs.ai/v1/prediction/",
        headers=HEADERS,
        json={
            "model": "multi-image-kontext",
            "version": "0.0.1",
            "input": {
                "seed": 9999,
                "prompt": prompt,
                "aspect_ratio": "match_input_image",
                "input_image_1": source_image,
                "input_image_2": style_image
            },
            "webhook_url": ""
        }
    )
    prediction = response.json()

    if prediction["status"] != "success":
        raise Exception(f"Prediction failed: {prediction}")

    return prediction["predictionID"]

def image_style_and_color_change(prompt: str, source_image: str, style_image: str):
    try:
        # Define your prompt, source_image, and style_image variables here
        prediction_id = image_style_enhanche_create_prediction(prompt, source_image, style_image)
        print(f"Prediction created: {prediction_id}")
        
        # Get result
        result = get_prediction(prediction_id)
        print(f"Output URL: {result['output']}")
        print(f"Processing time: {result['metrics']['predict_time']}s")
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    # Test the function

    source_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhMSExMWFhUXFRUWFxUTFxoXFxgXFRMWFxUVFRcbHiggGRomHRUXITEhJSkrLi4uFx8zODMsNygtLisBCgoKDQ0OFQ8QFSsdFh0tKzcrLS0rKystKy0tLS03NzUrLisyLSs3Ky0xKy0rNystLisrLTAtLS0rNysrKy0tK//AABEIAJsBRQMBIgACEQEDEQH/xAAcAAEAAgMBAQEAAAAAAAAAAAAABQYDBAcCAQj/xABJEAACAQIDBAYGBQkGBQUAAAABAgMAEQQSIQUGMUETIlFhcZEHMkKBobEUM1JiwSNDU3JzgpKy0RUWg9Lh8KKzwtPxNDVUk5T/xAAWAQEBAQAAAAAAAAAAAAAAAAAAAQL/xAAaEQEBAQADAQAAAAAAAAAAAAAAARESITEC/9oADAMBAAIRAxEAPwDuNKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKV5dwNSQPE2oPVK0pNqwrxlX3G/yrWk3jw49snwU0EtSoZd5sOfaPvFq2ItsxN6rKT2Blv5XvTBI0rXOJP2D5p/mr705/Rt5p/moM9KwfSRzVx+6T8r19+kr3jxVgPMigzUrGmIQ6BlPgRWSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpSgUpWvPigt+69zyFuNz/AL77UGcmo/aG2YohmZgBe12IVb8hc8T3DWqvtbehn0gsV/SsLrx/Nr7fcxsvAgODVP2tKSbszNIRbM2rAHiF+yD9lQBxsKCybV9IaA2jzvoTdB0a6W0LP1xx5IRVWxm+8rarFGP2jPKfMMg+FYelbDllEcTPcgvIgcrkJQqoa4FnEmttdOzWU3a28z4iOKdIpEkOTWGMEE+rbKo52GvbQV6be/Fn1WjX9WGM/wA6sa1m3txoP1q++CD/ALdX30gHBpC0UccHTlkHUjUOg9ZiSBpoLfvVzRouPu/H/Sg3l34xY4rA/wCtFb/lstb+G36Q6TYYgW9aB82vdHJb/mVXZcNa1YGhpo6dgMdHiEP0ebOALmMErIg5kxnW33hde+o3HiRLtqy8zzHiKg9791Ts44ZlmZpWEjF16mRkyZejIOYHrHW/lVs+mMjFMSwIVYD9LChFzYhCyR4lB6rdU/lV6vDMBfNV1Ee0E6qGeIxqTYGW0dz2DORevRxLJa5XX7EiP55GNvfWfeDZcjqqBiDHmyRseqA2W+Q8gcq2Hq8LWub09p2RirAgjiDp86Yq5w7VbhmbzNTUD4pRcJOB3Bx8BXOYcd312XdPa4xWGWQnrr1JP1lA194IPvqIgxtzEKfrmU/ZkRWHvFg3/FUhhd7ZVt0sAkGnXw7dbvJicjQfddj3VPYjIbK+U34K9tfAGo/FbvRN6oMZ+7w96n8LUNSGyNu4fEg9DKrFfWQ3WRO6SNgHQ+IFSNc523uqxszKWZfUmgJSZO9WXrDwFx21p4PezH4P64fTsOPbQBMUgF/WUdWW2g0AJ1JtRXUqVDbub04XGrmw8qsbXKHSRf1kOtu8ad9TNApSlApSlApSlApSlApSlApSlApSlApSlApSlArHNOq8Tx4DiT4DnWSoYM7yM+ojtYA6ZjcWIB1AFiNbXvpcG9BtmcsDfqDkGNmPeewd1Q+18GsqhHa6g3Kq4UNYaBxY5lHEDhex4gWzSxD/AM1gfCAg6VURU2AhB/OfuyJ/krQk2TCX6TppQ4IYEhHsQbg8ueutTmIwEQ9ZlW/AswUeFzzrANlKwurXHcb1cggMRu/nAH0oNYWBeEA2LFjqpY8ST7zWkN1ZlYNHNFcagqzIwPaCyix99Wh9jtyNYG2dIKZBUZt2cXckpn46pIjkk9ysTeo3EbHnS+eCVRfi0bKOA5kVe2gkHbXxJZF4XHhp8qcTXNGiPCt3ZceFUlsTMkZBGRHbJm5lr9g00vz87/JjpDo/WHZIM48mvWhjMLh5BaXCwOOwxqv8gFMNbJ21s2YBpcfE7AG+ZlYAHiNToNKgN6N4oUjxCQPDi451jzsjqWjaFQI+BsLBMwB+w1aG8e7eFkgkEGGWKULdGjZrZhqFILEEHh7+6qfubu++IaUOssaFbF7ZdSbFespubch2a1Lot+6e8gCLHKS0V7K3F4dbgAe1Hr6nLivMNZdo7KjlKl1ViMrq3rI68VvYjPGe4jQnUa1D7J3TiiRlSZWDgazQjMOrYEMj99+HId95fYOz5YwYXkiaHUqQzBo2Ot1DIBlY+st+8a3ugrm2tjSviJZEhc9I7PlhKsoLG7AFrHiTyqZ3dg2hhRIIsLN+UUA5zF1SL2dQX4i543HdUmT/AE8q2MPj5E9WRh3XuP4TpV4mtGLZ2MKMrbPDM1800rRPKSeYZpSAfADz1rMmzNo//Hm980X/AHKl4d45R6wR/dlPmNPhUlht54z6ysvgQw/CplEHBFtKPUQzeBkiceRkIrBjI8TI+dsMyuQAbPEASOZHScbfIVeMPtSN/VceB0+dbJkBGouPMUHIdq7lySt00StBiAbiVHQXNrdbI97/AHhZu88Knd2NubZi6mMwnToNOkSWAS27fXCuPHKe0mr40ER9m3hp8qxNs9fZcjxsaDaw2LVwDqp+y2hHd2eRNZ6iWwcg4WbwNj8a89K6cQw+X9KKmKVGRbQPaD46HzH9K20xinjp4/14VBsUr4DevtApSlApSlApSlApSlApSlApSlB4lawJ/wB91aWOmSNHdyAiqSxbQAAXJYngLC9+6vO8EuWBjcLqmpNrdcHj7q5D6Vd6ppMCuHFgZpFjYrpmHrHwGgBHefCqNTbXprHSlcLhg8YNg8hKlgOaoo6o7Lm/cOFWbcz0ixY68bJ0UttUJv3XU8xr4jstrXLY9kLhsGmKkcJG7hECqGlkuL9K1/VQgMVHMDiNL+du7Ilwc0Uqlc+VZY3X1XVgDYi+hsbMlza/Egglo77itoquh1PMD8a1U2ui+qluelhr26VWtmbRE8Ucq366hteIuNQe8HQ94rcEDHkfI1rETo24vY3w/rWRdtRntHiKrrREcQa8ZTTBZl2lGb9a2vZ90VhWQkj8rEw5jKVPxZqrovr/AL5V9zmmC3dDG3IVhfZsZ5VVxMRWVMcw9o+Zpgm22EhrDidj2U2NuCjxZgo+JFaKbWkHtedq9YjbTZRe31kXwmSnY2DsRhwrE+zHHKt+DbN+I8qk4ZwwvpbtoKq+FcHhx+dehs+XkjfL51BekH0mR4Rjh8MqyTi2Z21ji5209Z+69hzvqK5lPvptWY5ji5h+zYRL5IAKnIx2h8K6+spHiPxr0uFY8q5jsP0i7SgP5VkxMfNJbB7c8sgAN/1sw7q6fu/vPFi41aKR7k5WhI6PI9tI7g5gSASOsQ1jY3GUL956SW+MiYKTkG9wNZ4554+TD3EVG7f2U8l3illV9D0cs0jxEjszE5PIg9nE1Qdo4/EwYg5ouiFgAuIYsrEDVkeMxq17cuFNHXYd4WGjrf5+YqQw+2I29rKfvcPOuS7Y25iMK0S4mEgyRrKpgxDZcrdqMrajsufE1tHbrKEJkcGQXVGiie3IZhG4cAk6XXXXsNOh1s4ojw7RqPOva47vrmGB3nyHK0+HJvYqrSRsCDazJIvVPcTW4++0COEZ48xFxlkZ14kWLJGyg6cCag6E4jbiov2jQ/CteXCkC6P58f6Hw08Rxqmf38w68Xj/APsP4oK9pv8A4c8GXzVv+sUFqTElTbUH/fKt6Haf2hp2iqX/AHwibgyX7WhY/FJq8PvIO0f4ccw/mjkFB0hGBFxwr1VD3Q3xSSY4dmN79Uta57b2VbEachp8b5UUpSlApSlApSlApSlApSlBCb63GBxDAE5E6QgC5KxkOwA7cqm1cJ36s/0QhgVYyMrKbggqoDA/vV+j3QEEEXBFiDwIPEGvz7vT6N8TgJFnVunwEUpcLezQo7qSjKeINlGYHtJAuaoq0+1Gx6FJOq6RrHk4BUjAETKOQAChgOy/tG2aTbBaIYNgD15cQjHityB0YN/VssrHtunZV0/smOOVbxxQlnYQhIY4nbJeQMmUNKoUJq7MvC6hritDb+yIgJ55OtJ0UzLMpKs8lzGwkFsrjMSDwZTk4h1tBh3Ax35OWIH6uS6jsWQZrfxZ6vUO8Uo45W8RY/C1co3Ax0aTz9JIqBkWxYgAsGPaddCeFdLw2AEqLJFIjo3BlYW+PPurcRNRbzp7UZH6pB+BtWym1cK/Egfrp+IBFVx9kyj2SfDX5VrPhXHEEVcFvjw0El8rKdfZYdg5XrzLsQciR4iqb0Z7KzQ4uRPVdh4MQPKiJ+bY7jhY+H+taUuFI4gjxFYotvzjiwP6yj5jWtpN4ydHjU+BI+d6djTMZrXxYOX9+P4SoakpNowt7LKfcR871q4l0IFm9pOOnBwfwoPqSVo72bwNhcJI6nXQKPvt1VPuvf8AdraktyNUj0jS5vo8Z4F2c/4agD4vUqqRhMJweS7yOdF1ZizHmOJYk/HtqzYvdqaLCDGYg5I8yjo4gryAOOqzksFUarwzHrjQVg3d25Dg5o55o+kLhwut+iTVDIBzLNmXuCt9qvG1MdJK5Mj5w65SVNkkjZiRIBwDhmLHvJ5MBWFaGEkgldI0aZXdlVcwjkuWbKoKgoRr3mpmXC4nZeJVpVFj1S0bXjmS4LIG0KuNGFwCCFNiONd2VCY3zC2eLNY8sxAEZ/VsS3gpq6YLbkS4eUY28kWQoA5Jkke9+qSdCDc35GxvZEtLJZlWXO47DsfErNBHLmVw6hg6+0D6rEciRa45G9ZMRgUcFWUMp4qwBB8QdDXNvRftbLG8CksqESRFrXMU1zY2PrK6uGt7RNdCg2iDx0rUmRLdqC2xuHhZ2zkMj2Chkc6KOACtdbDstVaPo5xUL9JhcQGIIZc35NwRwsdUPwFdPVwa0MRvJhIiVedcw4hbuR3HIDb30Rw/bmAxsLO+LhdSz9I0siggsSST0q3WxLE5QezTQW1No7dknKNLd0RMqBQiIqjsAsov3dgrvC76YI6CYHxRwPfdarO2NkbOxDdJBMmGnBuskDBOtrq0dxfjxXKT20VzbDbawoAvC7HmRiY0F+5egYj+I1IQ7dhPq4Vm8cQzfyxitrbKbUwx/KYmcx/po5pGjt2sR1l8CPC9azY7Ekf+7j/9GN/CI1BtR42Rvq9nE+H0pv5XFS+NixTPmGAADokhLwyWVnQGRT0rFVs+cBbaC1VzOW+s2mCOy+Mf+aJRWXErgwIM2LZyImXLHApa/wBJnf25VYHr8LHSx50E1HLKhV3OHQoykLH9HDXZguUrD1ra6g6V2vZGLEsSt2qDr3i4riWA2IJAtopYorqxmxJCEhTmtFCFDsxKgcxYnWr/AOjrbDYmbFBRaCDLCL85FJuALcQALm/tAW01C90pSgUpSgUpSgUpSgUpSgVp7Z2euIgmgfRZY3jJ5jOpFx3i9/dW5Xwi9B+eNgRPFi8QZs3SxxsgzOWEcgxEQkUKdSHXN1hpblYgmP3v21IPpcIZlhkmbJE1r9VxmktxAOQW7Q3DS57Bvr6OkxrdNHMYJrAFsgdXA4B0uLkcAwN7aagC3PMd6EMezEjFYdu9hIp8gDbzoOPzi9S+zoJo1BVcZETrmhDZT3gDL866HhfQfjEYM8sD21yjMQfEEC47qnpdxsd7Uo9ymg5tFvNjIbD6dMh7MRDr7yQ1S+E9IuPFhnwkvaCWUnzIA8qseI3LxXNr+6ovF7nTe0obxANBmg9I0n53Z4I5mKRXPkB+NbSekDAH62DEQ97Jp8CflVZn3TdfzdvAEfKtR9jSrwMg8GP43q6L9h95NlS+rilX9oCn8wFSUGHglF4cRE4+66n5E1ySfAye1Zv10VvjatKXZ/bDGfDMnwBt8KcqmO1vsVxwrSxOBdcuntD5E/IGuSQSyx/VviYuwQzkAeA0PxqRj3v2ggsMbKf28SyebEOTV5GOktGw5VSt/wAHPAfuyj4xVpn0j4tR1xhpRzKqyN5Ar/LUdtrev6YYwYujK5tQ2YHMB3C2qilvQ84vdvEyiOUIOiMUOV2ljVbGJSRYm46xatrodWK9DksSY4pc4zBTbKyoVQkixJNtdaldmKJ8Kmc4f8icl8T9Win2iCGvpYdUpcrbW1ff7UTpFiwgOLmLKoklBiw6EmwyQg9JKv7ViNPVNZVrnZq2WzsWugIyotrtkBU3uPW0LXD2OUWNqjMZsTEuOlELSKt1Aw2SZI0FwFTIxIOgvcA8avO0IY4Y8RJGhkEAxHVeVxnSDFLhpM0gOc3EjupLHKVS3CsTYFJo1xWHPTJa90YQ42AXsdVKCZFJy9Upa92VjrQV7cF2injVldc30iICRcrZcscqqfAh/wCM10pcRaqJisaxxmCRiSUJuTqT0i5bk2W5so9kcan9ubR6CCWXiUUkD7x0W/dcitRKit899mjcYSAjpCQHc3yoG5G2vDU2/qKrGKxeJPUjBCgEZy8ayOftkhvyfcqWAFr5jdjXNnoZGkkZZJCxs3Ri7Xe5Zr2PG1v3jUvgt3jIQqYTF+LZUH8TJap6qf2XjcRGtiS1zr0s6sb/AHWMmnl7quOz4TJlHXuxAsoeSxP2jHmAH3jYd9Yt0PR7JA4nVo0kCkLntOFJHEDo015XBBsSLi9XLbO80eEjQTyrnYW6oy9Iw0JRCxyrfiSbDgTwBRGthd3Wi/OBBqTbv1b+tQG1Nu7JjJWbEwSEaG0KzfFUb51SN+985p80YYIL26PMB+8/2jzF9Odq5+sGurL5k/IGmjrWJ3s2Ev5kSH7mDhH8wWsI9J+Bh/8AT4Fwe4RQfGME1ypYVvYvr3KT87VI4TZDucyxTOONwuVR2AtqKaq9j0pyMWZcJCqrqxYtK9rgE5tBcXHEeVdn9HPRnBiSI3WWSWW3Jc7khVtyAtbtvc6k1wjYW4ONlChMMQpFiSxsbm9iw6vIcbWsK7j6M92Ztn4QwTSByXLgKNEBAGW99eFQW6lKUClKUClKUClKUClKUClKUClKUClKUHlkB4gVhkwUZ4qK2KUEZLsSI8q0MRutGeyrFSgpOJ3KU+yKh8XuIPs106lBxnFbidgqIxO5LDgK7y0KniKwSbOQ8qD884ndFx7N6i591iNcnkLV+jZ9gqeFvKovF7qk8MpoPzhicOULQyg5Wse/T1XXvFz5kaXvU56PB9H2hFI6Zo7sWZL5RlGdSo9klgBlPAXtoa6PvJuHJKhVoS3NWQjMp7V/pzrmGN3d2hhXsMPiGA4OkMo07CQNPcaC04LaQjgkMoz5cAxkHAmd5YcQyeStr3VznAxvdJAzxopzKwOUnqgWQcyRYF7W056AyL43FLcGKdb2vdJAdBbsvwFaMuHxMh+plP8AhsPMkUGHa20GkdnJsSb3GmvK3Z/pWfZ+1Z0uDJ0iMLNHMc6sp7ibj3V7g3cnOrQue7KQP9a3f7vTnUxnyoM+7m21wbO8CsgksHjYCeM5b2sSUYWubanjzqyr6RBziue5QP8Aqqq/3cn+wfKvo3an+wfKrotmI9KM2QrEiKTzZb277BtT8PHhVPm2iJGLzIJpD60kjyEns6qsoAHAAaDlWdN1MQfYPlWzDuPim9g+VQQzYheWGgPPrdKR5NKRXqKWU6KmGTwgjPxZTVqwvo1xLcb+VWDZ3opk0LX99Bk3MxmGVEWeFWcAXdHdAT25FIQe4V03ZU2ENjHEityOUX/i41Xdlej0R2uRVqwOw44++glAa+18UWr7QKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQKUpQfCKxth1PFR5VlpQaxwER9hfKvB2XD+jXyrcpQaf9lQ/o18q+jZsP6NfKtulBgXBxjgi+QrIsSjgo8q90oAFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoFKUoP/9k="
    style_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJQAAACUCAMAAABC4vDmAAAAA1BMVEV4hmtKIYMvAAAALElEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgZViQAAd2fpbUAAAAASUVORK5CYII="

    prompt = (
    f"Apply the pattern, texture, and colors from the style image ({style_image}) and {source_image} image color glossyfiber as a high-quality custom wrap on the car in the source image ({source_image}). "
    f"The entire vehicle surface — including the hood, roof, doors, and sides — should be wrapped fully in the style. "
    f"Preserve all reflections, lighting, and surface contours of the car for realism. "
    f"The wrap should appear vivid, glossy, and metallic. Do not change the background — only apply the style to the car body."
)



    result = image_style_and_color_change(prompt, source_image, style_image)
    print(f"car new ------>",result)
    
    
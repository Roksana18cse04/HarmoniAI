import json
import re

def extract_json_from_llm(raw):
    """
    Attempts to extract JSON from LLM output.
    - If raw is a dict, return it.
    - If wrapped in ```json ... ```, unwrap it.
    - If full JSON parse fails on array, tries to recover partial objects.
    - If it doesn't look like JSON, returns as plain text.
    """
    # Already a dict?
    if isinstance(raw, dict):
        return raw

    if not isinstance(raw, str):
        raise TypeError("LLM response must be a string or dict.")

    raw = raw.strip()

    # Remove markdown fences ```json ... ```
    cleaned = re.sub(r"^```json\s*|^```|```$", "", raw, flags=re.MULTILINE).strip()

    # Try full JSON parse (object or array)
    if cleaned.startswith("{") or cleaned.startswith("["):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass  # Will try recovery if array

    # If looks like a JSON array but full parse failed, try partial recovery
    if cleaned.startswith("["):
        try:
            # Extract JSON objects inside array (non-greedy)
            objects = re.findall(r'\{.*?\}', cleaned, re.DOTALL)

            valid_items = []
            for obj in objects:
                try:
                    valid_items.append(json.loads(obj))
                except json.JSONDecodeError:
                    # Skip broken objects
                    continue

            return valid_items
        except Exception as e:
            raise ValueError(f"Failed to extract partial JSON objects: {e}")

    # Otherwise, return cleaned string (not JSON)
    return cleaned

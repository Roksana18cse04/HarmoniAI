import requests
import ijson

url = "https://cdn.harmoniai.net/omuz.n_contents.json"

# Stream the HTTP response to avoid loading the full content into memory
with requests.get(url, stream=True) as response:
    response.raise_for_status()

    # Use ijson to parse each item in the top-level JSON array
    items = ijson.items(response.raw, 'item')  # assumes it's a JSON array: [ {...}, {...}, ... ]

    # Read the first 5 items
    first_5 = []
    for i, item in enumerate(items):
        first_5.append(item)
        if i == 4:
            break

    print(first_5)

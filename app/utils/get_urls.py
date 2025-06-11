from app.utils.r2_uploader import upload_to_r2
from app.config import config
from pathlib import Path
import os
import json

def get(filename):
    Remzi_dir = os.path.join(Path(config.BASE_DIR).parent, "Remzi")
    file_path = os.path.join(Remzi_dir, filename)

    with open(file_path, 'r', encoding='utf-8') as f:
        file_dict = json.load(f)
        file_bytes = json.dumps(file_dict, ensure_ascii=False).encode("utf-8")  # convert to bytes

    res = upload_to_r2(file_bytes, object_key=filename)
    print(res)
    return res

files= [
    "omuz.comments.json",
    "omuz.event_cities.json",
    "omuz.event_place_categories.json",
    "omuz.event_places_new.json",
    "omuz.follows.json",
    "omuz.n_categories.json",
    "omuz.n_event_categories.json",
    "omuz.n_events.json",
    "omuz.n_persons.json",
    "omuz.rates.json",
    "omuz.rates_bulk.json",
    "users.json",
    "omuz.n_contents.json"

]
urls=[]
for file in files:
    print(file)
    res= get(file)
    urls.append( res )
print(urls)


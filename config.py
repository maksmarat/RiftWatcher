import json
import os

PATH = "data/config.json"

def load_config():
    if not os.path.exists(PATH):
        return {}
    with open(PATH) as f:
        return json.load(f)

def save_config(data):
    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)
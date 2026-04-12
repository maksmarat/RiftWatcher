import os

PATH = "data/players.txt"

def load_players():
    if not os.path.exists(PATH):
        return []
    with open(PATH) as f:
        return [line.strip() for line in f if line.strip()]
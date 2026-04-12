def parse_riot_id(nickname: str):
    try:
        return nickname.split("#")
    except:
        return None, None


def format_game_time(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes + 2}:{sec:02d}"
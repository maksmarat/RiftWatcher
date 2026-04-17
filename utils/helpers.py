from datetime import datetime

QUEUE_ID_LABELS: dict[int, str] = {
    400: "Normal Draft",
    420: "Solo Queue",
    430: "Normal Blind",
    440: "Flex",
    450: "ARAM",
    480: "Swiftplay",
    490: "Quickplay",
    700: "Clash",
    720: "ARAM Clash",
    740: "Clash",
    870: "Co-op vs AI Intro",
    880: "Co-op vs AI Beginner",
    890: "Co-op vs AI Intermediate",
    900: "ARURF",
    1900: "Pick URF",
    1700: "Arena",
    1710: "Arena",
}

QUEUE_FILTER_IDS: dict[str, set[int]] = {
    "all": set(),
    "soloqueue": {420},
    "flex": {440},
    "arena": {1700, 1710},
    "normal": {400, 430, 480, 490},
    "aram": {450},
}

RANKED_QUEUE_TYPE_BY_ID: dict[int, str] = {
    420: "RANKED_SOLO_5x5",
    440: "RANKED_FLEX_SR",
}

RANKED_QUEUE_LABELS: dict[str, str] = {
    "RANKED_SOLO_5x5": "Solo Queue",
    "RANKED_FLEX_SR": "Flex",
}


def parse_riot_id(nickname: str):
    if not isinstance(nickname, str):
        return None, None

    value = nickname.strip()
    if value.count("#") != 1:
        return None, None

    game_name, tag_line = (part.strip() for part in value.split("#", 1))
    if not game_name or not tag_line:
        return None, None

    return game_name, tag_line


def format_match_age(timestamp_ms: int | float | None) -> str:
    if not timestamp_ms:
        return "Неизвестно"

    try:
        match_dt = datetime.fromtimestamp(int(timestamp_ms) / 1000)
    except Exception:
        return "Неизвестно"

    days_ago = (datetime.now().date() - match_dt.date()).days

    time_text = f"{match_dt.hour}:{match_dt.minute:02d}"

    if days_ago <= 0:
        return f"сегодня в {time_text}"
    if days_ago == 1:
        return f"вчера в {time_text}"
    if days_ago == 2:
        return f"позавчера в {time_text}"
    if days_ago <= 10:
        return f"неделю назад в {time_text}"
    if days_ago <= 24:
        return f"две недели назад в {time_text}"
    if days_ago <= 45:
        return f"месяц назад в {time_text}"

    return f"{match_dt.strftime('%d.%m.%Y')} в {time_text}"


def get_queue_display_name(queue_id: int | None) -> str:
    if queue_id is None:
        return "Unknown Queue"

    try:
        normalized_queue_id = int(queue_id)
    except (TypeError, ValueError):
        return "Unknown Queue"

    return QUEUE_ID_LABELS.get(normalized_queue_id, f"Queue {normalized_queue_id}")


def queue_matches_filter(queue_id: int | None, queue_filter: str) -> bool:
    allowed_ids = QUEUE_FILTER_IDS.get(queue_filter, set())
    if not allowed_ids:
        return True

    try:
        normalized_queue_id = int(queue_id) if queue_id is not None else None
    except (TypeError, ValueError):
        return False

    return normalized_queue_id in allowed_ids


def get_ranked_queue_type(queue_id: int | None) -> str | None:
    try:
        normalized_queue_id = int(queue_id) if queue_id is not None else None
    except (TypeError, ValueError):
        return None

    if normalized_queue_id is None:
        return None

    return RANKED_QUEUE_TYPE_BY_ID.get(normalized_queue_id)


def get_ranked_queue_label(queue_type: str | None) -> str | None:
    if not queue_type:
        return None

    return RANKED_QUEUE_LABELS.get(queue_type, queue_type)


def get_ranked_entry_for_queue(
    ranked_entries: list[dict] | None,
    queue_type: str,
) -> dict | None:
    if not ranked_entries:
        return None

    return next(
        (
            entry for entry in ranked_entries
            if entry.get("queueType") == queue_type
        ),
        None,
    )


def format_rank_entry(
    ranked_entry: dict | None,
    *,
    include_record: bool = False,
    unranked_text: str | None = "Unranked",
) -> str | None:
    if not ranked_entry:
        return unranked_text

    tier = str(ranked_entry.get("tier") or "").title()
    rank = str(ranked_entry.get("rank") or "").strip()

    try:
        league_points = int(ranked_entry.get("leaguePoints", 0) or 0)
    except (TypeError, ValueError):
        league_points = 0

    parts = []
    if tier:
        parts.append(tier)
    if rank:
        parts.append(rank)
    parts.append(f"{league_points} LP")

    text = " ".join(parts).strip()
    if not text:
        return unranked_text

    if not include_record:
        return text

    try:
        wins = int(ranked_entry.get("wins", 0) or 0)
    except (TypeError, ValueError):
        wins = 0

    try:
        losses = int(ranked_entry.get("losses", 0) or 0)
    except (TypeError, ValueError):
        losses = 0

    return f"{text} ({wins}W/{losses}L)"


def format_game_time(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes + 2}:{sec:02d}"

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class RecordDefinition:
    key: str
    label: str
    extractor: Callable[[dict], float | int]
    formatter: Callable[[float | int], str] | None = None


def default_formatter(value: float | int) -> str:
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def get_challenges_value(participant: dict, field: str, default: float = 0) -> float:
    return participant.get("challenges", {}).get(field, default)


RECORD_DEFINITIONS: list[RecordDefinition] = [
    RecordDefinition(
        key="kills",
        label="🔥 Топ киллов",
        extractor=lambda p: p.get("kills", 0),
    ),
    RecordDefinition(
        key="deaths",
        label="💀 Топ смертей",
        extractor=lambda p: p.get("deaths", 0),
    ),
    RecordDefinition(
        key="question_pings",
        label="❓ Топ пингов вопроса",
        extractor=lambda p: p.get("enemyMissingPings", 0),
    ),
    RecordDefinition(
        key="objectives",
        label="🐉 Топ забранных объектов",
        extractor=lambda p: p.get("dragonKills", 0) + p.get("baronKills", 0),
    ),
    RecordDefinition(
        key="vision",
        label="👁️ Топ контроля",
        extractor=lambda p: p.get("visionScore", 0),
    ),
    RecordDefinition(
        key="gpm",
        label="💰 Топ GPM",
        extractor=lambda p: get_challenges_value(p, "goldPerMinute", 0),
        formatter=lambda v: f"{float(v):.0f}",
    ),
    RecordDefinition(
        key="kill_streak",
        label="⚔️ Топ стрик убийств",
        extractor=lambda p: p.get("largestKillingSpree", 0),
    ),
]
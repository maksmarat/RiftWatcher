from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ROLE_ALIASES = {
    "TOP": "TOP",
    "JUNGLE": "JUNGLE",
    "MIDDLE": "MIDDLE",
    "MID": "MIDDLE",
    "BOTTOM": "BOTTOM",
    "BOT": "BOTTOM",
    "ADC": "BOTTOM",
    "UTILITY": "UTILITY",
    "SUPPORT": "UTILITY",
    "SUP": "UTILITY",
}

ROLE_SHORT_LABELS = {
    "TOP": "TOP",
    "JUNGLE": "JGL",
    "MIDDLE": "MID",
    "BOTTOM": "BOT",
    "UTILITY": "SUP",
    "FLEX": "FLEX",
}

ENGAGE_SUPPORT_CHAMPIONS = {
    "Alistar",
    "Amumu",
    "Blitzcrank",
    "Braum",
    "Leona",
    "Maokai",
    "Nautilus",
    "Pyke",
    "Rakan",
    "Rell",
    "Taric",
    "Thresh",
}

ENCHANTER_SUPPORT_CHAMPIONS = {
    "Janna",
    "Karma",
    "Lulu",
    "Milio",
    "Nami",
    "Renata",
    "Seraphine",
    "Sona",
    "Soraka",
    "Yuumi",
    "Zilean",
}

MAGE_SUPPORT_CHAMPIONS = {
    "Brand",
    "Hwei",
    "Lux",
    "Morgana",
    "Neeko",
    "Swain",
    "Velkoz",
    "Xerath",
    "Zyra",
}

CONTROL_MAGE_CHAMPIONS = {
    "Anivia",
    "Annie",
    "AurelionSol",
    "Aurora",
    "Azir",
    "Cassiopeia",
    "Galio",
    "Hwei",
    "Lissandra",
    "Lux",
    "Malzahar",
    "Mel",
    "Orianna",
    "Ryze",
    "Seraphine",
    "Syndra",
    "Taliyah",
    "TwistedFate",
    "Veigar",
    "Velkoz",
    "Vex",
    "Viktor",
    "Xerath",
    "Ziggs",
    "Zoe",
}

ASSASSIN_MID_CHAMPIONS = {
    "Akali",
    "Ahri",
    "Akshan",
    "Diana",
    "Ekko",
    "Fizz",
    "Katarina",
    "Kassadin",
    "Leblanc",
    "Naafiri",
    "Qiyana",
    "Sylas",
    "Talon",
    "Yasuo",
    "Yone",
    "Zed",
}

SCALING_MID_CHAMPIONS = {
    "Azir",
    "Cassiopeia",
    "Hwei",
    "Kassadin",
    "Orianna",
    "Ryze",
    "Smolder",
    "Syndra",
    "Veigar",
    "Viktor",
}

TANK_TOP_CHAMPIONS = {
    "Chogath",
    "DrMundo",
    "KSante",
    "Malphite",
    "Maokai",
    "Ornn",
    "Poppy",
    "Rammus",
    "Shen",
    "Sion",
    "TahmKench",
    "Zac",
}

SPLIT_PUSH_TOP_CHAMPIONS = {
    "Camille",
    "Fiora",
    "Gangplank",
    "Gwen",
    "Illaoi",
    "Jax",
    "Nasus",
    "Quinn",
    "Riven",
    "Tryndamere",
    "Urgot",
    "Yorick",
}

OBJECTIVE_JUNGLE_CHAMPIONS = {
    "Amumu",
    "FiddleSticks",
    "Hecarim",
    "Ivern",
    "JarvanIV",
    "Nunu",
    "Sejuani",
    "Shyvana",
    "Skarner",
    "Trundle",
    "Udyr",
    "Vi",
    "Volibear",
    "Warwick",
    "XinZhao",
}

CARRY_JUNGLE_CHAMPIONS = {
    "Belveth",
    "Briar",
    "Diana",
    "Ekko",
    "Elise",
    "Evelynn",
    "Graves",
    "Karthus",
    "Kayn",
    "Khazix",
    "Kindred",
    "Lillia",
    "MasterYi",
    "Nidalee",
    "Nocturne",
    "Rengar",
    "Viego",
}

FACILITATOR_JUNGLE_CHAMPIONS = {
    "Amumu",
    "Ivern",
    "JarvanIV",
    "Maokai",
    "Nunu",
    "Poppy",
    "Rammus",
    "Sejuani",
    "Vi",
    "Zac",
}

HYPERCARRY_BOTTOM_CHAMPIONS = {
    "Aphelios",
    "Caitlyn",
    "Draven",
    "Jinx",
    "Kaisa",
    "Kalista",
    "KogMaw",
    "Lucian",
    "Samira",
    "Smolder",
    "Tristana",
    "Twitch",
    "Vayne",
    "Xayah",
    "Zeri",
}

UTILITY_BOTTOM_CHAMPIONS = {
    "Ashe",
    "Ezreal",
    "Jhin",
    "Nilah",
    "Senna",
    "Seraphine",
    "Sivir",
    "Varus",
    "Veigar",
    "Ziggs",
}

PROFILE_LABELS = {
    "top_frontline": "frontline top",
    "top_splitpush": "splitpush top",
    "top_bruiser": "carry top",
    "jungle_objective": "objective jungle",
    "jungle_carry": "carry jungle",
    "jungle_facilitator": "facilitator jungle",
    "mid_control": "control mid",
    "mid_assassin": "assassin mid",
    "mid_scaling": "scaling mid",
    "mid_roamer": "roaming mid",
    "bottom_hypercarry": "hypercarry bot",
    "bottom_utility": "utility bot",
    "bottom_teamfight": "teamfight bot",
    "support_engage": "engage support",
    "support_enchanter": "enchanter support",
    "support_mage": "mage support",
    "support_roamer": "roaming support",
    "flex_carry": "all-round carry",
    "flex_frontline": "frontline flex",
    "flex_support": "battle support",
}

PROFILE_WEIGHTS = {
    "top_frontline": {
        "efficiency": 0.09,
        "presence": 0.08,
        "damage": 0.10,
        "economy": 0.08,
        "vision": 0.06,
        "utility": 0.16,
        "tank": 0.23,
        "objectives": 0.10,
        "playmaking": 0.08,
        "mechanics": 0.02,
    },
    "top_splitpush": {
        "efficiency": 0.12,
        "presence": 0.04,
        "damage": 0.11,
        "economy": 0.19,
        "vision": 0.03,
        "utility": 0.05,
        "tank": 0.09,
        "objectives": 0.20,
        "playmaking": 0.12,
        "mechanics": 0.05,
    },
    "top_bruiser": {
        "efficiency": 0.12,
        "presence": 0.08,
        "damage": 0.16,
        "economy": 0.14,
        "vision": 0.04,
        "utility": 0.08,
        "tank": 0.12,
        "objectives": 0.12,
        "playmaking": 0.10,
        "mechanics": 0.04,
    },
    "jungle_objective": {
        "efficiency": 0.10,
        "presence": 0.15,
        "damage": 0.10,
        "economy": 0.05,
        "vision": 0.12,
        "utility": 0.08,
        "tank": 0.08,
        "objectives": 0.22,
        "playmaking": 0.07,
        "mechanics": 0.03,
    },
    "jungle_carry": {
        "efficiency": 0.12,
        "presence": 0.14,
        "damage": 0.18,
        "economy": 0.09,
        "vision": 0.06,
        "utility": 0.05,
        "tank": 0.05,
        "objectives": 0.17,
        "playmaking": 0.11,
        "mechanics": 0.03,
    },
    "jungle_facilitator": {
        "efficiency": 0.08,
        "presence": 0.17,
        "damage": 0.08,
        "economy": 0.04,
        "vision": 0.12,
        "utility": 0.13,
        "tank": 0.10,
        "objectives": 0.18,
        "playmaking": 0.08,
        "mechanics": 0.02,
    },
    "mid_control": {
        "efficiency": 0.15,
        "presence": 0.07,
        "damage": 0.24,
        "economy": 0.13,
        "vision": 0.04,
        "utility": 0.13,
        "tank": 0.01,
        "objectives": 0.07,
        "playmaking": 0.10,
        "mechanics": 0.06,
    },
    "mid_assassin": {
        "efficiency": 0.12,
        "presence": 0.12,
        "damage": 0.20,
        "economy": 0.10,
        "vision": 0.03,
        "utility": 0.05,
        "tank": 0.02,
        "objectives": 0.08,
        "playmaking": 0.20,
        "mechanics": 0.08,
    },
    "mid_scaling": {
        "efficiency": 0.17,
        "presence": 0.06,
        "damage": 0.23,
        "economy": 0.16,
        "vision": 0.03,
        "utility": 0.10,
        "tank": 0.01,
        "objectives": 0.08,
        "playmaking": 0.11,
        "mechanics": 0.05,
    },
    "mid_roamer": {
        "efficiency": 0.11,
        "presence": 0.14,
        "damage": 0.17,
        "economy": 0.09,
        "vision": 0.06,
        "utility": 0.10,
        "tank": 0.02,
        "objectives": 0.08,
        "playmaking": 0.16,
        "mechanics": 0.07,
    },
    "bottom_hypercarry": {
        "efficiency": 0.17,
        "presence": 0.10,
        "damage": 0.27,
        "economy": 0.17,
        "vision": 0.03,
        "utility": 0.03,
        "tank": 0.01,
        "objectives": 0.08,
        "playmaking": 0.11,
        "mechanics": 0.03,
    },
    "bottom_utility": {
        "efficiency": 0.14,
        "presence": 0.12,
        "damage": 0.15,
        "economy": 0.12,
        "vision": 0.05,
        "utility": 0.12,
        "tank": 0.02,
        "objectives": 0.10,
        "playmaking": 0.12,
        "mechanics": 0.06,
    },
    "bottom_teamfight": {
        "efficiency": 0.15,
        "presence": 0.12,
        "damage": 0.22,
        "economy": 0.14,
        "vision": 0.04,
        "utility": 0.05,
        "tank": 0.01,
        "objectives": 0.10,
        "playmaking": 0.13,
        "mechanics": 0.04,
    },
    "support_engage": {
        "efficiency": 0.06,
        "presence": 0.19,
        "damage": 0.03,
        "economy": 0.01,
        "vision": 0.16,
        "utility": 0.24,
        "tank": 0.16,
        "objectives": 0.05,
        "playmaking": 0.08,
        "mechanics": 0.02,
    },
    "support_enchanter": {
        "efficiency": 0.09,
        "presence": 0.19,
        "damage": 0.03,
        "economy": 0.01,
        "vision": 0.17,
        "utility": 0.27,
        "tank": 0.05,
        "objectives": 0.04,
        "playmaking": 0.10,
        "mechanics": 0.05,
    },
    "support_mage": {
        "efficiency": 0.10,
        "presence": 0.17,
        "damage": 0.15,
        "economy": 0.02,
        "vision": 0.14,
        "utility": 0.19,
        "tank": 0.04,
        "objectives": 0.04,
        "playmaking": 0.10,
        "mechanics": 0.05,
    },
    "support_roamer": {
        "efficiency": 0.07,
        "presence": 0.20,
        "damage": 0.04,
        "economy": 0.01,
        "vision": 0.17,
        "utility": 0.20,
        "tank": 0.09,
        "objectives": 0.05,
        "playmaking": 0.12,
        "mechanics": 0.05,
    },
    "flex_carry": {
        "efficiency": 0.15,
        "presence": 0.12,
        "damage": 0.20,
        "economy": 0.12,
        "vision": 0.05,
        "utility": 0.06,
        "tank": 0.05,
        "objectives": 0.10,
        "playmaking": 0.10,
        "mechanics": 0.05,
    },
    "flex_frontline": {
        "efficiency": 0.08,
        "presence": 0.13,
        "damage": 0.08,
        "economy": 0.05,
        "vision": 0.08,
        "utility": 0.16,
        "tank": 0.20,
        "objectives": 0.11,
        "playmaking": 0.07,
        "mechanics": 0.04,
    },
    "flex_support": {
        "efficiency": 0.09,
        "presence": 0.16,
        "damage": 0.07,
        "economy": 0.04,
        "vision": 0.12,
        "utility": 0.22,
        "tank": 0.08,
        "objectives": 0.07,
        "playmaking": 0.09,
        "mechanics": 0.06,
    },
}

BENCHMARK_WEIGHTS = {
    "efficiency": 0.28,
    "presence": 0.18,
    "damage": 0.18,
    "economy": 0.08,
    "vision": 0.10,
    "utility": 0.04,
    "tank": 0.02,
    "objectives": 0.08,
    "playmaking": 0.06,
    "mechanics": 0.02,
    "laning": 0.04,
}


@dataclass(slots=True)
class PlayerMVPEntry:
    participant_id: int
    puuid: str | None
    team_id: int
    riot_id: str
    display_name: str
    champion: str
    role: str
    role_short: str
    archetype: str
    score: float
    benchmark_score: float
    rank: int = 0
    benchmark_rank: int = 0
    team_rank: int = 0
    badge: str = ""
    short_reason: str = ""
    components: dict[str, float] | None = None


@dataclass(slots=True)
class MatchMVPSummary:
    ranked_players: list[PlayerMVPEntry]
    by_puuid: dict[str, PlayerMVPEntry]
    by_participant_id: dict[int, PlayerMVPEntry]
    mvp_player: PlayerMVPEntry | None
    ace_player: PlayerMVPEntry | None

    def get_for_player(self, player: dict[str, Any]) -> PlayerMVPEntry | None:
        participant_id = _safe_int(player.get("participantId"))
        puuid = player.get("puuid")

        if participant_id in self.by_participant_id:
            return self.by_participant_id[participant_id]
        if puuid and puuid in self.by_puuid:
            return self.by_puuid[puuid]
        return None


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _average(*values: float) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _relative(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return _clamp(value / maximum)


def _cap_ratio(value: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return _clamp(value / cap)


def _normalize_role(player: dict[str, Any]) -> str:
    raw_role = (
        str(
            player.get("teamPosition")
            or player.get("individualPosition")
            or player.get("role")
            or ""
        )
        .strip()
        .upper()
    )
    return ROLE_ALIASES.get(raw_role, "FLEX")


def _player_display_name(player: dict[str, Any]) -> str:
    return (
        player.get("riotIdGameName")
        or player.get("summonerName")
        or "Unknown"
    )


def _riot_id(player: dict[str, Any]) -> str:
    game_name = player.get("riotIdGameName") or player.get("summonerName") or "Unknown"
    tag_line = player.get("riotIdTagline")
    return f"{game_name}#{tag_line}" if tag_line else game_name


def _initial_player_metrics(player: dict[str, Any], team: list[dict[str, Any]]) -> dict[str, Any]:
    challenges = player.get("challenges", {})
    role = _normalize_role(player)

    time_played = max(
        _safe_float(player.get("timePlayed")),
        _safe_float(challenges.get("gameLength")),
        1.0,
    )
    minutes_played = max(time_played / 60.0, 1.0)

    kills = _safe_int(player.get("kills"))
    deaths = _safe_int(player.get("deaths"))
    assists = _safe_int(player.get("assists"))
    cs = _safe_int(player.get("totalMinionsKilled")) + _safe_int(player.get("neutralMinionsKilled"))
    gold = _safe_int(player.get("goldEarned"))
    total_damage_to_champs = _safe_float(player.get("totalDamageDealtToChampions"))
    total_damage_taken = _safe_float(player.get("totalDamageTaken"))
    damage_self_mitigated = _safe_float(player.get("damageSelfMitigated"))
    damage_to_objectives = _safe_float(player.get("damageDealtToObjectives"))
    damage_to_turrets = _safe_float(player.get("damageDealtToTurrets"))
    damage_to_buildings = _safe_float(player.get("damageDealtToBuildings"))
    vision_score = _safe_float(player.get("visionScore"))
    heal_on_teammates = _safe_float(player.get("totalHealsOnTeammates"))
    shield_on_teammates = _safe_float(player.get("totalDamageShieldedOnTeammates"))
    healing = heal_on_teammates + shield_on_teammates
    team_kills = max(sum(_safe_int(team_player.get("kills")) for team_player in team), 1)

    kill_participation = _safe_float(challenges.get("killParticipation"))
    if kill_participation <= 0:
        kill_participation = _ratio(kills + assists, team_kills)
    kill_participation = _clamp(kill_participation)

    dpm = _safe_float(challenges.get("damagePerMinute"))
    if dpm <= 0:
        dpm = _ratio(total_damage_to_champs, minutes_played)

    gpm = _safe_float(challenges.get("goldPerMinute"))
    if gpm <= 0:
        gpm = _ratio(gold, minutes_played)

    csm = _ratio(cs, minutes_played)

    vision_per_min = _safe_float(challenges.get("visionScorePerMinute"))
    if vision_per_min <= 0:
        vision_per_min = _ratio(vision_score, minutes_played)

    control_wards = max(
        _safe_float(challenges.get("controlWardsPlaced")),
        _safe_float(player.get("detectorWardsPlaced")),
        _safe_float(player.get("visionWardsBoughtInGame")),
    )

    wards_killed = max(
        _safe_float(challenges.get("wardTakedowns")),
        _safe_float(player.get("wardsKilled")),
    )

    crowd_control = max(
        _safe_float(player.get("timeCCingOthers")),
        _safe_float(player.get("totalTimeCCDealt")),
    )

    immobilizations = _safe_float(challenges.get("enemyChampionImmobilizations"))
    damage_taken_share = _safe_float(challenges.get("damageTakenOnTeamPercentage"))
    tank_score = damage_self_mitigated + (total_damage_taken * 0.45)

    epic_objectives = (
        _safe_float(player.get("dragonKills"))
        + _safe_float(player.get("baronKills")) * 2.0
        + _safe_float(challenges.get("riftHeraldTakedowns")) * 1.5
        + _safe_float(challenges.get("voidMonsterKill")) * 1.3
        + _safe_float(player.get("objectivesStolen")) * 2.5
        + _safe_float(player.get("objectivesStolenAssists")) * 1.2
    )

    objective_score = (
        damage_to_objectives
        + damage_to_turrets * 0.35
        + damage_to_buildings * 0.15
        + epic_objectives * 7000
    )

    takedowns = max(
        _safe_float(challenges.get("takedowns")),
        _safe_float(kills + assists),
    )

    legendary_count = _safe_float(challenges.get("legendaryCount"))
    multikills = max(
        _safe_float(challenges.get("multikills")),
        _safe_float(player.get("doubleKills"))
        + _safe_float(player.get("tripleKills")) * 1.5
        + _safe_float(player.get("quadraKills")) * 2.0
        + _safe_float(player.get("pentaKills")) * 3.0,
    )

    solo_kills = _safe_float(challenges.get("soloKills"))
    spree_score = (
        _safe_float(player.get("largestKillingSpree"))
        + _safe_float(player.get("killingSprees")) * 0.7
        + legendary_count * 2.2
    )
    largest_spree = _safe_float(player.get("largestKillingSpree"))

    skillshots_dodged = (
        _safe_float(challenges.get("skillshotsDodged"))
        + _safe_float(challenges.get("dodgeSkillShotsSmallWindow")) * 1.4
    )
    skillshots_hit = max(
        _safe_float(challenges.get("skillshotsHit")),
        _safe_float(challenges.get("landSkillShotsEarlyGame")),
    )
    ability_uses = max(
        _safe_float(challenges.get("abilityUses")),
        _safe_float(player.get("spell1Casts"))
        + _safe_float(player.get("spell2Casts"))
        + _safe_float(player.get("spell3Casts"))
        + _safe_float(player.get("spell4Casts")),
    )

    lane_advantage = max(
        0.0,
        _safe_float(challenges.get("laningPhaseGoldExpAdvantage")),
        _safe_float(challenges.get("earlyLaningPhaseGoldExpAdvantage")),
    )

    lane_pressure = max(
        _safe_float(challenges.get("laneMinionsFirst10Minutes")),
        _safe_float(challenges.get("jungleCsBefore10Minutes")),
    )

    early_impact = max(
        _safe_float(challenges.get("takedownsFirstXMinutes")),
        _safe_float(challenges.get("quickSoloKills")),
        _safe_float(challenges.get("quickFirstTurret")),
    )

    save_ally = _safe_float(challenges.get("saveAllyFromDeath"))
    first_blood = bool(player.get("firstBloodKill") or player.get("firstBloodAssist"))
    first_tower = bool(player.get("firstTowerKill") or player.get("firstTowerAssist"))
    win = bool(player.get("win"))

    kda = _ratio(kills + assists, max(deaths, 1))

    return {
        "player": player,
        "role": role,
        "display_name": _player_display_name(player),
        "riot_id": _riot_id(player),
        "champion": player.get("championName", "Unknown"),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": kda,
        "kill_participation": kill_participation,
        "takedowns": takedowns,
        "dpm": dpm,
        "damage_to_champs": total_damage_to_champs,
        "team_damage_pct": _safe_float(challenges.get("teamDamagePercentage")),
        "gold_per_min": gpm,
        "cs_per_min": csm,
        "vision_per_min": vision_per_min,
        "vision_score": vision_score,
        "control_wards": control_wards,
        "wards_killed": wards_killed,
        "crowd_control": crowd_control,
        "immobilizations": immobilizations,
        "heal_shield": healing,
        "tank_score": tank_score,
        "damage_taken": total_damage_taken,
        "damage_taken_share": damage_taken_share,
        "objective_score": objective_score,
        "objective_damage": damage_to_objectives,
        "epic_objectives": epic_objectives,
        "spree_score": spree_score,
        "largest_spree": largest_spree,
        "solo_kills": solo_kills,
        "multikills": multikills,
        "legendary_count": legendary_count,
        "skillshots_dodged": skillshots_dodged,
        "skillshots_hit": skillshots_hit,
        "ability_uses": ability_uses,
        "lane_advantage": lane_advantage,
        "lane_pressure": lane_pressure,
        "early_impact": early_impact,
        "save_ally": save_ally,
        "first_blood": first_blood,
        "first_tower": first_tower,
        "win": win,
        "participant_id": _safe_int(player.get("participantId")),
        "puuid": player.get("puuid"),
        "team_id": _safe_int(player.get("teamId")),
    }


def _team_damage_pct(raw_metric: dict[str, Any], team_totals: dict[str, float]) -> float:
    explicit_value = _safe_float(raw_metric.get("team_damage_pct"))
    if explicit_value > 0:
        return _clamp(explicit_value)
    return _clamp(_ratio(raw_metric["damage_to_champs"], team_totals["damage_to_champs"]))


def _team_damage_taken_pct(raw_metric: dict[str, Any], team_totals: dict[str, float]) -> float:
    explicit_value = _safe_float(raw_metric.get("damage_taken_share"))
    if explicit_value > 0:
        return _clamp(explicit_value)
    return _clamp(_ratio(raw_metric["damage_taken"], team_totals["damage_taken"]))


def _collect_team_totals(team_metrics: list[dict[str, Any]]) -> dict[str, float]:
    totals = {
        "damage_to_champs": sum(metric["damage_to_champs"] for metric in team_metrics),
        "damage_taken": sum(metric["damage_taken"] for metric in team_metrics),
    }

    maximums = {
        "dpm": max((metric["dpm"] for metric in team_metrics), default=0.0),
        "gold_per_min": max((metric["gold_per_min"] for metric in team_metrics), default=0.0),
        "cs_per_min": max((metric["cs_per_min"] for metric in team_metrics), default=0.0),
        "vision_per_min": max((metric["vision_per_min"] for metric in team_metrics), default=0.0),
        "control_wards": max((metric["control_wards"] for metric in team_metrics), default=0.0),
        "wards_killed": max((metric["wards_killed"] for metric in team_metrics), default=0.0),
        "crowd_control": max((metric["crowd_control"] for metric in team_metrics), default=0.0),
        "immobilizations": max((metric["immobilizations"] for metric in team_metrics), default=0.0),
        "heal_shield": max((metric["heal_shield"] for metric in team_metrics), default=0.0),
        "tank_score": max((metric["tank_score"] for metric in team_metrics), default=0.0),
        "damage_taken": max((metric["damage_taken"] for metric in team_metrics), default=0.0),
        "objective_score": max((metric["objective_score"] for metric in team_metrics), default=0.0),
        "epic_objectives": max((metric["epic_objectives"] for metric in team_metrics), default=0.0),
        "spree_score": max((metric["spree_score"] for metric in team_metrics), default=0.0),
        "solo_kills": max((metric["solo_kills"] for metric in team_metrics), default=0.0),
        "multikills": max((metric["multikills"] for metric in team_metrics), default=0.0),
        "legendary_count": max((metric["legendary_count"] for metric in team_metrics), default=0.0),
        "skillshots_dodged": max((metric["skillshots_dodged"] for metric in team_metrics), default=0.0),
        "skillshots_hit": max((metric["skillshots_hit"] for metric in team_metrics), default=0.0),
        "ability_uses": max((metric["ability_uses"] for metric in team_metrics), default=0.0),
        "lane_advantage": max((metric["lane_advantage"] for metric in team_metrics), default=0.0),
        "lane_pressure": max((metric["lane_pressure"] for metric in team_metrics), default=0.0),
        "early_impact": max((metric["early_impact"] for metric in team_metrics), default=0.0),
        "takedowns": max((metric["takedowns"] for metric in team_metrics), default=0.0),
        "deaths": max((metric["deaths"] for metric in team_metrics), default=0.0),
    }

    return totals | maximums


def _build_components(raw_metric: dict[str, Any], team_context: dict[str, float]) -> dict[str, float]:
    deaths = float(raw_metric["deaths"])
    kda_norm = _cap_ratio(raw_metric["kda"], 6.0)
    death_control = 1.0 - _cap_ratio(deaths, max(8.0, team_context["deaths"]))
    efficiency = (kda_norm * 0.68) + (death_control * 0.32)

    presence = (
        raw_metric["kill_participation"] * 0.72
        + _relative(raw_metric["takedowns"], team_context["takedowns"]) * 0.28
    )

    damage = (
        _cap_ratio(_team_damage_pct(raw_metric, team_context), 0.33) * 0.58
        + _relative(raw_metric["dpm"], team_context["dpm"]) * 0.42
    )

    economy = (
        _relative(raw_metric["cs_per_min"], team_context["cs_per_min"]) * 0.55
        + _relative(raw_metric["gold_per_min"], team_context["gold_per_min"]) * 0.45
    )

    vision = (
        _relative(raw_metric["vision_per_min"], team_context["vision_per_min"]) * 0.55
        + _relative(raw_metric["control_wards"], team_context["control_wards"]) * 0.20
        + _relative(raw_metric["wards_killed"], team_context["wards_killed"]) * 0.25
    )

    utility = (
        _relative(raw_metric["immobilizations"], team_context["immobilizations"]) * 0.35
        + _relative(raw_metric["crowd_control"], team_context["crowd_control"]) * 0.25
        + _relative(raw_metric["heal_shield"], team_context["heal_shield"]) * 0.30
        + _relative(raw_metric["save_ally"], 3.0) * 0.10
    )

    tank = (
        _relative(raw_metric["tank_score"], team_context["tank_score"]) * 0.55
        + _relative(raw_metric["damage_taken"], team_context["damage_taken"]) * 0.20
        + _cap_ratio(_team_damage_taken_pct(raw_metric, team_context), 0.33) * 0.25
    )

    objectives = (
        _relative(raw_metric["objective_score"], team_context["objective_score"]) * 0.56
        + _relative(raw_metric["epic_objectives"], team_context["epic_objectives"]) * 0.24
        + _relative(1.0 if raw_metric["first_tower"] else 0.0, 1.0) * 0.20
    )

    playmaking = (
        _relative(raw_metric["spree_score"], team_context["spree_score"]) * 0.34
        + _relative(raw_metric["solo_kills"], team_context["solo_kills"]) * 0.24
        + _relative(raw_metric["multikills"], team_context["multikills"]) * 0.16
        + _relative(raw_metric["legendary_count"], team_context["legendary_count"]) * 0.14
        + _relative(raw_metric["early_impact"], team_context["early_impact"]) * 0.12
    )

    mechanics = (
        _relative(raw_metric["skillshots_dodged"], team_context["skillshots_dodged"]) * 0.45
        + _relative(raw_metric["skillshots_hit"], team_context["skillshots_hit"]) * 0.30
        + _relative(raw_metric["ability_uses"], team_context["ability_uses"]) * 0.20
        + _relative(1.0 if raw_metric["first_blood"] else 0.0, 1.0) * 0.05
    )

    laning = (
        _relative(raw_metric["lane_advantage"], team_context["lane_advantage"]) * 0.52
        + _relative(raw_metric["lane_pressure"], team_context["lane_pressure"]) * 0.33
        + _relative(raw_metric["early_impact"], team_context["early_impact"]) * 0.15
    )

    return {
        "efficiency": _clamp(efficiency),
        "presence": _clamp(presence),
        "damage": _clamp(damage),
        "economy": _clamp(economy),
        "vision": _clamp(vision),
        "utility": _clamp(utility),
        "tank": _clamp(tank),
        "objectives": _clamp(objectives),
        "playmaking": _clamp(playmaking),
        "mechanics": _clamp(mechanics),
        "laning": _clamp(laning),
    }


def _infer_profile(raw_metric: dict[str, Any], components: dict[str, float]) -> str:
    role = raw_metric["role"]
    champion = raw_metric["champion"]

    if role == "TOP":
        if champion in TANK_TOP_CHAMPIONS or (components["tank"] >= 0.62 and components["utility"] >= 0.35):
            return "top_frontline"
        if champion in SPLIT_PUSH_TOP_CHAMPIONS or (
            components["objectives"] >= 0.58
            and components["economy"] >= 0.58
            and raw_metric["kill_participation"] <= 0.58
        ):
            return "top_splitpush"
        return "top_bruiser"

    if role == "JUNGLE":
        if champion in OBJECTIVE_JUNGLE_CHAMPIONS or (
            components["objectives"] >= 0.62 and components["vision"] >= 0.36
        ):
            return "jungle_objective"
        if champion in CARRY_JUNGLE_CHAMPIONS or (
            components["damage"] >= 0.56 and components["playmaking"] >= 0.46
        ):
            return "jungle_carry"
        if champion in FACILITATOR_JUNGLE_CHAMPIONS or (
            components["presence"] >= 0.62 and components["utility"] >= 0.32
        ):
            return "jungle_facilitator"
        return "jungle_objective"

    if role == "MIDDLE":
        if champion in CONTROL_MAGE_CHAMPIONS or (
            components["damage"] >= 0.55 and components["utility"] >= 0.26
        ):
            return "mid_control"
        if champion in ASSASSIN_MID_CHAMPIONS or (
            components["playmaking"] >= 0.58 and raw_metric["solo_kills"] >= 1
        ):
            return "mid_assassin"
        if champion in SCALING_MID_CHAMPIONS or (
            components["damage"] >= 0.52 and components["economy"] >= 0.58 and raw_metric["kill_participation"] <= 0.68
        ):
            return "mid_scaling"
        return "mid_roamer"

    if role == "BOTTOM":
        if champion in UTILITY_BOTTOM_CHAMPIONS or components["utility"] >= 0.28:
            return "bottom_utility"
        if champion in HYPERCARRY_BOTTOM_CHAMPIONS or (
            components["damage"] >= 0.58 and components["economy"] >= 0.60
        ):
            return "bottom_hypercarry"
        return "bottom_teamfight"

    if role == "UTILITY":
        if champion in ENCHANTER_SUPPORT_CHAMPIONS or raw_metric["heal_shield"] >= 3000 or components["utility"] >= 0.52:
            return "support_enchanter"
        if champion in ENGAGE_SUPPORT_CHAMPIONS or (
            components["tank"] >= 0.48 and components["utility"] >= 0.34
        ):
            return "support_engage"
        if champion in MAGE_SUPPORT_CHAMPIONS or components["damage"] >= 0.42:
            return "support_mage"
        return "support_roamer"

    if raw_metric["heal_shield"] >= 2500 or components["utility"] >= 0.45:
        return "flex_support"
    if components["tank"] >= 0.50:
        return "flex_frontline"
    return "flex_carry"


def _score_from_weights(components: dict[str, float], weights: dict[str, float]) -> float:
    return sum(components[name] * weight for name, weight in weights.items())


def _benchmark_weights_for_role(role: str) -> dict[str, float]:
    weights = dict(BENCHMARK_WEIGHTS)

    if role == "UTILITY":
        weights["utility"] += 0.05
        weights["vision"] += 0.04
        weights["damage"] -= 0.04
        weights["economy"] -= 0.03
        weights["playmaking"] -= 0.02
    elif role == "JUNGLE":
        weights["objectives"] += 0.04
        weights["vision"] += 0.02
        weights["economy"] -= 0.02
        weights["damage"] -= 0.02
        weights["laning"] -= 0.02
    elif role == "TOP":
        weights["laning"] += 0.02
        weights["tank"] += 0.02
        weights["vision"] -= 0.02
        weights["presence"] -= 0.02
    elif role == "BOTTOM":
        weights["damage"] += 0.04
        weights["economy"] += 0.02
        weights["utility"] -= 0.02
        weights["tank"] -= 0.02
        weights["vision"] -= 0.02
    elif role == "MIDDLE":
        weights["damage"] += 0.02
        weights["playmaking"] += 0.02
        weights["tank"] -= 0.02
        weights["vision"] -= 0.02

    total_weight = sum(weights.values())
    return {name: weight / total_weight for name, weight in weights.items()}


def _build_reason(raw_metric: dict[str, Any], components: dict[str, float], weights: dict[str, float]) -> str:
    candidates: list[tuple[float, str]] = []

    if components["presence"] >= 0.42:
        candidates.append((components["presence"] * weights.get("presence", 0.0), f"{raw_metric['kill_participation'] * 100:.0f}% KP"))

    if components["damage"] >= 0.42:
        if _team_damage_pct(raw_metric, {"damage_to_champs": 0.0}) > 0:
            damage_text = f"{_team_damage_pct(raw_metric, {'damage_to_champs': 0.0}) * 100:.0f}% dmg"
        else:
            damage_text = f"{raw_metric['dpm']:.0f} DPM"
        candidates.append((components["damage"] * weights.get("damage", 0.0), damage_text))

    if components["vision"] >= 0.36 and raw_metric["vision_score"] > 0:
        candidates.append((components["vision"] * weights.get("vision", 0.0), f"vision {raw_metric['vision_score']:.0f}"))

    if components["utility"] >= 0.38:
        if raw_metric["heal_shield"] >= 1800:
            candidates.append((components["utility"] * weights.get("utility", 0.0), f"{raw_metric['heal_shield'] / 1000:.1f}k heal"))
        elif raw_metric["immobilizations"] >= 8:
            candidates.append((components["utility"] * weights.get("utility", 0.0), f"{raw_metric['immobilizations']:.0f} immob"))
        elif raw_metric["crowd_control"] >= 20:
            candidates.append((components["utility"] * weights.get("utility", 0.0), f"{raw_metric['crowd_control']:.0f} CC"))

    if components["tank"] >= 0.42 and raw_metric["tank_score"] > 0:
        candidates.append((components["tank"] * weights.get("tank", 0.0), f"{raw_metric['tank_score'] / 1000:.0f}k tank"))

    if components["objectives"] >= 0.42 and raw_metric["objective_damage"] > 0:
        candidates.append((components["objectives"] * weights.get("objectives", 0.0), f"{raw_metric['objective_damage'] / 1000:.0f}k obj"))

    if components["playmaking"] >= 0.36:
        if raw_metric["largest_spree"] >= 3:
            candidates.append((components["playmaking"] * weights.get("playmaking", 0.0), f"spree {raw_metric['largest_spree']:.0f}"))
        elif raw_metric["solo_kills"] >= 1:
            candidates.append((components["playmaking"] * weights.get("playmaking", 0.0), f"{raw_metric['solo_kills']:.0f} solo"))
        elif raw_metric["multikills"] >= 1:
            candidates.append((components["playmaking"] * weights.get("playmaking", 0.0), f"multi {raw_metric['multikills']:.0f}"))

    if components["economy"] >= 0.42:
        candidates.append((components["economy"] * weights.get("economy", 0.0), f"{raw_metric['cs_per_min']:.1f} CS/m"))

    if components["mechanics"] >= 0.36:
        if raw_metric["skillshots_dodged"] >= 20:
            candidates.append((components["mechanics"] * weights.get("mechanics", 0.0), f"{raw_metric['skillshots_dodged']:.0f} dodged"))
        elif raw_metric["skillshots_hit"] >= 10:
            candidates.append((components["mechanics"] * weights.get("mechanics", 0.0), f"{raw_metric['skillshots_hit']:.0f} hit"))

    candidates.sort(key=lambda item: item[0], reverse=True)
    top_texts = [text for _, text in candidates[:2]]

    if not top_texts:
        top_texts.append(f"{raw_metric['kills']}/{raw_metric['deaths']}/{raw_metric['assists']}")

    return ", ".join(top_texts)


def build_match_mvp_summary(participants: list[dict[str, Any]]) -> MatchMVPSummary:
    if not participants:
        return MatchMVPSummary(
            ranked_players=[],
            by_puuid={},
            by_participant_id={},
            mvp_player=None,
            ace_player=None,
        )

    players_by_team: dict[int, list[dict[str, Any]]] = {}
    for player in participants:
        team_id = _safe_int(player.get("teamId"))
        players_by_team.setdefault(team_id, []).append(player)

    raw_metrics: list[dict[str, Any]] = []
    team_contexts: dict[int, dict[str, float]] = {}

    for team_id, team_players in players_by_team.items():
        team_metrics = [_initial_player_metrics(player, team_players) for player in team_players]
        raw_metrics.extend(team_metrics)
        team_contexts[team_id] = _collect_team_totals(team_metrics)

    entries: list[PlayerMVPEntry] = []

    for raw_metric in raw_metrics:
        team_context = team_contexts[raw_metric["team_id"]]
        components = _build_components(raw_metric, team_context)
        profile_key = _infer_profile(raw_metric, components)
        role_weights = PROFILE_WEIGHTS[profile_key]

        score = _score_from_weights(components, role_weights) * 100
        score += 4.0 if raw_metric["win"] else 0.0
        score += min(raw_metric["legendary_count"], 3.0) * 1.2
        score += min(raw_metric["save_ally"], 3.0) * 0.7
        score += min(raw_metric["epic_objectives"], 4.0) * 0.45
        score += 1.0 if raw_metric["first_blood"] else 0.0
        score = round(_clamp(score, 0.0, 100.0), 1)

        benchmark_weights = _benchmark_weights_for_role(raw_metric["role"])
        benchmark_score = _score_from_weights(components, benchmark_weights) * 100
        benchmark_score += 3.0 if raw_metric["win"] else 0.0
        benchmark_score = round(_clamp(benchmark_score, 0.0, 100.0), 1)

        entries.append(
            PlayerMVPEntry(
                participant_id=raw_metric["participant_id"],
                puuid=raw_metric["puuid"],
                team_id=raw_metric["team_id"],
                riot_id=raw_metric["riot_id"],
                display_name=raw_metric["display_name"],
                champion=raw_metric["champion"],
                role=raw_metric["role"],
                role_short=ROLE_SHORT_LABELS.get(raw_metric["role"], raw_metric["role"]),
                archetype=PROFILE_LABELS.get(profile_key, profile_key),
                score=score,
                benchmark_score=benchmark_score,
                short_reason=_build_reason(raw_metric, components, role_weights),
                components=components,
            )
        )

    ranked_players = sorted(
        entries,
        key=lambda item: (
            item.score,
            item.components["playmaking"] if item.components else 0.0,
            item.components["damage"] if item.components else 0.0,
            item.benchmark_score,
        ),
        reverse=True,
    )
    benchmark_ranked_players = sorted(
        entries,
        key=lambda item: (
            item.benchmark_score,
            item.score,
        ),
        reverse=True,
    )

    for rank, entry in enumerate(ranked_players, start=1):
        entry.rank = rank

    for rank, entry in enumerate(benchmark_ranked_players, start=1):
        entry.benchmark_rank = rank

    for team_id, team_players in players_by_team.items():
        team_entries = [entry for entry in ranked_players if entry.team_id == team_id]
        for team_rank, entry in enumerate(team_entries, start=1):
            entry.team_rank = team_rank

    winners = [entry for entry in ranked_players if any(player.get("win") for player in players_by_team.get(entry.team_id, []))]
    losers = [entry for entry in ranked_players if entry not in winners]

    mvp_player = max(winners, key=lambda item: item.score, default=None)
    ace_player = max(losers, key=lambda item: item.score, default=None)

    if mvp_player is not None:
        mvp_player.badge = "MVP"
    if ace_player is not None:
        ace_player.badge = "ACE"

    by_puuid = {entry.puuid: entry for entry in ranked_players if entry.puuid}
    by_participant_id = {entry.participant_id: entry for entry in ranked_players}

    return MatchMVPSummary(
        ranked_players=ranked_players,
        by_puuid=by_puuid,
        by_participant_id=by_participant_id,
        mvp_player=mvp_player,
        ace_player=ace_player,
    )


def format_mvp_board(summary: MatchMVPSummary, limit: int = 10) -> str:
    if not summary.ranked_players:
        return "No MVP data"

    lines: list[str] = []
    for entry in summary.ranked_players[:limit]:
        badge = f" {entry.badge}" if entry.badge else ""
        line = (
            f"{entry.rank}. {entry.display_name[:14]} / {entry.champion[:12]} {entry.role_short} "
            f"{entry.score:.1f}{badge} | #{entry.benchmark_rank} | {entry.short_reason}"
        )
        lines.append(line[:96])

    text = "\n".join(lines)
    if len(text) > 1024:
        return text[:1021] + "..."
    return text


def format_player_mvp_line(summary: MatchMVPSummary, player: dict[str, Any]) -> str | None:
    entry = summary.get_for_player(player)
    if entry is None:
        return None

    badge = f" {entry.badge}" if entry.badge else ""
    return f"#{entry.rank} {entry.score:.1f}{badge} | #{entry.benchmark_rank} | {entry.archetype}"

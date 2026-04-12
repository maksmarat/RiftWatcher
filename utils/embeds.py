import discord

def build_match_embed(stats, match_time, title, match_id):
    embed = discord.Embed(
        title=title,
        description=f"Match ID: `{match_id}`",
        color=discord.Color.green()
    )

    blue_team = [p for p in stats if p['team'] == 100]
    red_team = [p for p in stats if p['team'] == 200]

    embed.add_field(name="🔵 Blue", value=format_team(blue_team), inline=True)
    embed.add_field(name="🔴 Red", value=format_team(red_team), inline=True)

    return embed


def format_team(team):
    text = ""
    for p in team:
        text += f"{p['nickname']} {p['kills']}/{p['deaths']}/{p['assists']}\n"
    return text or "Нет данных"
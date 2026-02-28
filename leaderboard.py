import discord
from database import fetch


def generate_leaderboard_embed():

    rows = fetch(
        "SELECT user_id, elo, wins, losses FROM users ORDER BY elo DESC LIMIT 10"
    )

    embed = discord.Embed(
        title="# <a:emoji_3:1477325503961501969>⛩️🩸**BLOOD BATTLES**🩸⛩️<a:emoji_3:1477325503961501969>",
        color=0x8B0000
    )

    if not rows:
        embed.description = "No Data Yet."
        return embed

    text = ""
    rank = 1

    for user_id, elo, wins, losses in rows:
        text += (
            f"**#{rank}** <@{user_id}>\n"
            f"🩸 Elo: {elo} | ✅ Wins: {wins} | ❌ Losses: {losses}\n\n"
        )
        rank += 1

    embed.description = text
    return embed

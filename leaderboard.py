import discord
from database import fetch


def generate_leaderboard_embed():

    rows = fetch(
        "SELECT user_id, elo, wins, losses FROM users ORDER BY elo DESC LIMIT 10"
    )

    embed = discord.Embed(
        title="<a:emoji_3:1477325503961501969>⛩️🩸**BLOOD BATTLES**🩸⛩️<a:emoji_3:1477325503961501969>",
        color=0x8B0000
    )

    if not rows:
        embed.description = "No Data Yet."
        return embed

    description = ""
    rank = 1

    for user_id, elo, wins, losses in rows:

        description += (
            f"**#{rank}** <@{user_id}>\n"
            f"<a:emoji_7:1477346975815831572> Elo: {elo} | <a:emoji_9:1477348230076301322> Wins: {wins} | <a:emoji_10:1477348263232540772>Losses: {losses}\n\n"
        )

        rank += 1

    embed.description = description
    return embed

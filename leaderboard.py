import discord
from database import fetch

leaderboard_message = None

async def update_leaderboard(channel):
    global leaderboard_message

    rows = fetch("SELECT user_id, elo, wins, losses FROM players ORDER BY elo DESC LIMIT 10")

    desc = ""
    rank = 1

    for user_id, elo, wins, losses in rows:
        desc += f"**#{rank}** <@{user_id}> 🩸 {elo} Elo | ✅ {wins} ❌ {losses}\n"
        rank += 1

    embed = discord.Embed(
        title="🩸 BLOOD LEADERBOARD",
        description=desc or "No Data",
        color=0x8B0000
    )

    if leaderboard_message is None:
        leaderboard_message = await channel.send(embed=embed)
    else:
        await leaderboard_message.edit(embed=embed)

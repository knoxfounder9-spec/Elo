import discord
from discord import app_commands
from config import TOKEN
from database import execute, fetch
from history import add_match
from leaderboard import update_leaderboard
import requests

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")


# ================= ELO COMMANDS ================= #

@tree.command(name="giveelo")
@app_commands.checks.has_permissions(administrator=True)
async def giveelo(interaction: discord.Interaction, user: discord.Member, amount: int):

    execute("INSERT INTO players (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (str(user.id),))
    execute("UPDATE players SET elo = elo + %s WHERE user_id=%s", (amount, str(user.id)))

    await interaction.response.send_message("✅ Elo Added")
    await update_leaderboard(interaction.channel)


@tree.command(name="removeelo")
@app_commands.checks.has_permissions(administrator=True)
async def removeelo(interaction: discord.Interaction, user: discord.Member, amount: int):

    execute("UPDATE players SET elo = elo - %s WHERE user_id=%s", (amount, str(user.id)))

    await interaction.response.send_message("❌ Elo Removed")
    await update_leaderboard(interaction.channel)


@tree.command(name="addwin")
@app_commands.checks.has_permissions(administrator=True)
async def addwin(interaction: discord.Interaction, winner: discord.Member, loser: discord.Member):

    execute("UPDATE players SET wins = wins + 1, elo = elo + 5 WHERE user_id=%s", (str(winner.id),))
    execute("UPDATE players SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s", (str(loser.id),))

    add_match(winner.id, loser.id)

    await interaction.response.send_message("🏆 Match Saved")
    await update_leaderboard(interaction.channel)


@tree.command(name="addloss")
@app_commands.checks.has_permissions(administrator=True)
async def addloss(interaction: discord.Interaction, user: discord.Member):

    execute("UPDATE players SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s", (str(user.id),))

    await interaction.response.send_message("💀 Loss Added")
    await update_leaderboard(interaction.channel)


# ================= HISTORY ================= #

@tree.command(name="history")
async def history(interaction: discord.Interaction):

    rows = fetch("SELECT winner, loser, timestamp FROM match_history ORDER BY id DESC LIMIT 10")

    text = ""

    for w, l, t in rows:
        text += f"🏆 <@{w}> vs <@{l}> — {t}\n"

    await interaction.response.send_message(text or "No History")


# ================= AI COMMAND ================= #

@tree.command(name="ai")
async def ai(interaction: discord.Interaction, prompt: str):

    await interaction.response.defer()

    # Free simple AI fallback
    try:
        res = requests.get("https://api.quotable.io/random").json()
        reply = f"🧠 AI:\n{prompt}\n\n💭 {res['content']}"
    except:
        reply = "AI Service Failed."

    await interaction.followup.send(reply)


import asyncio

async def main():
    await asyncio.sleep(5)  # prevents instant reconnect spam
    await bot.start(TOKEN)

asyncio.run(main())

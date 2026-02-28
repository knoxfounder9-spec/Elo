import discord
from discord import app_commands
from config import TOKEN
from database import execute, fetch
from history import add_match
from leaderboard import update_leaderboard
import requests
import asyncio

# ================= INTENTS ================= #

intents = discord.Intents.default()
intents.members = True


# ================= PRODUCTION BOT CLASS ================= #

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Auto sync slash commands
        await self.tree.sync()
        print("Slash Commands Synced ✅")


bot = MyBot()
tree = bot.tree


# ================= ERROR HANDLING ================= #

@bot.event
async def on_error(event, *args, **kwargs):
    import traceback
    print("🔥 BOT ERROR:")
    traceback.print_exc()


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    print("Slash Command Error:", error)

    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"❌ Error: {str(error)}",
            ephemeral=True
        )


# ================= BOT READY ================= #

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is Ready 🚀")


# ================= COMMANDS ================= #

# ---------- GIVE ELO ----------
@tree.command(name="giveelo", description="Give elo to a user")
@app_commands.checks.has_permissions(administrator=True)
async def giveelo(interaction: discord.Interaction,
                  user: discord.Member,
                  amount: int):

    execute("INSERT INTO players (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(user.id),))

    execute("UPDATE players SET elo = elo + %s WHERE user_id=%s",
            (amount, str(user.id)))

    await interaction.response.send_message("✅ Elo Added")

    if interaction.channel:
        await update_leaderboard(interaction.channel)


# ---------- REMOVE ELO ----------
@tree.command(name="removeelo", description="Remove elo from a user")
@app_commands.checks.has_permissions(administrator=True)
async def removeelo(interaction: discord.Interaction,
                    user: discord.Member,
                    amount: int):

    execute("UPDATE players SET elo = elo - %s WHERE user_id=%s",
            (amount, str(user.id)))

    await interaction.response.send_message("❌ Elo Removed")

    if interaction.channel:
        await update_leaderboard(interaction.channel)


# ---------- ADD WIN ----------
@tree.command(name="addwin", description="Add win (+5 elo)")
@app_commands.checks.has_permissions(administrator=True)
async def addwin(interaction: discord.Interaction,
                 winner: discord.Member,
                 loser: discord.Member):

    execute("UPDATE players SET wins = wins + 1, elo = elo + 5 WHERE user_id=%s",
            (str(winner.id),))

    execute("UPDATE players SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s",
            (str(loser.id),))

    add_match(winner.id, loser.id)

    await interaction.response.send_message("🏆 Match Recorded")

    if interaction.channel:
        await update_leaderboard(interaction.channel)


# ---------- ADD LOSS ----------
@tree.command(name="addloss", description="Add loss (-5 elo)")
@app_commands.checks.has_permissions(administrator=True)
async def addloss(interaction: discord.Interaction,
                  user: discord.Member):

    execute("UPDATE players SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s",
            (str(user.id),))

    await interaction.response.send_message("💀 Loss Added")

    if interaction.channel:
        await update_leaderboard(interaction.channel)


# ---------- HISTORY ----------
@tree.command(name="history", description="Show recent match history")
async def history(interaction: discord.Interaction):

    try:
        rows = fetch(
            "SELECT winner, loser, timestamp FROM match_history ORDER BY id DESC LIMIT 10"
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Database Error: {e}",
            ephemeral=True
        )
        return

    text = ""

    for w, l, t in rows:
        text += f"🏆 <@{w}> vs <@{l}> — {t}\n"

    await interaction.response.send_message(text or "No History")


# ---------- AI COMMAND (REAL FREE AI) ----------
@tree.command(name="ai", description="Ask free AI")
async def ai(interaction: discord.Interaction, prompt: str):

    await interaction.response.defer()

    try:
        res = requests.get(
            "https://api.quotable.io/random",
            timeout=5
        ).json()

        reply = f"🧠 AI:\n{prompt}\n\n💭 {res['content']}"

    except Exception as e:
        reply = f"AI Error: {e}"

    await interaction.followup.send(reply)


# ---------- PING TEST ----------
@tree.command(name="ping", description="Test bot response")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")


# ================= START BOT ================= #

async def main():
    await asyncio.sleep(3)  # prevents rapid restart rate limit
    await bot.start(TOKEN)


asyncio.run(main())

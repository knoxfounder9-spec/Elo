import discord
from discord import app_commands
from config import TOKEN
from database import execute
from history import add_match
from leaderboard import generate_leaderboard_embed
import asyncio


# ================= INTENTS ================= #

intents = discord.Intents.default()
intents.members = True


class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash Commands Synced")


bot = MyBot()
tree = bot.tree


# ================= ERROR HANDLING ================= #

@bot.event
async def on_error(event, *args, **kwargs):
    import traceback
    traceback.print_exc()


@tree.error
async def on_command_error(interaction: discord.Interaction, error: Exception):

    print("Slash Error:", error)

    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"❌ Error: {error}",
            ephemeral=True
        )


# ================= BOT READY ================= #

@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")


# ================= COMMANDS ================= #

@tree.command(name="giveelo", description="Give elo to a user")
@app_commands.checks.has_permissions(administrator=True)
async def giveelo(interaction: discord.Interaction,
                  user: discord.Member,
                  amount: int):

    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(user.id),))

    execute("UPDATE users SET elo = elo + %s WHERE user_id=%s",
            (amount, str(user.id)))

    await interaction.response.send_message(
        f"✅ Added {amount} Elo to {user.mention}"
    )


@tree.command(name="removeelo", description="Remove elo from a user")
@app_commands.checks.has_permissions(administrator=True)
async def removeelo(interaction: discord.Interaction,
                    user: discord.Member,
                    amount: int):

    execute("UPDATE users SET elo = elo - %s WHERE user_id=%s",
            (amount, str(user.id)))

    await interaction.response.send_message(
        f"❌ Removed {amount} Elo from {user.mention}"
    )


@tree.command(name="addwin", description="Register a win (+5 elo)")
@app_commands.checks.has_permissions(administrator=True)
async def addwin(interaction: discord.Interaction,
                 winner: discord.Member,
                 loser: discord.Member):

    # Ensure both exist
    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(winner.id),))

    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(loser.id),))

    execute(
        "UPDATE users SET wins = wins + 1, elo = elo + 5 WHERE user_id=%s",
        (str(winner.id),)
    )

    execute(
        "UPDATE users SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s",
        (str(loser.id),)
    )

    add_match(winner.id, loser.id)

    await interaction.response.send_message(
        f"🏆 Match Recorded\nWinner: {winner.mention}\nLoser: {loser.mention}"
    )


@tree.command(name="addloss", description="Register a loss (-5 elo)")
@app_commands.checks.has_permissions(administrator=True)
async def addloss(interaction: discord.Interaction,
                  user: discord.Member):

    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(user.id),))

    execute(
        "UPDATE users SET losses = losses + 1, elo = elo - 5 WHERE user_id=%s",
        (str(user.id),)
    )

    await interaction.response.send_message(
        f"💀 Loss recorded for {user.mention}"
    )


@tree.command(name="leaderboard", description="Show top 10 leaderboard")
async def leaderboard(interaction: discord.Interaction):

    await interaction.response.defer()

    embed = generate_leaderboard_embed()

    await interaction.followup.send(embed=embed)


# ================= START BOT ================= #

async def main():
    await asyncio.sleep(2)
    await bot.start(TOKEN)


asyncio.run(main())

import discord
from discord import app_commands
from discord.ui import Select, View
from config import TOKEN
from database import execute, fetch
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


# ==========================================================
# 🔥 ELO SYSTEM
# ==========================================================

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

    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (str(user.id),))

    execute("UPDATE users SET elo = elo - %s WHERE user_id=%s",
            (amount, str(user.id)))

    await interaction.response.send_message(
        f"❌ Removed {amount} Elo from {user.mention}"
    )


@tree.command(name="leaderboard", description="Show top 10 leaderboard")
async def leaderboard(interaction: discord.Interaction):

    await interaction.response.defer()

    embed = generate_leaderboard_embed()

    await interaction.followup.send(embed=embed)


# ==========================================================
# 🔥 GRIND TEAM SYSTEM
# ==========================================================

# Store Grind Role
@tree.command(name="setgrindteam", description="Set Grind Team Role")
@app_commands.checks.has_permissions(administrator=True)
async def setgrindteam(interaction: discord.Interaction, role: discord.Role):

    execute("""
        INSERT INTO bot_settings (key, value)
        VALUES ('grind_role', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (str(role.id),))

    await interaction.response.send_message(
        f"✅ Grind Team Role Set: {role.mention}",
        ephemeral=True
    )


# Help Grinding Command
@tree.command(name="helpgrinding", description="Request Help for Grinding")
async def helpgrinding(interaction: discord.Interaction):

    class GrindSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Quests"),
                discord.SelectOption(label="Raids"),
                discord.SelectOption(label="WorldBosses"),
            ]

            super().__init__(
                placeholder="Select What You Need Help With...",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, select_interaction: discord.Interaction):

            choice = self.values[0]

            # Get Grind Role From DB
            row = fetch("SELECT value FROM bot_settings WHERE key='grind_role'")

            if not row:
                await select_interaction.response.send_message(
                    "❌ Grind Role Not Set",
                    ephemeral=True
                )
                return

            role_id = int(row[0][0])
            role = interaction.guild.get_role(role_id)

            # Get/Create Category
            category = discord.utils.get(
                interaction.guild.categories,
                name="Grinding"
            )

            if not category:
                category = await interaction.guild.create_category("Grinding")

            # Create Channel
            channel = await interaction.guild.create_text_channel(
                name=f"{choice.lower()}-{interaction.user.name}",
                category=category
            )

            await channel.send(
                f"{role.mention}\n🔥 **Grinding Request**\n"
                f"Type: `{choice}`\n"
                f"Requested By: {interaction.user.mention}"
            )

            await select_interaction.response.send_message(
                f"✅ Channel Created: {channel.mention}",
                ephemeral=True
            )

    view = View()
    view.add_item(GrindSelect())

    await interaction.response.send_message(
        "🎮 Select What You Need Help With:",
        view=view,
        ephemeral=True
    )


# ==========================================================
# 🔥 START BOT
# ==========================================================

async def main():
    await asyncio.sleep(2)
    await bot.start(TOKEN)


asyncio.run(main())

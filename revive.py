import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import execute, fetch
import random


# ===============================
# 🔥 JJK REVIVE SYSTEM
# ===============================

JJK_MESSAGES = [
    "🔥 The cursed energy is rising...",
    "⚡ Domain Expansion Activated!",
    "🩸 Battle resumes... Who's strongest now?",
    "👑 A new challenger enters the battlefield!",
    "💀 Curses awaken from the shadows...",
    "⚔️ Let the fight begin again!",
    "🔥 Sukuna laughs at the chaos..."
]


class Revive(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.auto_revive.start()

    # ===============================
    # DATABASE TABLE
    # ===============================

    @commands.Cog.listener()
    async def on_ready(self):
        execute("""
        CREATE TABLE IF NOT EXISTS revive_channel (
            channel_id TEXT
        );
        """)
        print("✅ Revive System Ready")

    # ===============================
    # SET REVIVE CHANNEL
    # ===============================

    @app_commands.command(
        name="setrevivechannel",
        description="Set Auto Chat Revive Channel"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setrevivechannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        execute("DELETE FROM revive_channel")
        execute(
            "INSERT INTO revive_channel (channel_id) VALUES (%s)",
            (str(channel.id),)
        )

        await interaction.response.send_message(
            f"✅ Revive Channel Set: {channel.mention}",
            ephemeral=True
        )

    # ===============================
    # INSTANT REVIVE
    # ===============================

    @app_commands.command(
        name="instantchatrevive",
        description="Instantly Trigger Chat Revive"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def instantchatrevive(self, interaction: discord.Interaction):

        row = fetch("SELECT channel_id FROM revive_channel LIMIT 1")

        if not row:
            return await interaction.response.send_message(
                "❌ Revive channel not configured.",
                ephemeral=True
            )

        channel_id = row[0][0]
        channel = interaction.guild.get_channel(int(channel_id))

        if not channel:
            return await interaction.response.send_message(
                "❌ Channel not found.",
                ephemeral=True
            )

        message = random.choice(JJK_MESSAGES)

        await channel.send(
            f"@everyone\n🔥 **Instant Revival Activated** 🔥\n{message}"
        )

        await interaction.response.send_message(
            "✅ Instant revive triggered.",
            ephemeral=True
        )

    # ===============================
    # AUTO REVIVE TASK (EVERY HOUR)
    # ===============================

    @tasks.loop(hours=1)
    async def auto_revive(self):

        row = fetch("SELECT channel_id FROM revive_channel LIMIT 1")

        if not row:
            return

        channel_id = row[0][0]

        for guild in self.bot.guilds:
            channel = guild.get_channel(int(channel_id))

            if channel:
                message = random.choice(JJK_MESSAGES)

                await channel.send(
                    f"@everyone\n🔥 **Auto Chat Revival** 🔥\n{message}"
                )

    @auto_revive.before_loop
    async def before_auto_revive(self):
        await self.bot.wait_until_ready()


# ===============================
# LOAD FUNCTION
# ===============================

async def setup(bot):
    await bot.add_cog(Revive(bot))

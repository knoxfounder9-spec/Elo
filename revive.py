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
    "🩸 Battle resumes... Who's strongest now?",
    "👑 A new challenger enters the battlefield!",
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

        execute("""
        CREATE TABLE IF NOT EXISTS revive_role (
            role_id TEXT
        );
        """)

        print("✅ Revive System Ready")

    # ======================================================
    # SET REVIVE CHANNEL
    # ======================================================

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

    # ======================================================
    # SET REVIVE ROLE (PING ROLE)
    # ======================================================

    @app_commands.command(
        name="chatreviverole",
        description="Set Role To Ping On Auto & Instant Revive"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def chatreviverole(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):

        execute("DELETE FROM revive_role")

        execute(
            "INSERT INTO revive_role (role_id) VALUES (%s)",
            (str(role.id),)
        )

        await interaction.response.send_message(
            f"✅ Revive Ping Role Set To {role.mention}",
            ephemeral=True
        )

    # ======================================================
    # INSTANT REVIVE
    # ======================================================

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

        channel = interaction.guild.get_channel(int(row[0][0]))

        if not channel:
            return await interaction.response.send_message(
                "❌ Channel not found.",
                ephemeral=True
            )

        message = random.choice(JJK_MESSAGES)

        # 🔥 Get Role To Ping
        role_row = fetch("SELECT role_id FROM revive_role LIMIT 1")

        role_mention = ""
        if role_row:
            role = interaction.guild.get_role(int(role_row[0][0]))
            if role:
                role_mention = role.mention

        await channel.send(
            f"{role_mention}\n🔥 **Instant Revival Activated** 🔥\n{message}"
        )

        await interaction.response.send_message(
            "✅ Instant revive triggered.",
            ephemeral=True
        )

    # ======================================================
    # AUTO REVIVE (EVERY HOUR)
    # ======================================================

    @tasks.loop(hours=1)
    async def auto_revive(self):

        row = fetch("SELECT channel_id FROM revive_channel LIMIT 1")

        if not row:
            return

        for guild in self.bot.guilds:

            channel = guild.get_channel(int(row[0][0]))
            if not channel:
                continue

            message = random.choice(JJK_MESSAGES)

            # 🔥 Get Role To Ping
            role_row = fetch("SELECT role_id FROM revive_role LIMIT 1")

            role_mention = ""
            if role_row:
                role = guild.get_role(int(role_row[0][0]))
                if role:
                    role_mention = role.mention

            await channel.send(
                f"{role_mention}\n🔥 **Auto Chat Revival** 🔥\n{message}"
            )

    @auto_revive.before_loop
    async def before_auto_revive(self):
        await self.bot.wait_until_ready()


# ======================================================
# LOAD FUNCTION
# ======================================================

async def setup(bot):
    await bot.add_cog(Revive(bot))

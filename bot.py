import discord
from discord import app_commands
from discord.ui import Select, View
from config import TOKEN
from database import execute, fetch
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


# ================= READY ================= #

@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")


# ==========================================================
# 🔥 LEADERBOARD
# ==========================================================

@tree.command(name="leaderboard", description="Show top 10 leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = generate_leaderboard_embed()
    await interaction.followup.send(embed=embed)


# ==========================================================
# 🔥 SETUP COMMANDS
# ==========================================================

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


@tree.command(name="setstaffrole", description="Set Staff Role")
@app_commands.checks.has_permissions(administrator=True)
async def setstaffrole(interaction: discord.Interaction, role: discord.Role):

    execute("""
        INSERT INTO bot_settings (key, value)
        VALUES ('staff_role', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (str(role.id),))

    await interaction.response.send_message(
        f"✅ Staff Role Set: {role.mention}",
        ephemeral=True
    )


@tree.command(name="setreviewchannel", description="Set Application Review Channel")
@app_commands.checks.has_permissions(administrator=True)
async def setreviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):

    execute("""
        INSERT INTO bot_settings (key, value)
        VALUES ('review_channel', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (str(channel.id),))

    await interaction.response.send_message(
        f"✅ Review Channel Set: {channel.mention}",
        ephemeral=True
    )


@tree.command(name="pingrole", description="Set Role To Ping On Applications")
@app_commands.checks.has_permissions(administrator=True)
async def pingrole(interaction: discord.Interaction, role: discord.Role):

    execute("""
        INSERT INTO bot_settings (key, value)
        VALUES ('ping_role', %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (str(role.id),))

    await interaction.response.send_message(
        f"✅ Ping Role Set: {role.mention}",
        ephemeral=True
    )


# ==========================================================
# 🔥 HELP GRINDING
# ==========================================================

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
                options=options
            )

        async def callback(self, select_interaction: discord.Interaction):

            choice = self.values[0]

            row = fetch("SELECT value FROM bot_settings WHERE key='grind_role'")
            if not row:
                return await select_interaction.response.send_message(
                    "❌ Grind Role Not Set", ephemeral=True
                )

            role = interaction.guild.get_role(int(row[0][0]))
            if not role:
                return await select_interaction.response.send_message(
                    "❌ Grind Role Missing", ephemeral=True
                )

            category = discord.utils.get(interaction.guild.categories, name="Grinding")
            if not category:
                category = await interaction.guild.create_category("Grinding")

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
# 🔥 APPLICATION SYSTEM (WITH ADMIN OR STAFF ACCESS)
# ==========================================================

@tree.command(name="applygrindteam", description="Apply For Grind Team")
async def applygrindteam(interaction: discord.Interaction):

    questions = [
        "How active are you daily?",
        "What content can you help with?",
        "Power level / Experience?",
        "Why join Grind Team?",
        "Willing to respond when pinged?",
        "Have you helped others?",
        "Understand inactivity removal?",
        "Anything else?"
    ]

    await interaction.response.send_message(
        "📬 Check your DMs to complete the application.",
        ephemeral=True
    )

    dm = await interaction.user.create_dm()
    answers = []

    try:
        for q in questions:
            await dm.send(f"**{q}**")

            def check(m):
                return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

            msg = await bot.wait_for("message", check=check, timeout=300)
            answers.append(msg.content)

    except asyncio.TimeoutError:
        return await dm.send("❌ Application timed out.")

    review_row = fetch("SELECT value FROM bot_settings WHERE key='review_channel'")
    grind_row = fetch("SELECT value FROM bot_settings WHERE key='grind_role'")
    ping_row = fetch("SELECT value FROM bot_settings WHERE key='ping_role'")

    if not review_row or not grind_row:
        return await dm.send("❌ System not configured.")

    review_channel = interaction.guild.get_channel(int(review_row[0][0]))
    grind_role = interaction.guild.get_role(int(grind_row[0][0]))

    ping_role = None
    if ping_row:
        ping_role = interaction.guild.get_role(int(ping_row[0][0]))

    embed = discord.Embed(
        title="📥 Grind Team Application",
        color=0x8B0000
    )

    embed.add_field(
        name="Applicant",
        value=interaction.user.mention,
        inline=False
    )

    for i in range(len(questions)):
        embed.add_field(
            name=questions[i],
            value=answers[i],
            inline=False
        )

    # ==================================================
    # 🔥 BUTTON PANEL
    # ==================================================

    class ReviewButtons(View):

        def __init__(self):
            super().__init__(timeout=None)

        # ---------- STAFF CHECK ---------- #

        def staff_only(self, user: discord.Member):

            # ✅ Admin Permission
            if user.guild_permissions.administrator:
                return True

            staff_row = fetch("SELECT value FROM bot_settings WHERE key='staff_role'")
            if not staff_row:
                return False

            staff_role = user.guild.get_role(int(staff_row[0][0]))

            if staff_role and staff_role in user.roles:
                return True

            return False

        # ---------- ACCEPT ---------- #

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept(self, btn_interaction: discord.Interaction, button: discord.ui.Button):

            if not self.staff_only(btn_interaction.user):
                return await btn_interaction.response.send_message(
                    "❌ Staff Only",
                    ephemeral=True
                )

            await interaction.user.add_roles(grind_role)

            for item in self.children:
                item.disabled = True

            await btn_interaction.message.edit(view=self)

            await btn_interaction.response.send_message("✅ Accepted")

            await interaction.user.send(
                "🎉 Your Grind Team application was accepted!"
            )

        # ---------- DECLINE ---------- #

        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline(self, btn_interaction: discord.Interaction, button: discord.ui.Button):

            if not self.staff_only(btn_interaction.user):
                return await btn_interaction.response.send_message(
                    "❌ Staff Only",
                    ephemeral=True
                )

            for item in self.children:
                item.disabled = True

            await btn_interaction.message.edit(view=self)

            await btn_interaction.response.send_message("❌ Declined")

            await interaction.user.send(
                "❌ Your Grind Team application was declined."
            )

        # ---------- CLOSE ---------- #

        @discord.ui.button(label="Close", style=discord.ButtonStyle.gray)
        async def close(self, btn_interaction: discord.Interaction, button: discord.ui.Button):

            if not self.staff_only(btn_interaction.user):
                return await btn_interaction.response.send_message(
                    "❌ Staff Only",
                    ephemeral=True
                )

            await btn_interaction.message.delete()

    await review_channel.send(
        content=ping_role.mention if ping_role else None,
        embed=embed,
        view=ReviewButtons()
    )

    await dm.send("✅ Application submitted!")


# ==========================================================
# 🔥 START BOT
# ==========================================================

async def main():
    await bot.start(TOKEN)


asyncio.run(main())

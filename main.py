import os
import discord
from dotenv import load_dotenv
from stay_awake import stay_awake
from replit import db
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD"))

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)


class PersistentView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(
        label="Accept",
        style=discord.ButtonStyle.green,
        custom_id=f"mcsoc-bot-dev:button:accept:{datetime.now().isoformat()}",
    )
    async def accept(self, button: discord.ui.Button,
                     interaction: discord.Interaction):
        await accept_click(interaction)

    @discord.ui.button(
        label="Reject",
        style=discord.ButtonStyle.red,
        custom_id=f"mcsoc-bot-dev:button:reject:{datetime.now().isoformat()}",
    )
    async def reject(self, button: discord.ui.Button,
                     interaction: discord.Interaction):
        await reject_click(interaction, self.user)


class SelectRejectionReasonView(discord.ui.View):
    def __init__(self, user):
        self.user = user
        super().__init__()

    @discord.ui.select(
        placeholder="Select a reason for rejection",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Not Registered On SU"),
            discord.SelectOption(
                label="Used IT username instead of numerical student ID"),
            discord.SelectOption(label="Non-existent Minecraft username"),
            discord.SelectOption(label="Non Student Email"),
            discord.SelectOption(label="Incorrect Details"),
            discord.SelectOption(label="Other Rejection Reason")
        ])
    async def select_callback(self, select, interaction):
        await interaction.message.edit(content=interaction.message.content +
                                       "```diff\n- Rejected - " +
                                       select.values[0] + "\n```",
                                       view=None)

        try:
            user_dm = await bot.create_dm(self.user)
            await user_dm.send(
                "You were not whitelisted on the UoM Minecraft Society server "
                "due to an issue with the details you entered. The issue was: "
                f"{select.values[0]}. Please correct this and send the "
                "whitelist command again, or contact a committee member if "
                "you need help.")
        except Exception:
            print("Failed to send DM")


@bot.event
async def on_ready():
    # wait for everything in this function to make sure nothing gets weird
    print(f"Logged on as {bot.user}")


async def whitelist_user(ctx, username, email_or_id, email: bool):
    """Whitelist logic"""
    db[str(ctx.author.mention)] = [str(ctx.author), username, email_or_id]

    log_channel = bot.get_channel(int(os.getenv("LOG-CHANNEL")))
    rules_channel = bot.get_channel(int(os.getenv("RULES-CHANNEL")))
    info_channel = bot.get_channel(int(os.getenv("INFO-CHANNEL")))

    view = PersistentView(user=ctx.author)
    bot.add_view(view)

    await log_channel.send(
        f"Discord user: {ctx.author.mention}\n"
        f"Username: `{username}`\n"
        f"Student {'email' if email else 'id'}: {email_or_id}",
        view=view)

    response_msg = (
        "Thanks, that's all! You'll get the 'whitelisted' role on discord "
        "when we've manually whitelisted you.\nPlease go read the "
        f"{rules_channel.mention} and {info_channel.mention} channels in the "
        "meantime to make sure you're up to date!")

    await ctx.respond(response_msg, ephemeral=True)


# Create whitelist command group
whitelist = bot.create_group("whitelist", guild_ids=[GUILD_ID])


@whitelist.command(guild_ids=[GUILD_ID])
async def with_id(ctx, minecraft_username, student_id: int):
    """Apply to be whitelisted using your student ID"""
    await whitelist_user(ctx, minecraft_username, student_id, email=False)


@whitelist.command(guild_ids=[GUILD_ID])
async def with_email(ctx, minecraft_username, student_email):
    """Apply to be whitelisted using your student email"""
    await whitelist_user(ctx, minecraft_username, student_email, email=True)


async def accept_click(interaction):
    msg = interaction.message.content.split()
    user_id = msg[2]
    mc_user = db[user_id][1]

    # Send whitelist command
    console_channel = bot.get_channel(int(os.getenv("CONSOLE-CHANNEL")))
    await console_channel.send(f"whitelist add {mc_user}")

    guild = interaction.guild
    member = await guild.fetch_member(user_id[2:-1])

    # Add whitelisted role
    whitelisted_role = guild.get_role(int(os.getenv("WHITELISTED-ROLE")))
    await member.add_roles(whitelisted_role)

    # Remove buttons and record result
    await interaction.message.edit(content=interaction.message.content +
                                   "```diff\n+ Accepted\n```",
                                   view=None)


# async def reject_click(interaction, reject_reason, user):
async def reject_click(interaction, user):
    await interaction.message.edit(
        view=SelectRejectionReasonView(user))


stay_awake()
bot.run(BOT_TOKEN)

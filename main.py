import os
import discord
from discord.ui import Button, View
from dotenv import load_dotenv
from stay_awake import stay_awake
from replit import db
from functools import partial

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD"))

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)


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

    view = View()
    accept_button = Button(label="Accept", style=discord.ButtonStyle.green)
    accept_button.callback = accept_click
    view.add_item(accept_button)

    reject_reasons = ["Not Registered On SU", "Used IT username instead of numerical student ID",
                      "Non-existent Minecraft username", "Non Student Email", "Incorrect Details",
                      "Other Rejection Reason"]
    for reject_reason in reject_reasons:
        reject_button = Button(label=reject_reason, style=discord.ButtonStyle.red)
        reject_button_callback_partial = partial(reject_click, reject_reason=reject_reason, user=ctx.author)
        reject_button.callback = reject_button_callback_partial
        view.add_item(reject_button)

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
whitelist = bot.create_group(
    "whitelist",
    guild_ids=[GUILD_ID])


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
    username = msg[2]
    mc_user = db[username][1]

    # Send whitelist command
    console_channel = bot.get_channel(int(os.getenv("CONSOLE-CHANNEL")))
    await console_channel.send(f"whitelist add {mc_user}")

    guild = interaction.guild
    member = await guild.fetch_member(username[2:-1])
    
    # Add whitelisted role
    whitelisted_role = guild.get_role(int(os.getenv("WHITELISTED-ROLE")))
    await member.add_roles(whitelisted_role)

    # Remove buttons and record result
    await interaction.message.edit(
        content=interaction.message.content + "```diff\n+ Accepted\n```",
        view=None
    )


async def reject_click(interaction, reject_reason, user):
    # Remove buttons and record result
    await interaction.message.edit(
        content=interaction.message.content + "```diff\n- Rejected - " + reject_reason + "\n```",
        view=None
    )
    try:
        user_dm = await bot.create_dm(user)
        await user_dm.send(
            "You were not whitelisted on the UoM Minecraft Society server due to an issue with the details you entered."
            f" The issue was: {reject_reason}. Please correct this and send the whitelist command again, "
            "or contact a committee member if you need help.")
    except Exception:
        print("Failed to send DM")


stay_awake()
bot.run(BOT_TOKEN)
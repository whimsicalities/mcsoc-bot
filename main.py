import os
import discord
from dotenv import load_dotenv
from stay_awake import stay_awake

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD"))

bot = discord.Bot()


@bot.event
async def on_ready():
    # wait for everything in this function to make sure nothing gets weird
    print(f"Logged on as {bot.user}")


async def whitelist_user(ctx, username, email_or_id, email: bool):
    """Whitelist logic"""

    log_channel = bot.get_channel(int(os.getenv("LOG-CHANNEL")))
    rules_channel = bot.get_channel(int(os.getenv("RULES-CHANNEL")))
    info_channel = bot.get_channel(int(os.getenv("INFO-CHANNEL")))

    await log_channel.send(
        f"Discord user: {ctx.author}\n"
        f"Username: `{username}`\n"
        f"Student {'email' if email else 'id'}: {email_or_id}")

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

stay_awake()
bot.run(BOT_TOKEN)

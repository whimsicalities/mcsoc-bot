import os
import discord
from discord.ui import Button, View
from dotenv import load_dotenv
from stay_awake import stay_awake
from replit import db

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
    db[str(ctx.author)] = [str(ctx.author), username, email_or_id]
    
    log_channel = bot.get_channel(int(os.getenv("LOG-CHANNEL")))
    rules_channel = bot.get_channel(int(os.getenv("RULES-CHANNEL")))
    info_channel = bot.get_channel(int(os.getenv("INFO-CHANNEL")))

    view = View()
    accept_button = Button(label="Accept", style=discord.ButtonStyle.green)
    accept_button.callback = accept_click
    view.add_item(accept_button)

    reject_button = Button(label="Reject", style=discord.ButtonStyle.red)
    reject_button.callback = reject_click
    view.add_item(reject_button)
    
    await log_channel.send(
        f"Discord user: {ctx.author}\n"
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
    # Get Discord member by username
    member = discord.utils.get(
        guild.members,
        name=username[:username.index("#")],
        discriminator=username[username.index("#") + 1:]
    )

    # Add whitelisted role
    whitelisted_role = guild.get_role(int(os.getenv("WHITELISTED-ROLE")))
    await member.add_roles(whitelisted_role)

    # Remove buttons and record result
    await interaction.message.edit(
        content=interaction.message.content + "```diff\n+ Accepted\n```",
        view=None
    )


async def reject_click(interaction):
    # Remove buttons and record result
    await interaction.message.edit(
        content=interaction.message.content + "```diff\n- Rejected\n```",
        view=None
    )

stay_awake()
bot.run(BOT_TOKEN)
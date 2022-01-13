import os
import discord
from dotenv import load_dotenv
from stay_awake import stay_awake

load_dotenv()

bot = discord.Client()


@bot.event
async def on_ready():
    # wait for everything in this function to make sure nothing gets weird
    print(f"Logged on as {bot.user}")


@bot.event
async def on_message(message):
    def check_is_dm(msg):
        return (msg.author == author and
                isinstance(msg.channel, discord.channel.DMChannel))

    if '!WHITELIST' in message.content.upper():
        author = message.author

        # Request user details in private chat
        await message.author.send(
            "Please send your Minecraft Java Edition Username.")
        username = await bot.wait_for('message', check=check_is_dm)

        await message.author.send(
            "Please send your student ID number or uni email so that we can "
            "verify you signed up on the SU website.")
        student_id = await bot.wait_for('message', check=check_is_dm)

        await message.author.send(
            "Thanks, that's all! You'll get the 'whitelisted' role on discord "
            "when we've manually whitelisted you.\nPlease go read the "
            " `#rules` and `#server-information` channels in the meantime to "
            "make sure you're up to date!")

        # Send user details to log channel
        log_channel = bot.get_channel(int(os.getenv('log-channel')))
        await log_channel.send(
            f"Discord user: {message.author}\n"
            f"Username: `{username.content}`\n"
            f"Student ID or email: {student_id.content}")

stay_awake()
bot.run(os.getenv('TOKEN'))

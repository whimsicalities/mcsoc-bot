import discord
import os
from dotenv import load_dotenv
from stay_awake import stay_awake

load_dotenv()

bot = discord.Client()

@bot.event
async def on_ready(): # wait for everything in this function to make sure nothing gets weird
  print("Logged on as {0.user}".format(bot))

@bot.event
async def on_message(message):
  print("Recieved message")

  def check_is_dm(msg):
    return msg.author==author and isinstance(msg.channel, discord.channel.DMChannel)

  if ('!WHITELIST' in message.content.upper()):
    log_channel = bot.get_channel(int(os.getenv('log-channel')))
    await log_channel.send('Discord user: '+message.author.name+'#'+message.author.discriminator)
    author = message.author
    await message.author.send("Please send your Minecraft Java Edition Username")
    msg = await bot.wait_for('message', check=check_is_dm)
    await log_channel.send('Username for '+message.author.name+': `'+msg.content+'`')
    await message.author.send("Please send your student ID number or uni email so that we can verify you signed up on the SU website.")
    msg = await bot.wait_for('message', check=check_is_dm)
    await log_channel.send('Student ID or email for '+message.author.name+': '+msg.content)
    await message.author.send("Thanks, that's all! you'll get the 'whitelisted' role on discord when we've manually whitelisted you, please go read the 'rules' and 'server-information' channels in the meantime to make sure you're up to date!")


stay_awake()
bot.run(os.getenv('TOKEN'))
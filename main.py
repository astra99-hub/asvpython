import datetime

import discord
import asyncio
import ezcord
from dotenv import load_dotenv
import os
from ezcord import log
import logging
import asyncio
from colorama import Fore

intents = discord.Intents.all()
intents.voice_states = True


colors = {
    logging.DEBUG: "blue",
    logging.INFO: Fore.MAGENTA,
}

bot = ezcord.Bot(intents=intents,
        error_webhook_url=(os.getenv("webhook"))
)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else:
        if message.channel.id == 1135585815146274832: ##Hier kommt die id vom channel hin
            user = message.author

            embed = discord.Embed(title=f"Vorschlag von {message.author.name}", description=message.content,
                                  color=discord.Color.purple()) ##die farbe des embed kann man hier ändern
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"{message.author.name} danke für dein Vorschlag.")
           

            msg = await bot.get_channel(1135585815146274832).send(embed=embed) ###hier kommt die id vom channel hin
            await msg.add_reaction("👍") ##hier könnt ihr die emoji reaktionen ändern
            await msg.add_reaction("👎") ##hier könnt ihr die emoji reaktionen ändern
            await asyncio.sleep(1) ## er wartet
            await message.delete() ## er löscht es

@bot.event
async def on_ready():
    channel_id = 1135585816215830568 # dein id
    channel = bot.get_channel(channel_id)
    bot.loop.create_task(status_task())


@bot.event
async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game('https://dsc.gg/av-bot'), status=discord.Status.online)
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game('TikTok wannashowmiss'), status=discord.Status.idle)
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game('My owner is av.tano'), status=discord.Status.dnd)
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game('error an av.tano'), status=discord.Status.dnd)
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game('https://github.com/asvpython/asvpython/tree/main'), status=discord.Status.dnd)
        await asyncio.sleep(10)




@bot.slash_command(description="Zeigt dir alle Commands an")
async def help(ctx):
    emb = discord.Embed(
        title="Help",
        description="**Commands**",
        color=discord.Color.blue()
    )
    for cog in bot.cogs:
        emb.add_field(name=cog, value="• " + "\n• ".join([command.name for command in bot.get_cog(cog).get_commands()]),
                      inline=False)
    await ctx.respond(embed=emb)

log.debug("This is a debug message")
log.info("This is an info message")

ezcord.custom_log("CUSTOM", "This is a message with a custom log level")



if __name__ == "__main__":
    bot.load_cogs("cogs", log=ezcord.CogLog.default, log_color="green")

    load_dotenv()
    bot.run(os.getenv("TOKEN"))

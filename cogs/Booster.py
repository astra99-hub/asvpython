import discord
from discord.ext import commands

class Booster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is None and after.premium_since is not None:
            booster = after
            nachricht = f"Vielen Dank, {booster.mention}, dass du den Server geboostet hast! Wir schätzen deine Unterstützung!"

            channel_id = 1133810500879257600  # Hier die ID des channel einfügen
            channel = self.bot.get_channel(channel_id)

            if channel is not None:
                await channel.send(nachricht)

def setup(bot):
    bot.add_cog(Booster(bot))

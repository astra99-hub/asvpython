import discord
from discord.ext import commands
from discord.commands import slash_command


class invite(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
            embed = discord.Embed(
                title="Danke!",
                description=f"Danke {guild.owner.mention} das du mich auf {guild.name} hinzugefügt hast!",
                color=discord.Color.purple()
            )

            channel = await self.bot.fetch_channel(1135585814684897340) # dein id
            await channel.send(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(invite(bot))
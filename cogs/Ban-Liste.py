import discord
from discord.ext import commands
from discord.commands import Option

from discord.ext import commands

class BanListe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_only=True, description="Alle Banned-Mitglieder auf dem Server abrufen")
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        bans = ctx.guild.bans()
        pretty_list = ["• {0.name}#{0.discriminator}".format(entry.user) async for entry in bans]
        if pretty_list == []:
            em = discord.Embed(description="Niemand wurde auf den Server verbannt **Großartig!**",
                               color=discord.Color.blue())
            return await ctx.respond(embed=em)
        embed = discord.Embed(title="Ban Liste für diesen Server",
                              description="\n{}".format("\n".join(pretty_list)), color=discord.Color.blue())
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar.url}")
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(BanListe(bot))


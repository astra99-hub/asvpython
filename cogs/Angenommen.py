import discord
from discord.ext import commands
from discord.commands import slash_command
class Angenommen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Ein Angenommen command")
    @commands.has_permissions(ban_members=True)
    async def angenommen_embed(self, ctx):
        embed = discord.Embed(
            title="Willkommen im  Team",
            description="Angenommen",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Angenommen(bot))

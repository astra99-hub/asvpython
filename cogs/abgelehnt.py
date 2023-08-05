import discord
from discord.ext import commands
from discord.commands import slash_command
class abgelehnt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Ein abgelehnt command")
    @commands.has_permissions(ban_members=True)
    async def abgelehnt_embed(self, ctx):
        embed = discord.Embed(
            title="sie wurde nicht angenommen Team",
            description="abgelehnt",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(abgelehnt(bot))
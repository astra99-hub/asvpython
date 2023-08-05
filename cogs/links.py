import discord
from discord.commands import slash_command
from discord.ext import commands


class links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TutorialView())


    @slash_command(description="Zeige dir alle Wichtigen Links an")
    async def links(self, ctx):
        button = discord.ui.Button(label="YouTube", url="https://www.youtube.com/@Codingkiwi519")
        button2 = discord.ui.Button(label="my discord ", url="https://dsc.gg/av-bot")
        button3 = discord.ui.Button(label="TikTok", url="https://www.tiktok.com/@wannashowmiss")
        button4 = discord.ui.Button(label="Bot hinzufügen", url="https://discord.com/api/oauth2/authorize?client_id=1130213076122218516&permissions=8&scope=applications.commands%20bot")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)

        await ctx.respond(view=view)


def setup(bot: discord.Bot):
    bot.add_cog(links(bot))


class TutorialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
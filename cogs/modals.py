import discord
from discord.ext import commands
from discord.commands import slash_command


class ModalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    @discord.default_permissions(moderate_members=True)
    async def modal(self, ctx):
        modal = TutorialModal(title="Erstelle ein Embed")
        await ctx.send_modal(modal)


def setup(bot):
    bot.add_cog(ModalCog(bot))


class TutorialModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Embed Titel",
                placeholder="Placeholder"
            ),
            discord.ui.InputText(
                label="Embed Beschreibung",
                placeholder="Placeholder",
                style=discord.InputTextStyle.long
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title=self.children[0].value,
            description=self.children[1].value,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

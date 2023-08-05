import discord
from discord.ext import commands

class VoiceState(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if after.channel is not None and after.channel.id == 1136659062352777246:
            print(f"es wurde ein {member} channel gemacht")
            category = discord.utils.get(guild.categories, id=1136658842613203014)
            channel_name = f'『🔥』{member.display_name}'
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=True)
            }
            channel = await category.create_voice_channel(channel_name, overwrites=overwrites)
            await member.move_to(channel)
        elif before.channel is not None and before.channel.name.startswith('『🔥』'):
            if len(before.channel.members) <= 1:
                print(f"Der Kanal wurde von {member} erfolgreich gelöscht")
                await before.channel.delete()

def setup(bot):
    bot.add_cog(VoiceState(bot))
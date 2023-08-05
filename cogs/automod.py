import discord
from discord.ext import commands
from discord.commands import slash_command
from datetime import timedelta

invite_links = ["discord.gg", "discord.com/invite"]
word_filter = ["nigga", "pedo", "russe is bad"]
class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    @commands.guild_only()
    async def automod(self, ctx: discord.ApplicationCommand, log_channel: discord.TextChannel):
        actions = [
            discord.AutoModAction(
                action_type=discord.AutoModActionType.block_message,
                metadata=discord.AutoModActionMetadata(),
            ),
            discord.AutoModAction(
                action_type=discord.AutoModActionType.send_alert_message,
                metadata=discord.AutoModActionMetadata(channel_id=log_channel.id),
            ),
            discord.AutoModAction(
                action_type=discord.AutoModActionType.timeout,
                metadata=discord.AutoModActionMetadata(timeout_duration=timedelta(hours=1)),
            ),
        ]

        await ctx.guild.create_auto_moderation_rule(
            name="Anti Invite and Word Filter",
            event_type=discord.AutoModEventType.message_send,
            trigger_type=discord.AutoModTriggerType.keyword,
            trigger_metadata=discord.AutoModTriggerMetadata(keyword_filter=invite_links + word_filter),
            enabled=True,
            actions=actions
        )
        await ctx.respond("✅ Erfolgreich eingerichtet.", ephemeral=True)

def setup(bot):
    bot.add_cog(Automod(bot))

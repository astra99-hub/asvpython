import discord
from discord.ext import commands
from discord.commands import slash_command, Option

class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def userinfo(self,ctx: discord.ApplicationContext, member: Option(discord.Member, required=False)):
        member = member or ctx.author
        user = await self.bot.fetch_user(member.id)  # Fetch user for the user banner

        BADGE_DICT = {
            discord.UserFlags.bug_hunter: '🌮 Bug Hunter',
            discord.UserFlags.bug_hunter_level_2: '🌮 Bug Hunter Level 2',
            discord.UserFlags.early_supporter: '🌮 Early Supporter',
            discord.UserFlags.verified_bot_developer: '🌮Verifizierter Bot Entwickler',
            discord.UserFlags.active_developer: '🌮 Aktiver Entwickler',
            discord.UserFlags.partner: '🌮 Discord Partner',
            discord.UserFlags.staff: '🌮 Discord Staff',
            discord.UserFlags.hypesquad_balance: '🌮 Hypesquad Balance',
            discord.UserFlags.hypesquad_bravery: '🌮 Hypesquad Bravery',
            discord.UserFlags.hypesquad_brilliance: '🌮 Hypesquad Brilliance'
        }
        STATUS_DICT = {
            discord.Status.online: ('🌮' if member.is_on_mobile() else '🌮') + ' `Online`',
            discord.Status.idle: '🌮 `Abwesend`',
            discord.Status.dnd: '🌮 `Bitte nicht stören`',
            discord.Status.offline: '🌮> `Offline`',
        }

        embed = discord.Embed(
            color=member.color,
            timestamp=discord.utils.utcnow(),
            description=f'{member.mention} wurde {discord.utils.format_dt(member.created_at, style="R")} erstellt.\n'
                        f'{member.nick or member.name} ist dem Server {discord.utils.format_dt(member.joined_at, style="R")} beigetreten.'
        )
        embed.set_author(name=f'Userinfo {member}', icon_url=member.avatar or member.default_avatar)
        embed.set_thumbnail(url=member.display_avatar)
        if user and user.banner:
            embed.set_image(url=user.banner.url)

        embed.add_field(name='User-ID:', value=member.id, inline=False)
        embed.add_field(name='Höchste Rolle:', value=member.top_role.mention, inline=False)
        if member.premium_since:
            embed.add_field(
                name='Booster:', value=f'🌮 {discord.utils.format_dt(member.premium_since)}'
            )
        badges = [BADGE_DICT[flag] for flag in member.public_flags.all() if flag in BADGE_DICT.keys()]
        if badges:
            embed.add_field(name='Badges:', value='\n'.join(badges), inline=False)
        embed.add_field(
            name='Status:', value=STATUS_DICT[member.status] + (' (Mobile)' if member.is_on_mobile() else ''), inline=False
        )
        activities = []
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                txt = f'Spotify: [{activity.artist} - {activity.title}]({activity.track_url})'
            elif isinstance(activity, discord.Game):
                txt = f'Spielt: {activity.name}'
            elif isinstance(activity, discord.Streaming):
                txt = f'Streamt: [{activity.twitch_name} - {activity.game}]({activity.url})'
            elif isinstance(activity, discord.CustomActivity):
                txt = f'Status: {activity.name}'
            else:
                txt = f'{activity.name}: {activity.details}'
            activities.append(txt)
        if activities:
            embed.add_field(name='Aktivitäten', inline=False, value='\n'.join(activities))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Userinfo(bot))

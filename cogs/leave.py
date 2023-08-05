import discord
from discord.ext import commands
import sqlite3
from discord.commands import slash_command

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thumbnail_url = ""
        print("bye db 'sqlite3.connect' is ready.")
        self.conn = sqlite3.connect("data/bye.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS server_settings (server_id INTEGER PRIMARY KEY, thumbnail_url TEXT)"
        )
        self.conn.commit()

    @slash_command(description="create a leave channel.")
    @commands.has_permissions(administrator=True)
    async def setup_leave(self, ctx, channel: discord.TextChannel, thumbnail_url):
        self.cursor.execute(
            "INSERT OR REPLACE INTO server_settings (server_id, thumbnail_url) VALUES (?, ?)",
            (ctx.guild.id, thumbnail_url)
        )
        self.conn.commit()
        await ctx.respond(f"leave channel has been set to {channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        server_id = member.guild.id

        self.cursor.execute("SELECT thumbnail_url FROM server_settings WHERE server_id = ?", (server_id,))
        result = self.cursor.fetchone()
        thumbnail_url = result[0] if result else "https://example.com/default_thumbnail.jpg"

        embed = discord.Embed(
            title="Leave",
            description=f"Goodbye {member.mention}, I hope you had a very good time on the server!",
            color=discord.Color.purple()
        )
        embed.set_image(url=thumbnail_url)

        if member.guild.system_channel:
            await member.guild.system_channel.send(embed=embed)
        else:
            default_channel = discord.utils.get(member.guild.channels, name="☂┃terms")  # Replace with your channel name
            if default_channel:
                await default_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Leave(bot))

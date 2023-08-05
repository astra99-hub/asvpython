import discord
from discord.ext import commands
import sqlite3
from discord.ext.commands import slash_command


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thumbnail_url = ""
        print("Welcome db 'sqlite3.connect' is ready.")
        self.conn = sqlite3.connect("data/ok.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS server_settings (server_id INTEGER PRIMARY KEY, thumbnail_url TEXT, role_id INTEGER)"
        )
        self.conn.commit()

    @slash_command(description="create a welcome channel.")
    @commands.has_permissions(administrator=True)
    async def setup_welcomer(self, ctx, channel: discord.TextChannel, role: discord.Role, thumbnail_url="https://example.com/default_thumbnail.jpg"):
        self.cursor.execute(
            "INSERT OR REPLACE INTO server_settings (server_id, thumbnail_url, role_id) VALUES (?, ?, ?)",
            (ctx.guild.id, thumbnail_url, role.id)
        )
        self.conn.commit()
        await ctx.respond(f"Welcome channel has been set to {channel.mention} with the role '{role.name}'", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.cursor.execute("SELECT thumbnail_url, role_id FROM server_settings WHERE server_id = ?", (member.guild.id,))
        result = self.cursor.fetchone()
        thumbnail_url = result[0] if result else "https://example.com/default_thumbnail.jpg"
        role_id = result[1] if result else None
        print(role_id)

        if role_id is not None:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"Added role '{role.name}' to {member.name}")
                except discord.Forbidden:
                    print(f"Missing permissions to add role '{role.name}' to {member.name}")
                except discord.HTTPException as e:
                    print(f"Error adding role '{role.name}' to {member.name}: {e}")
            else:
                print("Role not found. Make sure the role ID is correct.")
        else:
            print("Role not found. Make sure the role ID is correct.")

        embed = discord.Embed(
            title="Welcome",
            description=f"Hello {member.mention}, have a great time!",
            color=discord.Color.purple()
        )
        embed.set_image(url=thumbnail_url)

        if member.guild.system_channel:
            await member.guild.system_channel.send(embed=embed)
        else:
            default_channel = discord.utils.get(member.guild.channels, name="🛬┃willkommen")
            if default_channel:
                await default_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcome(bot))

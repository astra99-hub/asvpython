import discord
from discord.commands import slash_command, Option
from discord.ext import commands
import asyncio
from datetime import datetime
import os
import sqlite3
import  aiosqlite






class TicketSystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("Ticket.db")
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticket_settings (
                guild_id INTEGER PRIMARY KEY,
                category_team INTEGER,
                category_help INTEGER,
                category_other INTEGER,
                role_team INTEGER,
                role_high_team INTEGER,
                role_fraktionsantrag INTEGER
            )
        ''')
        self.conn.commit()

    def get_guild_settings(self, guild_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM ticket_settings WHERE guild_id = ?', (guild_id,))
        return c.fetchone()

    def save_guild_settings(self, guild_id, category_team, category_help, category_other,
                            role_team, role_high_team, role_fraktionsantrag):
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO ticket_settings (guild_id, category_team, category_help, category_other,
                                                    role_team, role_high_team, role_fraktionsantrag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (guild_id, category_team, category_help, category_other, role_team, role_high_team, role_fraktionsantrag))
        self.conn.commit()


logchannelid = 1135585816400367627 # Logs
teamroleID = 1135585813506297941 # Team Rolle
teamroleID2 = 1135585813506297941 # high team rolle
teamroleID3 = 1135585813506297941
categoryt = 1136379084964904980 # Kategorie Team Bewerbung
categoryh = 1135585814684897331 # Kategorie Hilfe
categoryf = 1135585814684897332 # Kategorie discord bot helfe
feedbackch = 1136562290632687666  # Feedback Channel Ping
class ticketdropcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(dropdownticket(self.bot))
        self.bot.add_view(TicketClose(self.bot))



    @slash_command(description="Erstelle ein Ticket System")
    @discord.default_permissions(administrator=True, kick_members=True)
    async def ticketsystem(self, ctx):
        ticketsystem = discord.Embed(
            title="**__Ticket System__**",
            description="Wenn du ein Problem hast, bewerben, fraktionsantrag machen willst öffne gerne ein Ticket",
            color=discord.Color.blue()
        )
        ticketsystem.add_field(name="**__Wichtig__**", value="**Bitte pinge keine Teammitglieder!**")
        ticketsystem.set_image(
            url="https://cdn.discordapp.com/attachments/1077917507568013332/1078262295798497280/long.gif")
        ticketsystem.set_thumbnail(url=self.bot.user.display_avatar.url)
        ticketsystem.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

        erfolg = discord.Embed(
            title="Ticket System erfolgreich erstellt!"
        )

        await ctx.channel.send(embed=ticketsystem, view=dropdownticket(self.bot))
        await ctx.respond(embed=erfolg, ephemeral=True)


def setup(bot):
    bot.add_cog(ticketdropcommand(bot))


class dropdownticket(discord.ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout=None)

    options = [
        discord.SelectOption(label="Teambewerbung", description="Bewerbe dich im Team", emoji="🎫", value="1"),
        discord.SelectOption(label="Discord Bots Support", description="discord bot helfe", emoji="🎫", value="2"),
        discord.SelectOption(label="Support Ticket", description="mach ein Support", emoji="🎫", value="5"),
    ]

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder="Was möchtest du?",
        options=options,
        custom_id="drop"
    )
    async def select_callback(self, select, interaction):
        if "1" in select.values:
            teamroleid = teamroleID2
            categoryid = categoryt
            teamroletag = f"<@&{teamroleID}>"

            cat = self.bot.get_channel(categoryid)
            interaction.message.author = interaction.user
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(teamroleID2): discord.PermissionOverwrite(read_messages=True,
                                                                                     send_messages=True),

                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            ticket_channel1 = await interaction.guild.create_text_channel(
                f'🎫・{interaction.user}',
                category=cat,
                overwrites=overwrites
            )
            ticketchannelem1 = discord.Embed(
                title=f"Willkommen in deinem Ticket {interaction.user}",
                description=f"Um zu beginnen folge den Schritten.\n"
                            f"Erkläre als was genau du dich bewerben möchtest und warte auf eine Antwort.\n"
                            f"In der Zwischenzeit kannst du die Regeln durchlesen.\n"
                            f"▬▬▬▬▬ **Team Bewerbung** ▬▬▬▬▬\n"
                            f"Unser {teamroletag} wird dir gleich helfen.",
                color=discord.Color.purple()
            )
            ticketchannelem1.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

            await ticket_channel1.send(embed=ticketchannelem1, view=TicketClose(self.bot))
            await interaction.response.send_message(f"Dein Ticket wurde erstellt! {ticket_channel1.mention}",
                                                    ephemeral=True)
            msg = await ticket_channel1.send(f"{teamroletag}")
            await asyncio.sleep(3)
            await msg.delete()

        if "2" in select.values:
            teamroleid = teamroleID
            categoryid = categoryh
            teamroletag = f"<@&{teamroleID}>"

            cat = self.bot.get_channel(categoryid)
            interaction.message.author = interaction.user

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(teamroleid): discord.PermissionOverwrite(read_messages=True,
                                                                                    send_messages=True),

                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            ticket_channel = await interaction.guild.create_text_channel(
                f'🎫・{interaction.user}',
                category=cat,
                overwrites=overwrites
            )
            ticketchannelem = discord.Embed(
                title=f"Willkommen in deinem Ticket {interaction.user}",
                description=f"Um zu beginnen folge den Schritten.\n"
                            f"Erkläre was genau du möchtest und warte auf eine Antwort.\n"
                            f"In der Zwischenzeit kannst du die Regeln durchlesen.\n"
                            f"▬▬▬▬▬ **Hilfe** ▬▬▬▬▬\n"
                            f"Unser {teamroletag} wird dir gleich helfen.",
                color=discord.Color.blue()
            )
            ticketchannelem.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

            await ticket_channel.send(embed=ticketchannelem, view=TicketClose(self.bot))
            msg = await ticket_channel.send(f"{teamroletag}")
            await interaction.response.send_message(f"Dein Ticket wurde erstellt! {ticket_channel.mention}",
                                                    ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()

        if "5" in select.values:
            teamroleid = teamroleID3
            categoryid = categoryf
            teamroletag = f"<@&{teamroleID}>"

            cat = self.bot.get_channel(categoryid)
            interaction.message.author = interaction.user

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(teamroleid): discord.PermissionOverwrite(read_messages=True,
                                                                                    send_messages=True),

                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            ticket_channel = await interaction.guild.create_text_channel(
                f'🎫・{interaction.user}',
                category=cat,
                overwrites=overwrites
            )
            ticketchannelem = discord.Embed(
                title=f"Willkommen in deinem Ticket {interaction.user}",
                description=f"Um zu beginnen folge den Schritten.\n"
                            f"Für welche Fraktion willst du ein Antrag machen? und warte auf eine Antwort.\n"
                            f"In der Zwischenzeit kannst du die Regeln durchlesen.\n"
                            f"▬▬▬▬ **Fraktionsantrag** ▬▬▬▬\n"
                            f"Unser {teamroletag} wird dir gleich helfen.",
                color=discord.Color.purple()
            )
            ticketchannelem.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

            await ticket_channel.send(embed=ticketchannelem, view=TicketClose(self.bot))
            msg = await ticket_channel.send(f"{teamroletag}")
            await interaction.response.send_message(f"Dein Ticket wurde erstellt! {ticket_channel.mention}",
                                                    ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()


class Logger:
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel

    async def create_log_file(self):
        with open(f"Log {self.channel.name}.txt", "w", encoding="utf-8") as f:
            f.write(f'Ticket " {self.channel.name}"\n\n')
            f.write("-----------------------------------------\n")
            messages = await self.channel.history(limit=69420).flatten()
            for i in reversed(messages):
                f.write(f"{i.created_at}: {i.author}: {i.author.id}: {i.content}\n")
            f.write("-----------------------------------------\n\n")
            if len(messages) >= 69420:
                f.write(
                    f"Es wurden mehr als 69420 Nachrichten in diesen Channel eingesendet. Aus Speicher-Gründen wurden "
                    f"nur die letzten 69420 Nachrichten geloggt.")
            else:
                f.write(f"Anzahl an Nachrichten: {len(messages)}")

    async def send_log_file(
            self,
            channel: discord.TextChannel
    ):
        await channel.send(
            files=[discord.File(f"Log {self.channel.name}.txt", filename=f"{self.channel.name}.txt")]
        )
        os.remove(
            f"Log {self.channel.name}.txt"
        )


class TicketClose(discord.ui.View):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, emoji=None, custom_id="ticketclose")
    async def button_callback2(self, button, interaction):
        for child in self.children:
            child.disabled = True

        closeem = discord.Embed(
            title="Ticket wird geschlossen",
            description=f"Anfrage von: {interaction.user.mention}\n"
                        f"\n"
                        f"Das Ticket wird in wenigen Sekunden gelöscht!\n"
                        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                        f"Lass doch gerne ein <#{feedbackch}> da!\n",
            color=discord.Color.purple()
        )
        closeem.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

        logchannel = interaction.guild.get_channel(logchannelid)
        logger = Logger(interaction.channel)
        await logger.create_log_file()
        await logger.send_log_file(logchannel)
        embed2 = discord.Embed(
            title=f"Chat erfolgreich exportiert",
            description=f"Geschlossen von {interaction.user.mention} 🔒\n```{interaction.channel.name}```",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed2.set_footer(icon_url=self.bot.user.display_avatar, text=self.bot.user)
        embed2.set_image(
            url="https://cdn.discordapp.com/attachments/1077917507568013332/1078262295798497280/long.gif")
        await logchannel.send(embed=embed2)

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=closeem)
        await asyncio.sleep(10)
        await interaction.channel.delete()

    @discord.ui.button(label="Regeln", style=discord.ButtonStyle.gray, emoji="📕", custom_id="ticketrule")
    async def button_callback3(self, button, interaction):
        ruleem = discord.Embed(
            title="**__REGELN__**",
            description="**``1.`` Nutze keine Beleidigungen**\n"
                        "**``2.`` Sei freundlich und gedulig**\n",
            color=discord.Color.purple()
        )
        ruleem.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=ruleem, ephemeral=True)


class ModalRateUs(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        super().__init__(
            discord.ui.InputText(
                label="Feedback",
                placeholder="..",
                style=discord.InputTextStyle.short
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        channel = self.bot.get_channel(logchannelid)

        embed = discord.Embed(
            title=f"Feedback",
            description=f"{self.children[0].value}\n"
                        f"\n"
                        f"> Feedback von: {interaction.user.mention}",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.set_footer(icon_url=self.bot.user.display_avatar.url, text=self.bot.user)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1077917507568013332/1078262295798497280/long.gif")

        await interaction.response.send_message("Feedback send!", ephemeral=True)
        await channel.send(embed=embed)
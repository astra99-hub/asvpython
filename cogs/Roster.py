import json
import uuid
from datetime import datetime

import aiosqlite
import discord
from discord.commands import slash_command
from discord.ext import commands
import asyncio


class SetRoster(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(roasterButtons())
            self.bot.add_view(ChannelSelect(None))
            self.bot.add_view(Roleselect(None))
            self.bot.add_view(ColorSelect(None))
            self.bot.add_view(RosterSelect())
            self.persistent_views_added = True

        async with aiosqlite.connect("data/roster.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS embeds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_id INTEGER,
                        code TEXT,
                        title TEXT,
                        embed JSON,
                        msg_id INTEGER,
                        build_id INTEGER,
                        guild_id INTEGER
                    )"""
                )

            await db.commit()

    @slash_command(name="roster", description="Erstelle ein Roster")
    @commands.has_permissions(administrator=True)
    async def roster(self, ctx: discord.ApplicationContext):
        await ctx.defer(invisible=True)

        embed = discord.Embed(
            title="📋 | Roster Setup",
            description="Hier kannst du ein paar Dinge machen",
            color=discord.Color.orange(),
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text=f"{ctx.guild.name}", icon_url=f"{self.bot.user.avatar.url}"
        )

        await ctx.respond(embed=embed, view=roasterButtons())


def setup(bot):
    bot.add_cog(SetRoster(bot))


class roasterButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.msg_id = None

    @discord.ui.button(
        label="Erstellen",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="roster_erstellen:btn",
    )
    async def erstellen_callback(
            self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        for btn in self.children:
            btn.disabled = True

        embed = discord.Embed(
            title="Default Title",
            description="Default Description",
        )

        await interaction.response.edit_message(view=self)
        msg = await interaction.channel.send(
            embed=embed, view=RosterSelect()
        )

        async with aiosqlite.connect("data/roster.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO embeds (build_id, guild_id) VALUES (?, ?)""",
                    (msg.id, interaction.guild.id)
                )
                await db.commit()


    @discord.ui.button(
        label="Bearbeiten",
        style=discord.ButtonStyle.blurple,
        emoji="📜",
        custom_id="roster_edit:btn",
    )
    async def bearbeiten_callback(
            self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_modal(LoadEmbed())

    @discord.ui.button(
        label="Löschen",
        style=discord.ButtonStyle.red,
        emoji="🔰",
        custom_id="roster_del:btn",
    )
    async def löschen_callback(
            self, button: discord.ui.Button, interaction: discord.Interaction
    ):

        await interaction.response.defer()
        async with aiosqlite.connect("data/roster.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('Select * FROM embeds')
                result = await cursor.fetchall()

            if result == None:
                em = discord.Embed(
                    title="📋 | Roster Setup",
                    description="Es wurden keine Roster gefunden",
                    color=discord.Color.orange(),
                )
                em.set_footer(
                    text=f"{interaction.guild.name}", icon_url=f"{interaction.user.avatar.url}"
                )
                await interaction.channel.send(embed=em)
                return

        counter = 0
        roster_list = []
        for i in result:
            code = i[2]
            msg_id = i[5]
            counter += 1

            roster_list.append(f"**{counter}.** Code: {code}\n Message ID: {msg_id}\n\n")

        em = discord.Embed(
            title="📋 | Roster Setup",
            description=f"{''.join(roster_list)}\n\n Bitte schreibe mir die Message ID des Rosters, welches du löschen möchtest",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        em.set_footer(
            text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
        )
        await interaction.channel.send(embed=em)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=500)
            msg1 = msg.content


        except asyncio.TimeoutError:
            em = discord.Embed(
                title="📋 | Roster Setup",
                description="Du hast zu lange gebraucht",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            em.set_footer(
                text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
            )
            await interaction.channel.send(embed=em)
            return

        if msg1.isdigit():

            async with aiosqlite.connect("data/roster.db") as db1:
                async with db1.cursor() as cursor:
                    await cursor.execute('SELECT * FROM embeds WHERE msg_id = ?', (msg1,))
                    result = await cursor.fetchone()
            if result == None:
                em = discord.Embed(
                    title="📋 | Roster Setup",
                    description="Diese Message ID existiert nicht",
                    color=discord.Color.orange(),
                )
                em.set_footer(
                    text=f"{interaction.guild.name}", icon_url=f"{interaction.user.avatar.url}"
                )
                await interaction.channel.send(embed=em)
                return

            db2 = await aiosqlite.connect("data/roster.db")
            async with db2.cursor() as cursor:
                await cursor.execute('SELECT channel_id FROM embeds WHERE msg_id = ?', (msg1,))
                id = await cursor.fetchone()

            channel_id = int(id[0])
            if channel_id == None:
                em = discord.Embed(
                    title="📋 | Roster Setup",
                    description="Dieser Channel existiert nicht mehr",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                em.set_footer(
                    text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
                )
                await interaction.channel.send(embed=em)
                return

            channel = interaction.guild.get_channel(channel_id)
            if channel == None:
                em = discord.Embed(
                    title="📋 | Roster Setup",
                    description="Dieser Channel existiert nicht mehr",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                em.set_footer(
                    text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
                )
                await interaction.channel.send(embed=em)
                return

            msg = await channel.fetch_message(int(msg1))
            if msg == None:
                em = discord.Embed(
                    title="📋 | Roster Setup",
                    description="Diese Message ID existiert nicht",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                em.set_footer(
                    text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
                )
                await interaction.channel.send(embed=em)
                return

            await msg.delete()
            async with aiosqlite.connect("data/roster.db") as db:
                async with db.cursor() as cursor:
                    await cursor.execute('DELETE FROM embeds WHERE msg_id = ?', (msg1,))
                    await db.commit()
                    em = discord.Embed(
                        title="📋 | Roster Setup",
                        description="Roster wurde gelöscht",
                        color=discord.Color.orange(),
                        timestamp=datetime.now()
                    )
                    em.set_footer(
                        text=f"{interaction.guild.name}", icon_url=f"{interaction.guild.icon}"
                    )
                    await interaction.channel.send(embed=em)
                    return



    @discord.ui.button(
        label="Codes",
        style=discord.ButtonStyle.blurple,
        emoji="📤",
        custom_id="roster_codes:btn",
    )
    async def codes_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
       async with aiosqlite.connect("data/roster.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("""SELECT channel_id, code, title FROM embeds""")
            result = await cursor.fetchall()

            if len(result) == 0:
                return await interaction.response.send_message(
                    "Es wurden keine Roster gefunden."
                )

            msg = "```yaml\n"
            for row in result:
                channel_id = row[0]
                channel = interaction.guild.get_channel(channel_id)

                if channel:
                    msg += "------------------\n"
                    msg += f"[✅] #{channel.name} | Code: {row[1]} | Title: {row[2]}\n"
                    msg += "------------------\n"

            msg += "```"
            await interaction.response.send_message(msg)


class LoadEmbed(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label=f"Code",
                placeholder="Enter your code here...",
                custom_id="input:code",
            ),
            title=f"Load Roaster",
            custom_id="persistent_modal:load_roaster",
            timeout=None,
        )

    async def callback(self, ctx: discord.Interaction):
        code = self.children[0].value
        async with aiosqlite.connect("data/roster.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT embed FROM embeds WHERE code = ?", (code,))
                result = await cursor.fetchone()
                if not result:
                    await ctx.response.send_message(
                        content="Dieser Code existiert nicht!"
                    )
                    return

                result_emb = json.loads(result[0])

                embed = discord.Embed.from_dict(result_emb)
                view = RosterSelect()

                await ctx.response.edit_message(embed=embed, view=view)


class RosterSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [
        discord.SelectOption(
            label="Title Hinzufügen",
            description="Füge einen Titel hinzu",
            emoji="📑",
        ),
        discord.SelectOption(
            label="Beschreibung Hinzufügen",
            description="Füge eine Beschreibung hinzu",
            emoji="📋",
        ),
        discord.SelectOption(
            label="Farbe Hinzufügen",
            description="Füge einen Farbe hinzu",
            emoji="🎨",
        ),
        discord.SelectOption(
            label="Thumbnail Hinzufügen",
            description="Füge ein Thumbnail hinzu",
            emoji="⚜️",
        ),
        discord.SelectOption(
            label="Image Hinzufügen",
            description="Füge ein Image hinzu",
            emoji="🔱",
        ),
        discord.SelectOption(
            label="Rollen Hinzufügen",
            description="Füge Rollen hinzu",
            emoji="🔴",
        ),
        discord.SelectOption(
            label="Roster Fertig",
            description="Sende dein Roster in ein Channel",
            emoji="💲",
        ),
    ]

    @discord.ui.select(
        placeholder="🀄️ | Erstelle dein Roster",
        min_values=1,
        max_values=1,
        options=options,
        custom_id="roster_select:select",
    )
    async def callback(
            self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        selected_option = select.values[0]
        if selected_option == "Title Hinzufügen":
            await interaction.response.send_modal(TitleModal())

        if selected_option == "Beschreibung Hinzufügen":
            await interaction.response.send_modal(DescriptionModal())

        if selected_option == "Farbe Hinzufügen":
            await interaction.response.send_message(
                view=ColorSelect(msg=interaction), ephemeral=True
            )

        if selected_option == "Thumbnail Hinzufügen":
            await interaction.response.send_modal(ThumbnailModal())

        if selected_option == "Image Hinzufügen":
            await interaction.response.send_modal(ImageModal())

        if selected_option == "Rollen Hinzufügen":
            await interaction.response.send_message(
                view=Roleselect(msg=interaction), ephemeral=True
            )

        if selected_option == "Roster Fertig":
            await interaction.response.send_message(
                view=ChannelSelect(msg=interaction), ephemeral=True
            )


class TitleModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label="Roaster Title",
                placeholder="Titel reinschreiben",
            ),
            title="Roaster Title",
        )

    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0].copy()

        embed.title = (
            self.children[0].value if self.children[0].value else "Kein Titel vorhanden"
        )

        await interaction.response.edit_message(embed=embed)


class DescriptionModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label="Roaster Beschreibung",
                placeholder="Beschreibung reinschreiben",
                style=discord.InputTextStyle.paragraph,
            ),
            title="Roaster Beschreibung",
        )

    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0].copy()

        embed.description = (
            self.children[0].value
            if self.children[0].value
            else "Keine Beschreibung vorhanden"
        )

        await interaction.response.edit_message(embed=embed)


class ThumbnailModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label="Roaster Thumbnail",
                placeholder="Thumbnail URL",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            title="Roaster Thumbnail",
        )

    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0].copy()

        thumbnail = self.children[0].value
        embed.set_thumbnail(url=thumbnail)

        await interaction.response.edit_message(embed=embed)


class ImageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            discord.ui.InputText(
                label="Roaster Image",
                placeholder="Image URL",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            title="Roaster Image",
        )

    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0].copy()

        image = self.children[0].value
        embed.set_image(url=image)

        await interaction.response.edit_message(embed=embed)


options = [
    discord.SelectOption(label="White", value="0xFFFFFF", emoji="⚪"),
    discord.SelectOption(label="Black", value="0x000000", emoji="⚫"),
    discord.SelectOption(label="Teal", value="0x1ABC9C", emoji="💠"),
    discord.SelectOption(label="Dark Teal", value="0x11806A", emoji="🌀"),
    discord.SelectOption(label="Green", value="0x2ECC71", emoji="🟢"),
    discord.SelectOption(label="Dark Green", value="0x1F8B4C", emoji="🍀"),
    discord.SelectOption(label="Blue", value="0x3498DB", emoji="🔵"),
    discord.SelectOption(label="Dark Blue", value="0x206694", emoji="📘"),
    discord.SelectOption(label="Purple", value="0x9B59B6", emoji="🟣"),
    discord.SelectOption(label="Dark Purple", value="0x71368A", emoji="🔮"),
    discord.SelectOption(label="Magenta", value="0xE91E63", emoji="🌸"),
    discord.SelectOption(label="Dark Magenta", value="0xAD1457", emoji="🎆"),
    discord.SelectOption(label="Yellow", value="0xFEE75C", emoji="💛"),
    discord.SelectOption(label="Gold", value="0xF1C40F", emoji="🌟"),
    discord.SelectOption(label="Orange", value="0xE67E22", emoji="🟠"),
    discord.SelectOption(label="Dark Orange", value="0xA84300", emoji="🍊"),
    discord.SelectOption(label="Red", value="0xE74C3C", emoji="🔴"),
    discord.SelectOption(label="Dark Red", value="0x992D22", emoji="🌹"),
    discord.SelectOption(label="Light Grey", value="0x979C9F", emoji="⚪"),
    discord.SelectOption(label="Dark Grey", value="0x607D8B", emoji="⚫"),
]


class ColorSelect(discord.ui.View):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🀄️ | Wähle eine Farbe",
        options=options,
        custom_id="editor_dropdown_color",
    )
    async def callback(self, select: discord.ui.Select, ctx: discord.Interaction):
        select.disabled = True
        emb = self.msg.message.embeds[0].copy()
        emb.color = int(select.values[0], 16)
        await self.msg.followup.edit_message(self.msg.message.id, embed=emb)
        await ctx.response.edit_message(view=self)


class Roleselect(discord.ui.View):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(timeout=None)

    @discord.ui.role_select(
        placeholder="Rollen Auswählen",
        min_values=1,
        max_values=5,
        custom_id="role_select:view",
    )
    async def role_callback(self, select, interaction):
        select.disabled = True
        emb = self.msg.message.embeds[0].copy()
        if len(select.values) == 25:
            await interaction.response.send_message(
                "Du kannst nur 25 Fields hinzufügen", ephemeral=True
            )
            return
        for role in select.values:
            emb.add_field(
                name=role.name,
                value="\n".join(
                    [f"> {member.mention} | `{member.id}`" for member in role.members]
                )
                      or "Keine Member mit dieser Rolle",
                inline=False,
            )

        await self.msg.followup.edit_message(self.msg.message.id, embed=emb)
        await interaction.response.edit_message(view=self)


async def check_code_exists(code):
    async with aiosqlite.connect("data/roster.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT code FROM embeds WHERE code = ?", (code,))
            result = await cursor.fetchone()
            return result is not None


class ChannelSelect(discord.ui.View):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(timeout=None)

    @discord.ui.channel_select(
        placeholder="📑 | Wähle ein Kanal",
        min_values=1,
        max_values=1,
        custom_id="channel_select:view",
        channel_types=[discord.ChannelType.text],
    )
    async def channel_callback(self, select, interaction):
        select.disabled = True
        channel = select.values[0]
        embed = self.msg.message.embeds[0].copy()

        try:
            async with aiosqlite.connect("data/roster.db") as db:
                async with db.cursor() as cursor:
                    embed_as_dict = self.msg.message.embeds[0].to_dict()
                    code = uuid.uuid4().hex[:20]
                    exists = await check_code_exists(code)

                    while exists:
                        code = uuid.uuid4().hex[:20]
                        exists = await check_code_exists(code)

                    msg = await channel.send(embed=embed)
                    await interaction.response.edit_message(
                        view=self,
                    )

                    await cursor.execute(
                        """INSERT INTO embeds (channel_id, code, title, embed, msg_id, guild_id) VALUES (?, ?, ?, ?, ?, ?)""",
                        (channel.id, code, embed.title, json.dumps(embed_as_dict), msg.id, interaction.guild.id),
                    )
                    await db.commit()

                    await interaction.followup.send(
                        f"Das Roster wurde in {channel.mention} gesendet und es wurde unter dem Code `{code}` gespeichert.",
                        ephemeral=True,
                    )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Ich habe keine Berechtigung, um das Embed in den ausgewählten Channel zu senden.",
                ephemeral=True,
            )
        except discord.HTTPException:
            await interaction.response.send_message(
                "Ein Fehler ist beim Senden des Embeds aufgetreten.", ephemeral=True
            )
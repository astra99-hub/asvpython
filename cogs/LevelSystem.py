import discord
from discord.ext import commands
from discord.commands import slash_command

import aiosqlite
import random

from easy_pil import load_image_async, Editor, Font, Canvas


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "data/level.db"
        print("level db 'sqlite3.connect' is ready.")

    @staticmethod
    def get_level(xp):
        lvl = 1
        amount = 100

        while True:
            xp -= amount
            if xp < 0:
                return lvl
            lvl += 1
            amount += 100

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
                )"""
            )

    async def check_user(self, user_id):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            await db.commit()

    async def get_xp(self, user_id):
        await self.check_user(user_id)
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()

        return result[0] if result else 0

    async def get_next_level_xp(self, level):
        return level * 100

    async def get_remaining_xp(self, user_id):
        await self.check_user(user_id)
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()

        if result:
            xp = result[0]
            current_level = self.get_level(xp)
            next_level_xp = await self.get_next_level_xp(current_level)
            remaining_xp = next_level_xp - xp
            return remaining_xp if remaining_xp >= 0 else 0
        else:
            return None

    async def get_user_leaderboard_rank(self, user_id):
        counter = 1
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(
                    "SELECT user_id FROM users WHERE msg_count > 0 ORDER BY xp DESC"
            ) as cursor:
                async for uid, in cursor:
                    if uid == user_id:
                        return counter
                    counter += 1
        return None

    async def check_level_up(self, message, xp_gain):
        user_id = message.author.id
        old_xp = await self.get_xp(user_id)
        new_xp = old_xp + xp_gain

        old_level = self.get_level(old_xp)
        new_level = self.get_level(new_xp)

        if old_level < new_level:
            role_rewards = {
                1: 1136583141549690891,   # Role ID for level 1
                2: 1136583200316084294,   # Role ID for level 2
                3: 1136583248303112255,  # Role ID for level 3
                4: 1136583505829175306,  # Role ID for level 4
                5: 1136583628642582561,  # Role ID for level 5
                10: 1136583763145539666,  # Role ID for level 25
                15: 1136583900970356776,  # Role ID for level 30
                20: 1136583986659991653,  # Role ID for level 35
                30: 1136584070541869087,  # Role ID for level 100
                40: 1136584151940731000,  # Role ID for level 100
                50: 1136584265451192391,  # Role ID for level 100
                75: 1136584391422918686,  # Role ID for level 100
                100: 1136584462877081610  # Role ID for level 100

            }

            role_id = role_rewards.get(new_level)
            if role_id is not None:
                role = message.guild.get_role(role_id)
                await message.author.add_roles(role)
                await message.channel.send(f"Level Up! Du hast die Rolle {role.mention} erhalten!")


        # Update the user's XP in the database
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("UPDATE users SET msg_count = msg_count + 1, xp = ? WHERE user_id = ?", (new_xp, user_id))
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        xp_gain = random.randint(10, 20)

        await self.check_user(message.author.id)
        await self.check_level_up(message, xp_gain)

    @slash_command(description="Frage deine Rankdaten ab")
    async def rank(self, ctx):
        xp = await self.get_xp(ctx.author.id)
        lvl = self.get_level(xp)
        user_leaderboard_rank = await self.get_user_leaderboard_rank(ctx.author.id)
        background = Editor("img/level.jpg").resize((934, 282))
        avatar = await load_image_async(ctx.author.display_avatar.url)
        circle_avatar = Editor(avatar).resize((200, 200)).circle_image()
        background.paste(circle_avatar, (25, 25))

        text_user_name = Font.poppins(size=50, variant="bold")
        text_level = Font.poppins(size=40, variant="bold")
        background.text((750, 20), f"Level {lvl}", color="white", font=text_level)
        background.text((260, 140), f"{ctx.author.display_name}", color="white", font=text_user_name)
        background.bar(
            (250, 180),
            max_width=650,
            height=40,
            percentage=(xp / (lvl * 100)) * 100,
            fill="#003C98",
            radius=20,
        )

        text_xp_level = Font.poppins(size=30, variant="bold")
        next_level_xp = await self.get_next_level_xp(lvl)
        background.text((750, 150), f"{xp}/{next_level_xp}", color="white", font=text_xp_level)

        if user_leaderboard_rank is not None:
            text_leaderboard = Font.poppins(size=40, variant="bold")
            background.text((550, 20), f"Rank {user_leaderboard_rank}", color="white", font=text_leaderboard)

        file = discord.File(fp=background.image_bytes, filename='level.jpg')
        await ctx.respond(file=file)

    @slash_command()
    async def leaderboard(self, ctx):
        desc = ""
        counter = 1
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(
                    "SELECT user_id, xp FROM users WHERE msg_count > 0 ORDER BY xp DESC LIMIT 10"
            ) as cursor:
                async for user_id, xp in cursor:
                    level = self.get_level(xp)
                    desc += f"{counter}. <@{user_id}> - Level {level} - {xp} XP\n"
                    counter += 1

        embed = discord.Embed(
            title="Rangliste",
            description=desc,
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(LevelSystem(bot))
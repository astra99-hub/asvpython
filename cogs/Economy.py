import discord
import ezcord
import datetime
import random
import asyncio
import json
import aiosqlite
import sqlite3
import os
import asyncpraw

from discord.ext import commands
from datetime import datetime
from discord.commands import slash_command, Option


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = "data/main.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS bank(wallet INTEGER, bank INTEGER, maxbank INTEGER, user INTEGER)")
            await db.commit()

    async def create_balance(self, user):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("INSERT INTO bank VALUES(?, ?, ?, ?)", (0, 100, 500, user.id))
            await db.commit()
            return

    async def get_balance(self, user):
        async with aiosqlite.connect(self.db) as db:
            cursor = await db.execute("SELECT wallet, bank, maxbank FROM bank WHERE user = ?", (user.id,))
            data = await cursor.fetchone()
            if data is None:
                await self.create_balance(user)
                return 0, 100, 500
            wallet, bank, maxbank = data[0], data[1], data[2]
            return wallet, bank, maxbank

    async def update_wallet(self, user, amount: int):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("UPDATE bank SET wallet = wallet + ? WHERE user = ?", (amount, user.id))
            await db.commit()

    @slash_command(description="Check balance of yourself or another member.")
    async def balance(self, ctx, member: Option(discord.Member) = None):
        if not member:
            member = ctx.author
        wallet, bank, maxbank = await self.get_balance(member)
        em = discord.Embed(title=f"{member.name}'s Balance")
        em.add_field(name="Wallet", value=wallet)
        em.add_field(name="Bank", value=f"{bank}/{maxbank}")
        await ctx.respond(embed=em)


def setup(bot):
    bot.add_cog(Economy(bot))

import asyncio
from .utils import checks

from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.has_role("Bot Developer")
    @commands.command()
    async def shutdown(self, ctx):
        """Shuts off the bot"""
        await ctx.send("Shutting down...")
        exit()

def setup(bot):
    bot.add_cog(Admin(bot))
import asyncio
from .utils import checks

from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.has_role("bot master")
    @commands.command()
    async def ping(self):
        """Replies with a pong."""
        return await self.bot.say("pong")

def setup(bot):
    bot.add_cog(Ping(bot))

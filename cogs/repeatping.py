import asyncio
from .utils import checks

from discord.ext import commands

class RepeatPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @checks.has_role("bot master")
    @commands.command()
    async def repeat_ping(self):
        """Replies with a pong every 10 seconds."""
        self.running = True
        while self.running:
            await self.bot.say("pong")
            await asyncio.sleep(10)
    
    @checks.has_role("bot master")
    @commands.command()
    async def stop_ping(self):
        self.running = False

def setup(bot):
    bot.add_cog(RepeatPing(bot))

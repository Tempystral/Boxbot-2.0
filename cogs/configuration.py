import asyncio
from cogs.utils import checks

from discord.ext import commands
from utils.configmanager import ConfigManager

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = ConfigManager()

    @commands.has_any_role(["Bot Developer"])
    @commands.group(pass_context=True, aliases=["settings", "config"])
    async def configuration(self, context):
        if context.invoked_subcommand is None:
            await context.send("Not enough arguments!")
    
    @configuration.command()
    async def update(self, context):
        
        pass

    @configuration.command()
    async def ping(self, context):
        """Replies with a pong."""
        await context.send("pong")

def setup(bot):
    bot.add_cog(Config(bot))

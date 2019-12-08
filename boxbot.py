import json
import os

from discord.ext import commands
from utils import boxconfig, logger


# BoxBot extends commands.Bot, which extends discord.Client
class BoxBot(commands.Bot):
    def __init__(self):
        self.config = boxconfig.config
        super().__init__( command_prefix = self.config.get('command_prefix', '!') )
        for ext in self.config.get('extensions', []):
            self.load_extension(ext)

    async def on_ready(self):
        loginUsrMsg = f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}"
        loginSvrMsg = "Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds)))
        logger.info(loginUsrMsg)
        logger.info(loginSvrMsg)

    def run(self, *args, **kwargs):
        super().run(self.config['token'], reconnect=True)

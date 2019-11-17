import json, os, anyconfig

from discord.ext import commands

# BoxBot extends commands.Bot, which extends discord.Client
class BoxBot(commands.Bot):
    def __init__(self):
        #with open('./config/config.json') as configfile:
        self.config = anyconfig.load("./config/settings.toml") #json.load(configfile)
        # Default command prefix is !
        super().__init__( command_prefix = self.config.get('command_prefix', '!') )
        for ext in self.config.get('extensions', []):
            self.load_extension(ext)

    async def on_ready(self):
        print(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
        print("Logged into guilds:\n\t{guilds}"
              .format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

    def run(self, *args, **kwargs):
        super().run(self.config['token'], reconnect=True)

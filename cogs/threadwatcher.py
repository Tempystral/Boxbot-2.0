import os, asyncio

import cogs.utils.checks as checks
from discord.ext import commands
from watcher.boardwatcher2 import BoardWatcher
from utils import boxconfig, logger


def find_role(guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return role
    return None


class ThreadWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watcher = BoardWatcher(patternfile=boxconfig.get("boardwatcher.patternfile"),
                                    regex=boxconfig.get("boardwatcher.regex"))
        self.active = False
        self.interval = 300
        self._role = None
        self._notify_channel = None

    async def _update(self):
        """Update the boardwatcher"""
        threads = await self.watcher.update()
        return threads

    async def _getNewThreads(self):
        """Retrieve new threads from boardwatcher"""
        threads = await self._update()
        if len(threads) > 0:
            urls = [f"{thread.url}" for thread in threads]
            logger.info(f"New threads: {urls}")
            await self._notify_channel.send("{role} Found {n} new threads(s):\n{ts}"
                               .format(role = self._role.mention, n=len(urls), ts="\n".join(urls)))
        else:
            logger.debug("No new threads")
        return len(threads)

    async def _start(self, *, channel_id: int = None, role_name: str = None):
        """Begin checking for threads"""
        if channel_id:
            self._notify_channel = self.bot.get_channel(channel_id)
        elif self._notify_channel is None:
            channel_id = int(boxconfig.get('boardwatcher.notifychannel'))
            self._notify_channel = self.bot.get_channel(channel_id)
        if self._notify_channel is None:
            logger.error("No notification channel set")
            return

        if role_name:
            self._role = find_role(self._notify_channel.guild, role_name)
        elif self._role is None:
            role_name = boxconfig.get('boardwatcher.notifyrole')
            self._role = find_role(self._notify_channel.guild, role_name)
        if self._role is None:
            logger.warning("No notification role set")

        self.active = True
        while self.active:
            logger.debug("Started checking for threads")
            await self._getNewThreads()
            await asyncio.sleep(self.interval)

    @commands.Cog.listener()
    async def on_ready(self):
        await self._start()

    @checks.in_guild(126921614603452416)
    @checks.has_role("Bot Developer")
    @commands.group(pass_context=True, aliases=["tw"])
    async def threadwatcher(self, context):
        if context.invoked_subcommand is None:
            await context.send("Not enough arguments!")

    @checks.has_role("Bot Developer")
    @threadwatcher.command()
    async def start(self, context):
        """Begin checking for threads"""
        if self.active:
            await context.send("Already checking for threads.")
            return

        asyncio.create_task(self._start())
        await context.send("Started checking for threads.")

    @checks.has_role("Bot Developer")
    @threadwatcher.command()
    async def stop(self, context):
        """Stop checking for new threads"""
        if not self.active:
            return
        self.active = False
        await context.send("Stopped checking for threads.")

    @threadwatcher.command()
    async def check(self, context):
        """Manually check for new threads"""
        i = await self._getNewThreads()
        if i == 0:
            await context.send("No new threads.")

    @checks.has_role("Bot Developer")
    @threadwatcher.command()
    async def reset(self, context):
        """Manually clear tracked threads"""
        self.watcher.setTrackedThreads({})
        await context.send("Tracked threads reset.")
    
    @threadwatcher.command()
    async def tracked(self, context):
        await context.send("\n".join(f"{i.url}" for i in self.watcher.getTrackedThreads())
                            or "Not currently tracking any threads")
    
    # To do: Change this to let it accept a full message as the pattern
    @threadwatcher.command()
    async def addpattern(self, context, pattern):
        valid = self.watcher.addNewPattern(pattern)
        if valid:
            await context.send(f"Added pattern to list: {pattern}")
        else:
            await context.send(f"Pattern \"{pattern}\" not valid." +
                                "\nPatterns must be of the form " +
                                "``phrase1, phrase2, phrase3 | arg1, arg2 | board1, board2, board3``")

    @threadwatcher.command()
    async def show_patterns(self, context):
        patterns = self.watcher.getPatterns() or {}
        exclude_patterns = self.watcher.getExcludePatterns() or {}
        if len(patterns) == 0 and len(exclude_patterns) == 0:
            context.send("There are no patterns in the database.")
            return
        response = ""
        for board in patterns:
            response += f"In /{board}/, include: " + ", ".join(
                    [f"``{p.pattern}``" for p in patterns[board]]) + "\n"
        for board in exclude_patterns:
            response += f"In /{board}/, exclude: " + ", ".join(
                    [f"{p.pattern}" for p in exclude_patterns[board]]) + "\n"
        
        await context.send(f"Here is the current list of patterns:\n{response}")
        
    @threadwatcher.command()
    async def setnotifyrole(self, context, role_name):
        """Set role to notify"""
        guild = context.message.guild
        role = find_role(guild, role_name)
        if role:
            self._role = role
            await context.send(f"I'll notify {role_name} of new threads.")
            return
        await context.send("No such role found")
        logger.warning(f"Tried to set notification role \"{role_name}\", but no such role was found")

    @threadwatcher.command()
    async def setnotifychannel(self, context, channelName):
        """Set channel to notify"""
        g = context.message.guild
        for channel in g.channels:
            if channel.name == channelName:
                self._notify_channel = channel
                await context.send(f"I'll post new threads to {channel.mention}.")
                return
        await context.send(f"Channel \"{channelName}\" not found")
        logger.warning(f"Tried to set notification channel \"{channelName}\", but no such channel was found")


def setup(bot):
    bot.add_cog(ThreadWatcher(bot))

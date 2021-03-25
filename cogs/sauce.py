import asyncio
import re

import aiohttp
import discord
from discord.ext import commands

import ladles
from ladles.ehentai import EHentaiApiError
from utils import boxconfig, logger


class Sauce(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        extractors = [getattr(ladles, name)() for name in boxconfig.get("ladles")]
        self._extractors = [(re.compile(e.pattern), e) for e in extractors]
        self._session = aiohttp.ClientSession()

    def __remove_spoilered_text(self, message) -> str:
        '''Quick hacky way to remove spoilers, doesn't handle ||s in code blocks'''
        strs = message.content.split('||')
        despoilered = ''.join(strs[::2]) # Get every 4th string
        despoilered += strs[-1] if len(strs) % 2 == 0 else ''
        return despoilered

    async def __suppressMessage(self, message:discord.Message):
        try:
            await message.edit(flags=4)
        except discord.errors.Forbidden as e:
            if e.code == 50013:
                # 50013 just means we don't have manage_messages perms here. Not worth spamming logs for.
                pass
            else:
                logger.warning(f"Couldn't suppress embed in {message}'s message: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        if message.author.bot:
            return

        # Filter and extract links from message
        despoilered_message = self.__remove_spoilered_text(message)
        links = []
        for pattern, extractor in self._extractors:
            matches = pattern.finditer(despoilered_message)
            if matches:
                links.extend([(match, extractor) for match in matches])

        links.sort(key=lambda x: x[0].start())
        
        logger.debug(f"Link(s) matched: {links}")

        for match, extractor in links[:3]:
            image_limit = 3

            try:
                info = await extractor.extract(match[0], self._session) # Exceptions which cause the function to fail should return None
            except EHentaiApiError as ehx:
                logger.warning(ehx.message)
                continue
            if info is None:
                continue

            # Break out data into chunks
            images = info.get('images') or []
            total_images = info.get('count') or len(images) if images else 0
            embed_info = {k: info[k] for k in info.keys() & ['title', 'description', 'thumbnail', "url"]}
            author_info = {k: info[k] for k in info.keys() & ['name', 'icon_url']}

            # Create embed
            embed = None

            if embed_info:
                embed = discord.Embed(**embed_info)
            if embed:
                if info.get('thumbnail'):
                    embed.set_thumbnail(url=info['thumbnail'])
                if author_info:
                    embed.set_author(**author_info)

            # TODO: handle embedding better, especially when the first post is already embedded by discord

            response_text = ''
            if total_images > 1:
                response_text += f'Set contains {total_images} images.\n'
            if info.get('url') and embed is None:
                response_text += info['url'] + '\n'

            # Suppress original embed when BoxBot creates its own
            if embed is not None and len(images[:image_limit]) > 0:
                await self.__suppressMessage(message)

            if extractor.hotlinking_allowed: # Posts the next x images from an album if the site supports it
                if embed is not None:
                    embed.set_image(url=images[0]) if images else 0
                    await message.channel.send(embed=embed)

                    images = images[1:] # Count down images and add to list for posting
                    image_limit -= 1
                if len(images[:image_limit]) > 0:
                    response_text += '\n'.join(images[:image_limit])
                if len(response_text) > 0:
                    await message.channel.send(response_text)

            else: # Some sites like Pixiv do not allow image hotlinking (easily)
                if embed is not None:
                    #embed.set_image(url=images[0]) if images else 0
                    await message.channel.send(embed=embed)
                files = [await extractor.download(i, self._session) for i in images[:image_limit]]
                if response_text or files:
                    await message.channel.send(response_text, files=[discord.File(f) for f in files])
    
    def cog_unload(self):
        asyncio.get_event_loop().create_task(self._session.close())

def setup(bot):
    bot.add_cog(Sauce(bot))

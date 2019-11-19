import re
import asyncio
import aiohttp
import discord
from discord.ext import commands

from ladles import *

class Sauce(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._extractors = [ESixPool(), ESixPost(), Furaffinity(), Pixiv()] # Twitter() is unnecessary as of 18/11/2019
        self._session = aiohttp.ClientSession()

    def __remove_spoilered_text(self, message) -> str:
        '''Quick hacky way to remove spoilers, doesn't handle ||s in code blocks'''
        strs = message.content.split('||')
        despoilered = ''.join(strs[::2]) # Get every 4th string
        despoilered += strs[-1] if len(strs) % 2 == 0 else ''
        return despoilered

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        if message.author.bot:
            return

        # Filter and extract links from message
        despoilered_message = self.__remove_spoilered_text(message)
        links = []
        for extractor in self._extractors:
            matches = extractor.findall(despoilered_message)
            if matches:
                links.extend([(match, extractor) for match in matches])
                break # Assumption: We won't match more than one site to a link, so it's safe to break as soon as we get a match.

        links.sort(key=lambda x: x[0].start())

        for match, extractor in links[:3]:
            image_limit = 4
            info = await extractor.extract(match, self._session)
            if info is None:
                continue
            images = info['images']
            total_images = info.get('count') or len(images)

            embed_info = {k: info[k] for k in info.keys() & ['title', 'description']}
            author_info = {k: info[k] for k in info.keys() & ['name', 'icon_url']}
            embed = None
            if embed_info:
                embed = discord.Embed(**embed_info)
            if author_info and embed is not None:
                embed.set_author(**author_info)

            # TODO: handle embedding better, especially when the first post is already embedded by discord
            if extractor.skip_first:
                if len(images) == 1:
                    continue
                images = images[1:]
                image_limit -= 1

            if extractor.hotlinking_allowed:
                if embed is not None:
                    embed.set_image(url=images[0])
                    await message.channel.send(embed=embed)
                    images = images[1:]
                    image_limit -= 1
                if len(images[:image_limit]) > 0:
                    # TODO: give a better message in cases where we don't post everything
                    await message.channel.send(f'Set contains {total_images} images:\n' + '\n'.join(images[:3]))
            else:
                if embed is not None:
                    await message.channel.send(embed=embed)
                if len(images[:image_limit]) > 1:
                    response_message = f'Set contains {total_images} images'
                else:
                    response_message = ''
                    await message.channel.send(f'Set contains {total_images} images')
                image_file = await extractor.download(images[0], self._session)
                await message.channel.send(response_message, file=discord.File(image_file))
                for i in images[1:image_limit]:
                    image_file = await extractor.download(i, self._session)
                    await message.channel.send(file=discord.File(image_file))
    
    def cog_unload(self):
        asyncio.get_event_loop().create_task(self._session.close())

def setup(bot):
    bot.add_cog(Sauce(bot))

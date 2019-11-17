from typing import Dict, Iterable, Match, Pattern, Optional
from abc import ABC, abstractmethod
import re
import json

from discord import Embed
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup


class BaseInfoExtractor(ABC):
    '''
    Abstract parent class for extractors
    '''
    pattern: Pattern
    hotlinking_allowed: bool
    skip_first: bool

    @abstractmethod
    def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        pass

    def findall(self, string: str) -> Iterable[Match]:
        return list(self.pattern.finditer(string))


class Twitter(BaseInfoExtractor):
    def __init__(self):
        self.pattern = re.compile(r'https?://(?:mobile\.)?twitter\.com/[a-z0-9_]+/status/(?P<id>\d+)', re.IGNORECASE)
        self.hotlinking_allowed = True
        self.skip_first = True

    async def extract(self, url: Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        tweet_id = url.groupdict()['id']

        async with session.get('https://twitter.com/i/tweet/stickersHtml?id=' + tweet_id) as response:
            text = await response.read()
            data = json.loads(text)
            soup = BeautifulSoup(data['tweet_html'], "html.parser")
            urls = [i['data-image-url'] for i in soup.select('div.js-adaptive-photo')]
            return {'images': urls}


class ESixPool(BaseInfoExtractor):
    def __init__(self):
        self.pattern = re.compile(r'https?://e(?:621|926)\.net/pool/show/(?P<id>\d+)', re.IGNORECASE)
        self.hotlinking_allowed = True
        self.skip_first = False

    async def extract(self, url: Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        pool_id = url.groupdict()['id']

        request_url = 'https://e621.net/pool/show.json?id=' + pool_id
        async with session.get(request_url, headers={'User-Agent': 'sauce/0.1'}) as response:
            text = await response.read()
            data = json.loads(text)
            urls = [i['file_url'] for i in data['posts']]
            title = data.get('name')
            if title is not None:
                title = title.replace('_', ' ')
            else:
                title = None
            return {'title': title, 'description': data.get('description'), 'images': urls}


class Furaffinity(BaseInfoExtractor):
    def __init__(self):
        self.pattern = re.compile(r'https?://www.furaffinity.net/(?:view|full)/(?P<id>\d+)', re.IGNORECASE)
        self.hotlinking_allowed = True
        self.skip_first = False

    async def extract(self, url: Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        submission_id = url.groupdict()['id']

        # NOTE: this api doesn't provide submission descriptions
        request_url = 'https://bawk.space/fapi/submission/' + submission_id
        async with session.get(request_url) as response:
            text = await response.read()
            data = json.loads(text)
            if data['rating'] == 'general':
                return None
            return {'title': data['title'], 'images': [data['image_url']],
                    'name': data['author'], 'icon_url': data['image_url']}


class Sauce(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._extractors = [Twitter(), ESixPool(), Furaffinity()]
        self._session = aiohttp.ClientSession()

    def __remove_spoilered_text(self, message) -> str:
            '''quick hacky way to remove spoilers, doesn't handle ||s in code blocks'''
            strs = re.split('(\|\|)', message.content)
            despoilered = ''.join(strs[::4]) # Get every 4th string
            despoilered += strs[-1] if len(strs) % 4 == 3 else ''
            return despoilered

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        if message.author.bot:
            return

        despoilered_message = self.__remove_spoilered_text(message)

        links = []
        for extractor in self._extractors:
            matches = extractor.findall(message.content)
            if matches:
                links.extend([(match, extractor) for match in matches])
                break # Assumption: We won't match more than one site to a link, so it's safe to break as soon as we get a match.

        links.sort(key=lambda x: x[0].start())

        for match, extractor in links[:3]:  # only embed 3 images at most in a single post
            if extractor.hotlinking_allowed:
                image_limit = 4
                info = await extractor.extract(match, self._session)
                if info is None:
                    continue
                images = info['images']
                total_images = len(images)

                embed_info = {k: info[k] for k in info.keys() & ['title', 'description']}
                author_info = {k: info[k] for k in info.keys() & ['name', 'icon_url']}
                embed = None
                if embed_info:
                    embed = Embed(**embed_info)
                if author_info and embed is not None:
                    embed.set_author(**author_info)

                # TODO: handle embedding better, especially when the first post is already embedded by discord
                if extractor.skip_first:
                    if len(images) == 1:
                        continue
                    images = images[1:]
                    image_limit -= 1
                if embed is not None:
                    embed.set_image(url=images[0])
                    await message.channel.send(embed=embed)
                    images = images[1:]
                    image_limit -= 1
                if len(images[:image_limit]) > 0:
                    # TODO: give a better message in cases where we don't post everything
                    await message.channel.send(f'Set contains {total_images} images:\n' + '\n'.join(images[:3]))


def setup(bot):
    bot.add_cog(Sauce(bot))

from typing import Optional, Dict
import re
import asyncio
import json
from io import BytesIO

import aiohttp
from pixivpy_async import *

from . import BaseInfoExtractor
from utils import boxconfig


class Pixiv(BaseInfoExtractor):
    def __init__(self):
        self.illust_pattern = r'https?://www.pixiv.net/[a-z]+/artworks/(?P<id1>\d+)'
        self.direct_pattern = r'https://i.pximg.net/\S+/(?P<id2>\d+)_p(?P<page>\d+)(?:_\w+)?\.\w+'
        self.pattern = self.direct_pattern + '|' + self.illust_pattern
        self.hotlinking_allowed = False

        loop = asyncio.get_event_loop()
        self.pixivapi = AppPixivAPI()
        loop.run_until_complete(
            self.pixivapi.login(
                username=boxconfig.get("pixiv.email"), #self.config['pixiv']['login'],
                password=boxconfig.get("pixiv.password") #self.config['pixiv']['password'])
        ))

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        if re.match(self.illust_pattern, url):
            return await self.extract_illust(url)
        else:
            return await self.extract_direct(url)

    async def extract_illust(self, url: str) -> Optional[Dict]:
        illust_id = int(re.match(self.pattern, url).groupdict()['id1'])

        details = await self.pixivapi.illust_detail(illust_id)

        if 'illust' not in details:
            return

        page_count = details.illust.page_count

        if details.illust.x_restrict == 0:
            if page_count == 1:
                return
            images = [i.image_urls.medium for i in details.illust.meta_pages[1:]]
        else:
            if page_count == 1:
                images = [details.illust.image_urls.medium]
            else:
                images = [i.image_urls.medium for i in details.illust.meta_pages]

        return {'count': page_count, 'images': images}

    async def extract_direct(self, url: str) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        illust_id = groups['id2']
        page = groups['page']
        pixiv_url = 'https://www.pixiv.net/en/artworks/' + illust_id
        details = await self.pixivapi.illust_detail(illust_id)
        if details.illust.x_restrict == 0 and page == '0':
            return {'url': pixiv_url}
        else:

            return {'url': url, 'name': details.illust.user.name, 'title': details.illust.title,
                    'description': details.illust.caption,
                    'thumbnail': 'https://s.pximg.net/www/images/pixiv_logo.gif?2', 'images': [url],
                    'count': details.illust.page_count}

    @staticmethod
    async def download(url: str, session: aiohttp.ClientSession) -> BytesIO:
        async with session.get(url, headers={'Referer': 'https://app-api.pixiv.net/'}) as response:
            data = await response.read()
            data = BytesIO(data)
            data.name = url.rpartition('/')[2]
            return data

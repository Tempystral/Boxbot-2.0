from typing import Match, Optional, Dict
import os
import re
import asyncio
import json
from io import BytesIO

import aiohttp
from pixivpy3 import *

from . import BaseInfoExtractor


class Pixiv(BaseInfoExtractor):
    def __init__(self):
        self.pattern = re.compile(r'https?://www.pixiv.net/[a-z]+/artworks/(?P<id>\d+)', re.IGNORECASE)
        self.hotlinking_allowed = False
        self.skip_first = False

        with open('config.json') as configfile:
            self.config = json.load(configfile)

        self.pixivapi = AppPixivAPI()
        self.pixivapi.login(self.config['pixiv']['login'], self.config['pixiv']['password'])

    async def extract(self, url: Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        illust_id = url.groupdict()['id']
        print(illust_id)

        # pixivpy3 uses requests under the hood, so wrap it in a thread to make it async
        loop = asyncio.get_running_loop()
        details = await loop.run_in_executor(None, self.pixivapi.illust_detail, illust_id)

        if 'illust' not in details:
            return

        page_count = len(details.illust.meta_pages)

        return {'count': page_count,
                'images': [i.image_urls.medium for i in details.illust.meta_pages]}

    async def download(self, url: str, session: aiohttp.ClientSession) -> BytesIO:
        print(url)
        async with session.get(url, headers={'Referer': 'https://app-api.pixiv.net/'}) as response:
            data = await response.read()
            data = BytesIO(data)
            data.name = url.rpartition('/')[2]
            return data

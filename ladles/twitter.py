import json
import re
from typing import Match, Optional, Dict

import aiohttp
from bs4 import BeautifulSoup

from . import BaseInfoExtractor


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
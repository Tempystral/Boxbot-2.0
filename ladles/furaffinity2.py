from typing import Optional, Dict
import re

import aiohttp
from bs4 import BeautifulSoup

from utils import boxconfig
from . import BaseInfoExtractor


class Furaffinity2(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://www.furaffinity.net/(?:view|full)/(?P<id>\d+)'
        self.hotlinking_allowed = True
        self._cookie = boxconfig.get('furaffinity.cookie')

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        submission_id = re.match(self.pattern, url).groupdict()['id']

        url = f'http://www.furaffinity.net/view/{submission_id}'
        async with session.get(url, headers={'Cookie': self._cookie}) as response:
            text = await response.read()
            soup = BeautifulSoup(text)

            title, _, author = soup.find('meta', property='og:title')['content'].rpartition(" by ")
            icon_url = 'https:' + soup.select('.classic-submission-title img.avatar')[0]['src']

            description = soup.select('.maintable .maintable tr:nth-of-type(2) td')[0].get_text()
            description = '\n'.join([l for l in description.split('\n') if l])
            description = (description[:197] + '...') if len(description) > 200 else description

            rating = soup.find('meta', attrs={'name': 'twitter:data2'})['content']

            img = 'https:' + soup.select('#submissionImg')[0]['data-fullview-src']

            if rating == "General":
                return None
            return {'url': url, 'name': author, 'icon_url': icon_url, 'title': title,
                    'description': description, 'images': [img]}

import json
import re
from typing import Match, Optional, Dict

import aiohttp

from . import BaseInfoExtractor


class ESixPool(BaseInfoExtractor):
    def __init__(self):
        self.pattern = re.compile(r'https?://(?P<site>e621|e926)\.net/pool/show/(?P<id>\d+)', re.IGNORECASE)
        self.hotlinking_allowed = True
        self.skip_first = False

    async def extract(self, url: Match, session: aiohttp.ClientSession) -> Optional[Dict]:
        pool_id = url.groupdict()['id']

        request_url = 'https://e621.net/pool/show.json?id=' + pool_id
        async with session.get(request_url, headers={'User-Agent': 'sauce/0.1'}) as response:
            text = await response.read()
            data = json.loads(text)
            if url.groupdict()['site'] == 'e926':
                urls = [i['file_url'] for i in data['posts'] if i['rating'] == 's']
            else:
                urls = [i['file_url'] for i in data['posts']]
            title = data.get('name')
            if title is not None:
                title = title.replace('_', ' ')
            else:
                title = None
            return {'title': title, 'description': data.get('description'), 'images': urls, 'count': data['post_count']}
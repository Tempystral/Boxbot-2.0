import json
import re
from typing import Match, Optional, Dict

import aiohttp

from . import BaseInfoExtractor


class ESixPool(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/pool/show/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        pool_id = groups['id']
        pool_id = re.match(self.pattern, url).groupdict()['id']

        request_url = 'https://e621.net/pool/show.json?id=' + pool_id
        async with session.get(request_url, headers={'User-Agent': 'sauce/0.1'}) as response:
            text = await response.read()
            data = json.loads(text)
            if groups['site'] == 'e926':
                urls = [i['file_url'] for i in data['posts'] if i['rating'] == 's']
            else:
                urls = [i['file_url'] for i in data['posts']]
            title = data.get('name')
            if title is not None:
                title = title.replace('_', ' ')
            else:
                title = None
            return {'title': title, 'description': data.get('description'), 'images': urls, 'count': data['post_count']}

class ESixPost(BaseInfoExtractor):
    '''Extractor to source E621 and E926 direct image links'''
    def __init__(self):
        self.pattern = r'https?://static1\.(?P<site>e621|e926)\.net/data/(sample/)?../../(?P<md5>\w+)\..*'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        image_md5 = re.match(self.pattern, url).groupdict()['md5']
        request_url = 'https://e621.net/post/show.json?md5=' + image_md5
        async with session.get(request_url, headers={'User-Agent': 'sauce/0.1'}) as response:
            text = await response.read()
            data = json.loads(text)
            post_url = "https://e621.net/post/show/" + str(data.get("id"))
            return {'images': [post_url]}
            
            '''
            artists = [data["artist"][k] for k in data["artist"].keys()]
            return {'name': ", ".join([a.capitalize() for a in artists if a != "conditional_dnp"]),
                    'description': data.get('description'),
                    'images': urls,
                    'count': data['post_count']
                    }
            '''
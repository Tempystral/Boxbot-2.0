import json
import re
import asyncio
from typing import Optional, Dict

import aiohttp

from utils import boxconfig

from . import BaseInfoExtractor


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class ESixApi(metaclass=Singleton):
    def __init__(self):
        self._auth = aiohttp.BasicAuth(
            boxconfig.get("e621.username"),
            boxconfig.get("e621.apikey")
        )
        self._base_url = 'https://e621.net'
        self._request_count = 0
        self._sleep = asyncio.sleep(0)

    async def get(self, url: str, session: aiohttp.ClientSession) -> Dict:
        if self._request_count > 1:
            await self._sleep
            self._request_count = 0
            self._sleep = asyncio.sleep(1)

        req_url = self._base_url + url

        async with session.get(req_url, headers={'User-Agent': 'sauce/0.1'}, auth=self._auth) as response:
            self._request_count += 1
            text = await response.read()
            return json.loads(text)


class ESixPool(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'
        self.hotlinking_allowed = True
        self._api = ESixApi()

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        pool_id = groups['id']

        data = await self._api.get('/pools.json?search%5Bid%5D=' + pool_id, session)
        first_post = await self._api.get('/posts.json?tags=id%3A' + str(data[0]['post_ids'][0]), session)
        urls = [first_post['posts'][0]['file']['url']]
        description = data[0].get('description')
        title = data[0].get('name')
        title = title.replace('_', ' ') if title else None
        return {'url': url, 'title': title, 'description': description, 'images': urls, 'count': data[0]['post_count']}


class ESixPost(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/posts/(?P<id>\d+)'
        self.hotlinking_allowed = True
        self._api = ESixApi()

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        post_id = groups['id']

        data = await self._api.get('/posts.json?tags=id%3A' + post_id, session)
        post = data['posts'][0]
        tags = post['tags']['general']
        blacklisted = any([tag in tags for tag in ['loli', 'shota']])
        blacklisted = blacklisted or ('young' in tags and not post['rating'] == 's')
        if post['file']['ext'] in ['jpg', 'png', 'gif', 'webm'] and blacklisted:
            return {'images': [data['posts'][0]['file']['url']]}


class ESixDirectLink(BaseInfoExtractor):
    '''Extractor to source E621 and E926 direct image links'''
    def __init__(self):
        self.pattern = r'https?://static1\.(?P<site>e621|e926)\.net/data/(sample/)?../../(?P<md5>\w+)\..*'
        self.hotlinking_allowed = True
        self._api = ESixApi()

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        image_md5 = re.match(self.pattern, url).groupdict()['md5']
        data = await self._api.get('/posts.json?tags=md5%3A' + image_md5, session)
        post_url = "https://e621.net/posts/" + str(data['posts'][0]['id'])
        return {'images': [post_url]}
            
        '''
        artists = [data["artist"][k] for k in data["artist"].keys()]
        return {'name': ", ".join([a.capitalize() for a in artists if a != "conditional_dnp"]),
                'description': data.get('description'),
                'images': urls,
                'count': data['post_count']
                }
        '''
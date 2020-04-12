import json
import re
import asyncio
from typing import Optional, Dict

import aiohttp

from utils import boxconfig, commaList

from . import BaseInfoExtractor


class ESixApi:
    def __init__(self):
        self._auth = aiohttp.BasicAuth(
            boxconfig.get("e621.username"),
            boxconfig.get("e621.apikey")
        )
        self._base_url = 'https://e621.net'
        self._request_count = 0
        self._sleep = asyncio.sleep(0)

    async def get(self, url: str, session: aiohttp.ClientSession) -> Dict:
        await self._sleep

        req_url = self._base_url + url

        async with session.get(req_url, headers={'User-Agent': 'sauce/0.1'}, auth=self._auth) as response:
            text = await response.read()
            result = json.loads(text)

        self._sleep = asyncio.get_event_loop().create_task(asyncio.sleep(0.5))
        return result


_api = ESixApi()


class ESixPool(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/pools/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        pool_id = groups['id']

        data = await _api.get(f'/pools/{pool_id}.json', session)
        first_post = await _api.get(f'/posts/{data["post_ids"][0]}.json', session)
        urls = [first_post['post']['file']['url']]
        description = data.get('description')
        title = data.get('name')
        title = title.replace('_', ' ') if title else None
        return {'url': url, 'title': title, 'description': description, 'images': urls, 'count': data['post_count']}


class ESixPost(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e621|e926)\.net/posts/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        post_id = groups['id']

        data = await _api.get(f'/posts/{post_id}.json', session)
        post = data['post']
        tags = post['tags']['general']
        #print(data)
        
        # Determine if post is embed-blacklisted
        blacklisted = any([tag in tags for tag in ['loli', 'shota']])
        blacklisted = blacklisted or ('young' in tags and not post['rating'] == 's')
        if blacklisted:
            images = {'images': [post['file']['url']]}
            if post['file']['ext'] in ['webm']:
                return images
            if post['file']['ext'] in ['jpg', 'png', 'gif']:
                characters = post["tags"]["character"]
                artists = post["tags"]["artist"]
                title = f"{commaList(characters)} drawn by {commaList(artists)}"
                return {'url': url, 'title': title, 'description': post["description"], 'images': [post['file']['url']]}


class ESixDirectLink(BaseInfoExtractor):
    '''Extractor to source E621 and E926 direct image links'''
    def __init__(self):
        self.pattern = r'https?://static1\.(?P<site>e621|e926)\.net/data/(sample/)?../../(?P<md5>\w+)\..*'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        image_md5 = re.match(self.pattern, url).groupdict()['md5']
        data = await _api.get('/posts.json?tags=md5%3A' + image_md5, session)
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
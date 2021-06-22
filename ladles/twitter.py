import json, re, scalpl
from typing import Dict, Optional

import aiohttp
from bs4 import BeautifulSoup

from . import BaseInfoExtractor


class Twitter(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?:mobile\.)?twitter\.com/[a-z0-9_]+/status/(?P<id>\d+)'
        self.hotlinking_allowed = True
        self.auth = r'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
        

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        tweet_id = re.match(self.pattern, url).groupdict()['id']

        async with session.get(
            url = f'https://api.twitter.com/2/timeline/conversation/{tweet_id}.json?tweet_mode=extended',
            #params = params,
            headers = { 'authorization': self.auth }
        ) as response:
            text = await response.read()
            data = scalpl.Cut(json.loads(text))
            #print(data)
            variants = data.get(f"globalObjects.tweets.{tweet_id}.extended_entities.media[0].video_info.variants")
            #print(variants)
            videos = [x for x in variants if x.get("bitrate")]
            video = videos[0]
            for v in videos:
                if int(v.get("bitrate")) > int(video.get("bitrate")):
                    video = v
            return {"images": [video.get("url")]}
            

        # async with session.get('https://twitter.com/i/tweet/stickersHtml?id=' + tweet_id) as response:
        #     text = await response.read()
        #     data = json.loads(text)
        #     soup = BeautifulSoup(data['tweet_html'], "html.parser")
        #     urls = [i['data-image-url'] for i in soup.select('div.js-adaptive-photo')]
        #     return {'images': urls[1:]}
import json
import re
from typing import Match, Optional, Dict

import aiohttp

from . import BaseInfoExtractor


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
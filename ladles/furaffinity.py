import json
import re
from typing import Optional, Dict

import aiohttp

from . import BaseInfoExtractor


class Furaffinity(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://www.furaffinity.net/(?:view|full)/(?P<id>\d+)'
        self.hotlinking_allowed = True

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        submission_id = re.match(self.pattern, url).groupdict()['id']

        # NOTE: this api doesn't provide submission descriptions
        request_url = 'https://bawk.space/fapi/submission/' + submission_id
        async with session.get(request_url) as response:
            text = await response.read()
            data = json.loads(text)
            if data['rating'] == 'general':
                return None
            return {'images': [data['image_url']]}
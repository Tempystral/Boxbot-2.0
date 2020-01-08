import asyncio, aiohttp, json, os, re, scalpl
from typing import Dict, Optional
from utils import boxconfig, logger
from . import BaseInfoExtractor


class InkBunny(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://.*inkbunny\.net/s/(?P<id>\d+)'
        self.hotlinking_allowed = True
        self.__sid = None

    async def login(self, session: aiohttp.ClientSession):
      user_info = {
        "username" : boxconfig.get("inkbunny.username"),
        "password" : boxconfig.get("inkbunny.password")
      }
      async with session.get(url='https://inkbunny.net/api_login.php', params = user_info, headers = {'User-Agent': 'sauce/0.1'}) as response:
          text = await response.read()
          data = json.loads(text)
          try:
            sid = data["sid"]
            return sid
          except KeyError as e:
            logger.critical(f'Could not login to InkBunny:\nResponse from server: {data["error_message"]}')

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        groups = re.match(self.pattern, url).groupdict()
        params = {
          "sid" : self.__sid,
          "submission_id" : groups['id']
        }

        request_url = 'https://inkbunny.net/api_submissions.php'
        async with session.get(request_url, params=params, headers={'User-Agent': 'sauce/0.1'}) as response:
            text = await response.read()
            data = json.loads(text)
            if "error_code" in data:
              pass # Retry
            else:
              submission = scalpl.Cut(data["submissions"][0])
              # I like this for accessing nested json dicts, and the IB API is rather verbose
              author = submission.get("username")
              author_icon = submission.get("user_icon_url_small")
              images = [f.get("file_url_full") for f in submission.get("files")]
              num_images = submission.get("pagecount")
              title = submission.get("title")
              rating = submission.get("rating_id") # 0: General, 1: Mature, 2: Adult

              return {'url': url,
                      'name': author,
                      'icon_url': author_icon,
                      'title': title,
                      #'description': description, -- To be added (or not)
                      'images': images}
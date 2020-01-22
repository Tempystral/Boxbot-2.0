import asyncio, aiohttp, json, os, re, scalpl, html
from typing import Dict, Optional
from utils import boxconfig, logger
from . import BaseInfoExtractor


class EHentai(BaseInfoExtractor):
    def __init__(self):
        self.pattern = r'https?://(?P<site>e-|ex)hentai\.org/(?P<type>g|s)/(?P<group_1>\w+)/(?P<group_2>\w+)(-(?P<page_num>\d+))?'
        self.hotlinking_allowed = True
        self._request_url = 'https://api.e-hentai.org/api.php'
        self._restricted_tags = ["abortion", "bestiality", "incest", "lolicon", "shotacon", "toddlercon"]

    async def __get_gallery_token(self, page_token: str, gallery_id: int, page_num: int, session: aiohttp.ClientSession) -> str:
      params = {
        "method": "gtoken",
        "pagelist": [[gallery_id, page_token, page_num]]
      }
      async with session.post(self._request_url, json = params, headers = {'User-Agent': 'sauce/0.1'}) as response:
          text = await response.read()
          data = json.loads(text)
          #print(data)
          gdata = data["tokenlist"][0]
          if "error" in gdata:
            logger.critical(f'E-Hentai API error: {gdata["error"]}')
          else:
            return gdata[0]["token"]

    def __is_restricted(self, tags: list) -> bool:
      for tag in tags:
        match = re.match(r'(fe)?male:(?P<label>\w+)', tag)
        if not match:
          continue
        if match.groupdict().get("label") in self._restricted_tags:
          return True
      return False
    
    def __tags_to_string(self, tags: list) -> str:
      s = "Tags: "
      for tag in tags:
        trunc = tag.split(":")[-1]
        s += f"{trunc}, "
      return s[:-2] # Remove trailing space and comma

    async def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
      gallery_id = None
      gallery_token = None
      try:
        groups = re.match(self.pattern, url).groupdict()
      except AttributeError as e:
        logger.warning(f"Ladle triggered, but match was invalid. Input: {url}")
      if groups["type"] == "s":
        gallery_id = int(groups["group_2"])
        gallery_token = await self.__get_gallery_token(groups["group_1"], gallery_id, groups["page_num"], session)
      elif groups["type"] == "g":
        gallery_id = int(groups["group_1"])
        gallery_token = groups["group_2"]
      
      params = {
        "method" : "gdata",
        "gidlist" : [[gallery_id, gallery_token]],
        "namespace" : 1
      }
      async with session.post(self._request_url, json=params, headers={'User-Agent': 'sauce/0.1'}) as response:
          text = await response.read()
          data = json.loads(text)
          #print(data)
          if "error" in data:
            logger.critical(f'E-Hentai API error: {data["error"]} Url: {url}')
            return {}

          metadata = scalpl.Cut(data["gmetadata"][0]) # This will only work for single requests. This logic will need to change to accomodate multi-gallery requests

          if "error" in metadata:
            logger.critical(f'E-Hentai API error: {metadata["error"]} Url: {url}')
            return {}
          else:
            title = str(metadata.get("title")).replace("\n", " ") # Covers the edge case of a newline in the title data
            thumb = [metadata.get("thumb")]
            #count = int(metadata.get("filecount"))
            tags = metadata.get("tags")
            description = ""
            if groups["site"] == "ex":
              if self.__is_restricted(tags):
                gallery_url = f"https://exhentai.org/g/{gallery_id}/{gallery_token}/"
                description += "```fix\nThis gallery is only available on ExHentai. An e-hentai account is required to view this gallery.```\n"
              else:
                gallery_url = f"https://e-hentai.org/g/{gallery_id}/{gallery_token}/"
            
            description += self.__tags_to_string(tags)

            return {'url': gallery_url, # Redundant in many cases but it's not a lot of overhead for the cases where we sauce pages within a gallery
                    'title': html.unescape(title),
                    #'count': count,
                    'description': description,
                    'images': thumb}
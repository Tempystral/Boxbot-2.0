from typing import Optional, List, Dict
from datetime import datetime
from itertools import chain
import aiohttp
import asyncio
from html2text import html2text
from utils import logger


class NetworkError(Exception):
    pass


class Post:
    def __init__(self, data: Dict, board: str):
        self._data = data
        self.board = board

    @property
    def no(self) -> int:
        return self._data.get('no')

    @property
    def subject(self) -> str:
        return self._data.get('sub', '')

    @property
    def html_comment(self) -> str:
        return self._data.get('com', '')

    @property
    def comment(self) -> str:
        return html2text(self.html_comment).rstrip()

    @property
    def name(self) -> str:
        return self._data.get('name', '')

    @property
    def time(self) -> int:
        return self._data.get('time')

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.time)

    @property
    def slug(self) -> str:
        return self._data.get('semantic_url')

    @property
    def url(self):
        u = "https://boards.4chan.org/{board}/thread/{no}/{slug}".format(
            board=self.board,
            no=self.no,
            slug=self.slug)
        return u


class Chan:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = aiohttp.ClientSession() if session is None else session

    async def catalog(self, board: str) -> List[Post]:
        url = 'https://a.4cdn.org/{}/catalog.json'.format(board)
        while True:
            attempts = 0
            max_attempts = 5
            try:
                async with self._session.get(url, timeout=60, raise_for_status=True) as response:
                    data = await response.json()
            except aiohttp.ClientConnectionError:
                if attempts < max_attempts:
                    logger.warning(f"Connection error, retrying({attempts})")
                    await asyncio.sleep(5 * 1.5 ** attempts)
                else:
                    raise
            except aiohttp.ClientResponseError as e:
                if attempts < max_attempts:
                    logger.warning(f"Response error {e.response.status}, retrying({attempts})")
                    await asyncio.sleep(5 * 1.5 ** attempts)
                else:
                    raise
            break

        threads = chain(*(i['threads'] for i in data))
        return [Post(i, board) for i in threads]

    async def close(self) -> type(None):
        await self._session.close()

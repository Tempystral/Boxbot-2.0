from abc import ABC, abstractmethod
from typing import Optional, Dict, Iterable, Match

import aiohttp


class BaseInfoExtractor(ABC):
    pattern: str
    hotlinking_allowed: bool

    @abstractmethod
    def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        pass

    def findall(self, string: str) -> Iterable[Match]:
        return list(self.pattern.finditer(string))
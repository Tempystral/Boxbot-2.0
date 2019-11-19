from abc import ABC, abstractmethod
from typing import Pattern, Optional, Dict, Iterable, Match

import aiohttp


class BaseInfoExtractor(ABC):
    '''Abstract Base Class for ladles'''
    pattern: Pattern
    hotlinking_allowed: bool
    skip_first: bool

    @abstractmethod
    def extract(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        '''
        Returns
        ~~~~~~~
        images : list --
            A list of image urls

        title : str --
            A title, if any

        description : str --
            A description, if any
        
        name: str --
            Name of the post author, if any
        
        icon_url : str --
            The url of an icon, if any
        '''
        pass

    def findall(self, string: str) -> Iterable[Match]:
        return list(self.pattern.finditer(string))
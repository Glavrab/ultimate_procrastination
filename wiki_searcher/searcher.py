import aiohttp
import asyncio
import ujson
import typing
from wiki_searcher.utilities import get_object_info
from shared.constants import Wiki


class WikiSearcher:
    """Class for processing searching actions on wikipedia"""

    def __init__(self, action: str, format: str, prop: str, title: typing.Optional[str]):
        if title:
            self.title = title
        self.action = action
        self.format = format
        self.prop = prop

    async def get_object_wiki_info(self) -> str:
        """Get info about specific object"""
        search_settings = {
            'action': self.action,
            'format': self.format,
            'prop': self.prop,
            'titles': self.title,
            'exlimit': 1,
            'exintro': 1,   # Search options for correct text representation only of main description
            'explaintext': 1,   # Additional info https://www.mediawiki.org/wiki/Extension:TextExtracts#API
            'exsectionformat': 'wiki',
        }
        object_description = await WikiSearcher.process_searching(search_settings)
        return object_description

    async def get_random_wiki_title(self) -> str:
        """Get random wikipedia title"""
        search_settings = {
            'action': self.action,
            'format': self.format,
            'list': 'random',
            'rnnamespace': 0,  # Searching only for pages
            'rnlimit': 1,
        }
        title = await WikiSearcher.process_searching(search_settings)
        return title

    @classmethod
    async def process_searching(cls, search_settings: dict[str, int]) -> str:
        """Get object info from required page"""
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            response = await session.get(Wiki.API_URL.value, params=search_settings)
            await session.close()
            return get_object_info(await response.json())


if __name__ == '__main__':
    search = WikiSearcher('query', 'json', 'extracts', 'Pet_door')
    asyncio.run(search.get_random_wiki_title())

import asyncio
import typing
from database.models import (
    PhysicsTitle,
    BiologyTitle,
    HistoryTitle,
    ChemistryTitle,
    ItTitle,
)
from wiki_searcher.utilities import process_searching
from shared.constants import SearchedObjectCategories, SearchedObjectTypes


class WikiSearcher:
    """Class for processing searching actions on wikipedia"""

    def __init__(self, action: str, format: str, **kwargs: dict[str]):
        self.main_search_settings = {
            'action': action,
            'format': format,
        }
        if kwargs:
            try:
                self.main_search_settings.update(
                    prop=kwargs['prop'],
                    title=kwargs['title'],
                )
            except KeyError:
                print('Wrong arguments, requires keys: prop, title')

    async def get_object_wiki_info(self) -> str:
        """Get info about specific object"""
        search_settings = self.main_search_settings
        search_settings.update(
            prop='extracts',
            exlimit=1,
            exintro=1,  # Search options for correct text representation only of main description
            explaintext=1,  # Additional info https://www.mediawiki.org/wiki/Extension:TextExtracts#API
            exectionformat='wiki',
        )

        object_description = await process_searching(search_settings, SearchedObjectTypes.PAGE.value)
        return object_description

    async def get_random_wiki_title(self) -> str:
        """Get random wikipedia title"""
        search_settings = self.main_search_settings
        search_settings.update(
            list='random',
            rnnamespace=0,  # Searching only for pages
            rnlimit=1,
        )
        title = await process_searching(search_settings, SearchedObjectTypes.TITLE.value)
        return title

    async def get_subcategories_titles(
            self,
            searched_object: str,
            title_db_model: typing.Union['PhysicsTitle', 'ChemistryTitle', 'ItTitle', 'BiologyTitle', 'HistoryTitle'],
            max_amount_of_objects_for_level: int,
    ) -> list[str]:
        """Get subcategories titles for required object and write them into db"""
        search_settings = self.main_search_settings
        search_settings.update(
            list=SearchedObjectTypes.CATEGORY_MEMBERS.value,
            cmtitle=searched_object,
            cmtype=SearchedObjectTypes.PAGE.value + '|' + SearchedObjectTypes.SUBCATEGORY.value,
            cmlimit=max_amount_of_objects_for_level,
        )
        titles, categories = await process_searching(
            search_settings,
            SearchedObjectTypes.CATEGORY_MEMBERS.value
        )
        for title in titles:  # await title_db_model.create(title_name=title)
            pass             # TODO: write down founded titles into db

        return categories


if __name__ == '__main__':
    search = WikiSearcher(action='query', format='json')
   # await search.get_subcategories_titles(SearchedObjectCategories.IT.value, 3, PhysicsTitle, 100)
    asyncio.run(search.get_random_wiki_title())

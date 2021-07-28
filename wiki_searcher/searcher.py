from database.models import Title
from wiki_searcher.utilities import process_searching
from shared.constants import SearchedObjectTypes


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

    async def get_object_wiki_info(self, title: str) -> str:
        """Get info about specific object"""
        search_settings = self.main_search_settings
        search_settings.update(
            titles=title,
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
            object_type_id: int,
            amount_of_searched_objects: int,
    ) -> list[str]:
        """Get subcategories titles for required object and write them into db"""
        search_settings = self.main_search_settings
        search_settings.update(
            list=SearchedObjectTypes.CATEGORY_MEMBERS.value,
            cmtitle=searched_object,
            cmtype=SearchedObjectTypes.PAGE.value + '|' + SearchedObjectTypes.SUBCATEGORY.value,
            cmlimit=amount_of_searched_objects,
        )
        titles, categories = await process_searching(
            search_settings,
            SearchedObjectTypes.CATEGORY_MEMBERS.value,
        )
        for title in titles:
            await Title.create(title_name=title, title_type_id=object_type_id)
        return categories

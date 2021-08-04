import asyncio
import typing

from database.models import Title, Category, connect_to_db
from wiki_searcher.utilities import process_searching
from shared.project_settings import settings
from shared.utilities import get_all_enum_values
from shared.constants import SearchedObjectTypes, SearchedObjectCategories


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
        search_settings = self.main_search_settings.copy()
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
        search_settings = self.main_search_settings.copy()
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
    ) -> typing.Optional[list[str]]:
        """Get subcategories titles for required object and write them into db"""
        search_settings = self.main_search_settings.copy()
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
        if not titles and not categories:
            return None
        tasks = []
        for title in titles:
            tasks.append(Title.create(title_name=title, title_type_id=object_type_id))
        await asyncio.gather(*tasks)
        return categories


async def process_titles_filling(
        searched_categories: list[str],
        amount_of_objects_for_level: int = 5000,
) -> tuple:
    await connect_to_db(settings.create_db_uri())
    searcher = WikiSearcher(action='query', format='json')
    tasks = []
    for category in searched_categories:
        just_category_name = category[9:]  # In SearchedObjectCategories wrote down as 'Category:name' so we get name
        existing_category = await Category.get_category_by_name(just_category_name)
        if not existing_category:
            existing_category = await Category.create(category_name=just_category_name)
        tasks.append(
            searcher.get_subcategories_titles(
                searched_object=category,
                object_type_id=existing_category.id,
                amount_of_searched_objects=amount_of_objects_for_level,
            )
        )
    result = await asyncio.gather(*tasks)
    return result

if __name__ == '__main__':
    categories = get_all_enum_values(SearchedObjectCategories)
    asyncio.run(process_titles_filling(categories))
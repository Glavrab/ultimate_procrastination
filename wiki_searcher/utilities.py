import ujson
import typing
import aiohttp
from shared.constants import Wiki, SearchedObjectTypes


async def process_searching(search_settings: dict[typing.Union[str, int]],
                            task: str) -> typing.Union[str, tuple[list[str], list[str]]]:
    """Get object info from required page"""
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        response = await session.get(Wiki.API_URL.value, params=search_settings)
        await session.close()
    if task != SearchedObjectTypes.CATEGORY_MEMBERS.value:
        return get_object_info_for_one_page(await response.json())
    return get_titles_and_categories(await response.json())


def get_object_info_for_one_page(data: dict[str]) -> str:
    """Parse json file to get reqired page's title or info"""
    result = data['query'].setdefault('pages')
    if result:
        pages_info = list(data['query']['pages'].values())
        object_description = pages_info[0]['extract']  # only 1 value represents because we look for 1 title
        return object_description
    object_info = data['query']['random'][0]  # same because we get 1 random page
    title = object_info['title']
    return title


def get_titles_and_categories(data: dict[str]) -> tuple[list[str], list[str]]:
    """Parse json file for categories or pages titles to insert into db """
    titles = []
    categories = []
    search_results = data['query']['categorymembers']
    for result in search_results:
        if result['ns'] == 0:  # Means that result is page other is category
            titles.append(result['title'])
        categories.append(result['title'])
    return titles, categories

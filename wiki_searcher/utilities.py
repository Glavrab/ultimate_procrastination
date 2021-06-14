
def get_object_info(data: dict[str]) -> str:
    """Parse json file to get required info"""
    try:
        pages_info = list(data['query']['pages'].values())
        object_description = pages_info[0]['extract']
        return object_description
    except KeyError:
        object_info = data['query']['random'][0]
        title = object_info['title']
        return title

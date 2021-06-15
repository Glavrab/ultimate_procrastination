import enum


class Wiki(enum.Enum):
    """Wiki api url"""
    API_URL = 'https://en.wikipedia.org/w/api.php'


class Codes(enum.Enum):
    """Codes for underestimation of required search"""
    SEARCH_RANDOM_PAGE_TITLE = 100
    SEARCH_REQUIRED_PAGE = 200


class SearchedObjectCategories(enum.Enum):
    """Objects category to search in wiki"""
    PHYSICS = 'Category:Physics'
    CHEMISTRY = 'Category:Chemistry'
    HISTORY = 'Category:History'
    BIOLOGY = 'Category:Biology'
    IT = 'Category:Information and communications technology'


class SearchedObjectTypes(enum.Enum):
    """Existing object types to search in wiki"""
    TITLE = 'title'
    PAGE = 'page'
    SUBCATEGORY = 'subcat'
    FILE = 'file'
    CATEGORY_MEMBERS = 'categorymembers'

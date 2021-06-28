import enum


class Wiki(enum.Enum):
    """Wiki api url"""
    API_URL = 'https://en.wikipedia.org/w/api.php'


class Codes(enum.Enum):
    """Codes for understimation of required search"""
    SEARCH_RANDOM_PAGE_TITLE = 100
    SEARCH_REQUIRED_PAGE = 200

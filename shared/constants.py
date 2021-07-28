import enum


class PasswordErrorMessage(enum.Enum):
    """Password errors messages"""
    UNMATCHED_PASSWORD = 'Typed passwords do not match up'
    INELIGIBLE_PASSWORD = 'Password must have at least one' \
                          ' uppercase letter and one number' \
                          ' password length should be 8-16 '


class LoginErrorMessage(enum.Enum):
    """Login error messages"""
    INELIGIBLE_LOGIN = 'Login should consist of latin letters and numbers'
    INCORRECT_DATA = 'Incorrect login or password'
    USER_ALREADY_EXIST = 'This login already exist'


class Wiki(enum.Enum):
    """Wiki api url"""
    API_URL = 'https://en.wikipedia.org/w/api.php'


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


ALPHABET = {
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z'
}

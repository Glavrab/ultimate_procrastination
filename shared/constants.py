import enum


class CurrentTask(enum.Enum):
    """Current task processing by user"""
    LOGIN_PAGE = 'Login page'
    REGISTRATION = 'Registration'
    LOGIN = 'Login'
    GETTING_INFO = 'Getting info'


class URL(enum.Enum):
    """Urls for accessing API"""
    REGISTER = 'procrastination_web:8000/registration'
    LOGIN = 'procrastination_web:8000/login'
    RANDOM_FACT = 'procrastination_web:8000/random_fact'
    RANDOM_RATED_FACT = 'procrastination_web:8000/random_rated_fact'
    RATE_FACT = 'procrastination_web:8000/rate_fact'


class InfoTypeId(enum.Enum):
    """Info category id"""
    PHYSICS = 0
    CHEMISTRY = 1
    BIOLOGY = 2
    HISTORY = 3
    IT = 4


class RateCommand(enum.Enum):
    """Rating commands"""
    LIKE = 'Like'
    DISLIKE = 'Dislike'
    NEXT = 'Next'
    MORE_INFO = 'More info'


class Codes(enum.Enum):
    """Response result codes"""
    SUCCESS = 500


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
    """Category objects to search in wiki"""
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

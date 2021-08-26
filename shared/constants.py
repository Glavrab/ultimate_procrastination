import enum
import re


PASSWORD_SYMBOLS_REQUIREMENTS_PATTERN = re.compile('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,16}$')
PASSWORD_COMPOUNDS_REQUIREMENTS_PATTERN = re.compile('^[a-zA-Z0-9$@]')
LOGIN_COMPOUNDS_REQUIREMENTS_PATTERN = re.compile('^[a-zA-Z0-9$@].{4,20}$')
EMAIL_COMPOUNDS_REQUIREMENTS_PATTERN = re.compile(
    '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]'
    '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
)


class EmailMessage(enum.Enum):
    """Message for user in email message to activate account"""
    CONFIRMATION = 'Here is your link go to it to activate your account! '


class RequiredData(enum.Enum):
    """Required data to process request"""
    USERNAME = 'username'
    PASSWORD = 'password'
    REPEATED_PASSWORD = 'repeated_password'
    EMAIL = 'email'
    TELEGRAM_ID = 'telegram_id'
    COMMAND = 'command'


class CurrentTask(enum.Enum):
    """Current task processing by user"""
    LOGIN_PAGE = 'Login page'
    REGISTRATION = 'Registration'
    LOGIN = 'Login'
    GETTING_INFO = 'Getting info'


class URL(enum.Enum):
    """Urls for accessing API"""
    REGISTER = 'http://procrastination_web:8000/registration'
    LOGIN = 'http://procrastination_web:8000/login'
    RANDOM_FACT = 'http://procrastination_web:8000/random_fact'
    RANDOM_RATED_FACT = 'http://procrastination_web:8000/random_rated_fact'
    RATE_FACT = 'http://procrastination_web:8000/rate_fact'
    EMAIL_CONFIRMATION = 'http://0.0.0.0:8000/email_confirmation/'


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
    AUTHORIZED = 200


class EmailErrorMessage(enum.Enum):
    """Email error messages"""
    INCORRECT_EMAIL = 'Your email is incorrect'


class PasswordErrorMessage(enum.Enum):
    """Password errors messages"""
    UNMATCHED_PASSWORD = 'Typed passwords do not match up'
    INELIGIBLE_PASSWORD = 'Password must have at least one' \
                          ' uppercase letter and one number' \
                          ' password length should be 8-16 '


class LoginErrorMessage(enum.Enum):
    """Login error messages"""
    INELIGIBLE_LOGIN = 'Login should consist of latin letters and numbers'
    INCORRECT_DATA = 'Incorrect login or password or email not confirmed yet'
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
    GEOGRAPHY = 'Category:Geography'
    ECONOMICS = 'Category:Economics'
    PHILOSOPHY = 'Category:Philosophy'
    MATH = 'Category:Mathematics'
    SOCIOLOGY = 'Category:Sociology'
    JURISPRUDENCE = 'Category:Jurisprudence'


class SearchedObjectTypes(enum.Enum):
    """Existing object types to search in wiki"""
    TITLE = 'title'
    PAGE = 'page'
    SUBCATEGORY = 'subcat'
    FILE = 'file'
    CATEGORY_MEMBERS = 'categorymembers'

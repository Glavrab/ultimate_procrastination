import random
import re
import typing
from functools import wraps

import bcrypt
import ujson
from aiohttp import web
from aiohttp_session import (
    new_session,
    Session,
    get_session,
)
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_redis_pool

from database.models import User, Title, Rating, db, CategoryRating
from shared.constants import (
    PasswordErrorMessage,
    LoginErrorMessage,
    Codes,
    RateCommand,
    RequiredData,
    PASSWORD_COMPOUNDS_REQUIREMENTS_PATTERN,
    LOGIN_COMPOUNDS_REQUIREMENTS_PATTERN,
    PASSWORD_SYMBOLS_REQUIREMENTS_PATTERN,
    SearchType,
)
from shared.exceptions import PasswordError, LoginError
from shared.project_settings import settings
from shared.utilities import get_all_enum_values
from wiki_searcher.searcher import WikiSearcher


async def create_redis_storage():
    """Create redis storage for app"""
    redis = await create_redis_pool(f'redis://procrastination_redis', password=settings.redis_password)
    storage = RedisStorage(
        redis,
        cookie_name='PROCRASTINATION_SESSION',
        encoder=ujson.dumps,
        decoder=ujson.loads,
    )
    return storage


async def register_user(data: dict[str]) -> dict[str]:
    """Register user"""
    await _check_if_data_correct(data)
    hashed_password = _hash_password(data['password'])
    if RequiredData.TELEGRAM_ID.value in data.keys():
        await User.create(
            username=data['username'],
            password=hashed_password,
            telegram_id=data['telegram_id'],
            email=data['email']
        )
    else:
        await User.create(
            username=data['username'],
            password=hashed_password,
            email=data['email']
        )
    return {'result': Codes.SUCCESS.value}


async def login_user(data: dict[str], request: web.Request) -> typing.Optional[dict[str]]:
    """Login user"""
    username = data['username']
    user = await User.get_user_by_username(username)
    if user:
        if bcrypt.checkpw(data['password'].encode('utf-8'), bytes(user.password, encoding='utf8')):
            session: 'Session' = await new_session(request)
            session['username'], session['user_id'] = username, user.id
            return {'result': Codes.SUCCESS.value}
    raise LoginError(LoginErrorMessage.INCORRECT_DATA.value)


async def get_random_fact_info() -> str:
    """Get random wiki page info"""
    searcher = WikiSearcher(action='query', format='json')
    random_title = await searcher.get_random_wiki_title()
    object_description = await searcher.get_object_wiki_info(random_title)
    return object_description


async def get_random_rated_fact_info(session: 'Session', search_type: str) -> tuple[str, str]:
    """Get random rated fact"""
    if search_type not in get_all_enum_values(SearchType):
        raise web.HTTPBadRequest(text='Incorrect request path')
    rated_categories = []
    if search_type == SearchType.TOP_FACTS.value:
        rated_categories = [category for category in await User.get_users_top_categories_id(5, session['user_id'])]
    if search_type == SearchType.NEW_FACTS.value:
        rated_categories = [category for category in await User.get_new_users_categories_id(5, session['user_id'])]
    random_category_id = _process_random_category_choosing(categories=rated_categories)
    rated_title = await Title.get_random_title_by_category(random_category_id)
    session['last_rated_topic_id'] = rated_title.id
    searcher = WikiSearcher(action='query', format='json')
    object_description = await searcher.get_object_wiki_info(rated_title.title_name)
    return object_description, rated_title.title_name


async def process_rating(data: dict, session: 'Session') -> tuple[str, str, dict[str]]:
    """Process rating command"""
    command = data['command']
    title_id = session['last_rated_topic_id']
    rated_title = await Title.get(title_id)
    amount_of_likes, amount_of_views, title_type = rated_title.amount_of_likes, \
                                                   rated_title.amount_of_views, \
                                                   rated_title.title_type_id,
    total_amount_of_views = amount_of_views + 1
    theme_rating = await Rating.get_user_theme_rating(title_type, session['username'])
    if not theme_rating:
        theme_rating = await Rating.create(category_type_id=title_type, user_id=session['user_id'])

    if command == RateCommand.LIKE.value:
        total_amount_of_likes = amount_of_likes + 1
        title_rating = total_amount_of_likes / total_amount_of_views
        async with db.transaction() as transaction:
            await theme_rating.update(rating_number=theme_rating.rating_number + 1).apply()
            await rated_title.update(
                amount_of_likes=amount_of_likes + 1,
                amount_of_views=total_amount_of_views,
                title_rating=title_rating,
            ).apply()
    elif command == RateCommand.DISLIKE.value:
        total_amount_of_likes = amount_of_likes - 1
        title_rating = total_amount_of_likes / total_amount_of_views
        async with db.transaction() as transaction:
            await theme_rating.update(rating_number=theme_rating.rating_number - 1).apply()
            await rated_title.update(
                amount_of_likes=amount_of_likes - 1,
                amount_of_views=total_amount_of_views,
                title_rating=title_rating
            ).apply()

    result = {"result": Codes.SUCCESS.value}
    return session['username'], command, result


async def _check_if_data_correct(data: dict[str]):
    """Check if data is ok with the requirements"""
    password = data['password']
    user_exist = await User.check_if_user_already_exist(data['username'], data['email'])
    if user_exist:
        raise LoginError(LoginErrorMessage.USER_ALREADY_EXIST.value)
    if password != data['repeated_password']:
        raise PasswordError(PasswordErrorMessage.UNMATCHED_PASSWORD.value)
    elif (
            not PASSWORD_SYMBOLS_REQUIREMENTS_PATTERN.search(password)
            or not PASSWORD_COMPOUNDS_REQUIREMENTS_PATTERN.match(password)
    ):
        raise PasswordError(PasswordErrorMessage.INELIGIBLE_PASSWORD.value)
    elif not LOGIN_COMPOUNDS_REQUIREMENTS_PATTERN.match(data['username']):
        raise LoginError(LoginErrorMessage.INELIGIBLE_LOGIN.value)


def login_required(handler: typing.Callable[[web.Request], typing.Awaitable[web.Response]]):
    """Check for authorization to process request"""

    @wraps(handler)
    async def wrapper(request: web.Request) -> web.Response:
        session = await get_session(request)
        if session.new:
            session.invalidate()
            raise web.HTTPUnauthorized(text='Requires authorization')
        return await handler(request)

    return wrapper


def json_required(handler: typing.Callable[[web.Request], typing.Awaitable[web.Response]]):
    """Check for correct request content to process request"""

    @wraps(handler)
    async def wrapper(request: web.Request) -> web.Response:
        if 'Content-type' not in request.headers or request.headers['Content-type'] != 'application/json':
            raise web.HTTPBadRequest(text='Incorrect request content')
        try:
            await request.json(loads=ujson.loads)
        except ValueError:
            raise web.HTTPBadRequest(text='Incorrect request content')
        return await handler(request)

    return wrapper


def create_json_response(data: dict[typing.Union[str, int]]) -> web.Response:
    """Json response using ujson.dumps"""
    return web.json_response(data, dumps=ujson.dumps)


def _process_random_category_choosing(categories: list['CategoryRating']) -> int:
    """Get random category id based on avg category rating"""
    amount_of_categories = len(categories)
    summary_rating = 0
    result = []
    for category in categories:
        summary_rating += category.rating_number
    try:
        avg_rating = amount_of_categories / summary_rating
    except ZeroDivisionError:
        avg_rating = 0
    for category in categories:
        if category.rating_number >= avg_rating:
            result.append(category.category_id)
            result.append(category.category_id)
        result.append(category.category_id)
    return result[random.randint(0, len(result))]


def _hash_password(password: str) -> str:
    """Hash password with salt"""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def check_for_required_info_for_login(data: dict[str]):
    if RequiredData.USERNAME.value not in data.keys() or RequiredData.PASSWORD.value not in data.keys():
        raise web.HTTPBadRequest(text='Incorrect data')


def check_for_required_info_for_registration(data: dict[str]):
    if (
            RequiredData.EMAIL.value not in data.keys()
            or RequiredData.USERNAME.value not in data.keys()
            or RequiredData.PASSWORD.value not in data.keys()
            or RequiredData.REPEATED_PASSWORD.value not in data.keys()
    ):
        raise web.HTTPBadRequest(text='Incorrect data')


def check_for_required_info_to_rate_title(data: dict[str]):
    available_commands = get_all_enum_values(RateCommand)
    if RequiredData.COMMAND.value not in data.keys() or data['command'] not in available_commands:
        raise web.HTTPBadRequest(text='Incorrect data')

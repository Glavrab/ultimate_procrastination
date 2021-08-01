import random
import re
import typing

import bcrypt
import ujson
from aiohttp import web
from aiohttp_session import (
    new_session,
    Session,
    get_session,
)
from aiohttp_session.redis_storage import RedisStorage

from database.models import User, Title, Rating
from shared.constants import (
    PasswordErrorMessage,
    LoginErrorMessage,
    Codes,
    RateCommand,
)
from shared.utilities import get_all_enum_values
from shared.exceptions import PasswordError, LoginError
from aioredis import create_redis_pool
from wiki_searcher.searcher import WikiSearcher


async def create_redis_storage():
    """Create redis storage for app"""
    redis = await create_redis_pool(f'redis://procrastination_redis')
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
    if data.setdefault('telegram_id'):
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


async def get_random_fact() -> str:
    """Get random wiki page info"""
    searcher = WikiSearcher(action='query', format='json')
    random_title = await searcher.get_random_wiki_title()
    object_description = await searcher.get_object_wiki_info(random_title)
    return object_description


async def get_random_rated_fact_info(session: 'Session') -> tuple[str, str]:
    """Get random rated fact"""
    topic_type_number = random.randint(0, 4)
    rated_title = await Title.get_random_title_by_category(topic_type_number)
    session['last_rated_topic_id'] = rated_title.id
    searcher = WikiSearcher(action='query', format='json')
    object_description = await searcher.get_object_wiki_info(rated_title.title_name)
    return object_description, rated_title.title_name


async def check_if_user_logged_in(request: web.Request) -> bool:
    """Check if user has logged in"""
    session = await get_session(request)
    if session.new:
        session.invalidate()
        return False
    return True


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
    theme_rating_number = theme_rating.rating_number

    if command == RateCommand.LIKE.value:
        title_rating = (amount_of_likes + 1) / total_amount_of_views
        await theme_rating.update(rating_number=theme_rating_number + 1).apply()
        await rated_title.update(
            amount_of_likes=amount_of_likes + 1,
            amount_of_views=total_amount_of_views,
            title_rating=title_rating,
        ).apply()

    elif command == RateCommand.DISLIKE.value:
        total_amount_of_likes = amount_of_likes - 1
        title_rating = total_amount_of_likes / total_amount_of_views
        await theme_rating.update(rating_number=theme_rating_number - 1).apply()
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
    user = await User.get_user_by_username(data['username'])
    if user:
        raise LoginError(LoginErrorMessage.USER_ALREADY_EXIST.value)
    if password != data['repeated_password']:
        raise PasswordError(PasswordErrorMessage.UNMATCHED_PASSWORD.value)
    elif not re.search('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,16}$', password) or not re.match('^[a-zA-Z0-9$@].{4,'
                                                                                                  '20}$', password):
        raise PasswordError(PasswordErrorMessage.INELIGIBLE_PASSWORD.value)
    elif not re.match('^[a-zA-Z0-9$@].{4,20}$', data['username']):
        raise LoginError(LoginErrorMessage.INELIGIBLE_LOGIN.value)


def _hash_password(password: str) -> str:
    """Hash password with salt"""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def check_for_required_info_for_login(data: dict[str]):
    if not data.setdefault('username') or not data.setdefault('password'):
        raise web.HTTPBadRequest(text='Incorrect data')


def check_for_required_info_for_registration(data: dict[str]):
    if not data.setdefault('username') or not data.setdefault('password') or not data.setdefault('email'):
        raise web.HTTPBadRequest(text='Incorrect data')
    if not data.setdefault('email'):
        raise web.HTTPBadRequest(text='Incorrect data')


def check_for_required_info_to_rate_title(data: dict[str]):
    available_commands = get_all_enum_values(RateCommand)
    if not data.setdefault('command') or data['command'] not in available_commands:
        raise web.HTTPBadRequest(text='Incorrect data')

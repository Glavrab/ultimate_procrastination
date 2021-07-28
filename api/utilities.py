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



def check_if_data_correct(data: dict[str]) -> typing.Union[bool, str]:
    """Check if data is ok with the requirements"""
    password = data['passwords']['password']
    if password != data['passwords']['repeated_password']:
        raise PasswordError(PasswordErrorMessage.UNMATCHED_PASSWORD.value)
    elif re.search('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,16}$', password):
        raise PasswordError(PasswordErrorMessage.INELIGIBLE_PASSWORD.value)
    elif re.match('^[a-zA-Z0-9$@].{4,20}$', data['username']):
        raise LoginError(LoginErrorMessage.INELIGIBLE_LOGIN.value)
    return True


def _hash_password(password: str) -> str:
    """Hash password with salt"""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

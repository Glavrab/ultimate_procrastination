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

async def register_user(data: dict[str]):
    """Register user"""
    check_if_data_correct(data)
    hashed_password = hash_password(data['passwords']['password'])
    if check_for_telegram_user(data):
        await User.create(
                username=data['username'],
                password=hashed_password,
                telegram_id=data['telegram_id'],
            )
    await User.create(
        username=data['username'],
        password=hashed_password,
    )


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


def hash_password(passwords: dict[str]) -> str:
    """Hash password with salt"""
    password = passwords['password']
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=8))
    return str(hashed_password)


def check_for_telegram_user(data: dict[str]) -> bool:
    """Look for telegram_id in data"""
    user_info = list(data.keys())
    for info in user_info:
        if info == 'telegram_id':
            return True
    return False

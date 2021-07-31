import typing
from enum import EnumMeta
from shared.constants import URL, CurrentTask
from loguru import logger
from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from typing import Optional, Any
from bot.constants import AuthorizationForm
import ujson
from aiohttp import ClientSession
import json
import itertools


async def process_showing_random_fact(bot: Bot,
                                      state: FSMContext,
                                      message: types.CallbackQuery,
                                      commands: list[str],
                                      ):
    """Process showing random fact for user"""
    random_fact, random_fact_title = await get_random_rated_fact(state)
    await bot.send_message(
            message.from_user.id,
            f'{random_fact_title}\n\n{random_fact}',
            reply_markup=create_inline_keyboard(
                commands,
            ),
        )


async def rate_fact(state: FSMContext, rate_command: str):
    """Process http request to rate random fact"""
    async with state.proxy() as data:
        session_key = data['session_key']
    session = ClientSession(cookies={'PROCRASTINATION_SESSION': session_key}, json_serialize=ujson.dumps)
    await session.post(URL.RATE_FACT.value, json={'command': rate_command})
    await session.close()


async def get_random_rated_fact(state: FSMContext) -> tuple[str, str]:
    """Process Http request to get random rated fact"""
    async with state.proxy() as data:
        session_key = data['session_key']
    session = ClientSession(cookies={'PROCRASTINATION_SESSION': session_key}, json_serialize=ujson.dumps)
    async with session.get(URL.RANDOM_RATED_FACT.value) as response:
        result = await response.json(loads=ujson.loads)
        await session.close()
    return result['random_rated_fact'], result['title_name']


async def process_authorization_error_scenario(message: types.Message, response: dict[str], process_type: str):
    """Process authorization errors"""
    logger.debug(f'Unsuccessful authorization by user: {message.from_user.id} error:{response["error"]}')
    await message.answer(
        response['error'] + ' ' + f' Get back to the login page or start {process_type}'
                                  f' process again by typing your username again',
        reply_markup=create_inline_keyboard([CurrentTask.LOGIN_PAGE.value]),
    )
    await AuthorizationForm.username.set()


async def show_login_menu(bot: Bot, chat_id: int):
    await bot.send_message(
        chat_id,
        'Welcome to yours procrastination supporter, have you already registered?',
        reply_markup=create_inline_keyboard
        (
            [
                'Yes',
                'No',
            ]
        )
    )


async def register_user(user_info: dict[str]) -> dict[str]:
    """Process Http request to api to register user"""
    session = ClientSession(json_serialize=ujson.dumps)
    async with session.post(URL.REGISTER.value, json=user_info) as response:
        result = await response.json(loads=ujson.loads)
        await session.close()
    return result


async def login_user(user_info: dict[str], state: FSMContext) -> tuple[dict[str], str]:
    """Process Http request to login user"""
    session = ClientSession(json_serialize=ujson.dumps)
    async with session.post(URL.LOGIN.value, json=user_info) as response:
        result = await response.json(loads=ujson.loads)
        await session.close()
    if response.cookies.setdefault('PROCRASTINATION_SESSION'):
        async with state.proxy() as data:
            data['session_key'] = response.cookies['PROCRASTINATION_SESSION']
    return result, response.cookies.setdefault('PROCRASTINATION_SESSION')


def create_inline_keyboard(buttons: list[str],
                           callback_queries: Optional[tuple] = None,
                           ) -> types.InlineKeyboardMarkup:
    """Create an inline keyboard to communicate with bot."""
    if callback_queries is None:
        callback_queries = buttons.copy()

    keyboard = types.InlineKeyboardMarkup()
    for button, query in itertools.zip_longest(buttons, callback_queries):
        button_to_add = types.InlineKeyboardButton(button, callback_data=_callback_data_normalize(query))
        keyboard.add(button_to_add)
    return keyboard


def _callback_data_normalize(data: Any) -> Optional[str]:
    """Process data to appear as str in callbacks"""
    if isinstance(data, str):
        return data
    if isinstance(data, (int, float)):
        return str(data)
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)

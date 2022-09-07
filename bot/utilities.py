import itertools
import json
from typing import Optional, Any, Union

import ujson
from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiohttp import ClientSession
from shared.utilities import get_all_enum_values
from bot.constants import AuthorizationForm, MainForm
from shared.constants import URL, CurrentTask, SearchType, RateCommand, ContentType


async def process_showing_random_fact(bot: Bot,
                                      state: FSMContext,
                                      message: types.CallbackQuery,
                                      ):
    """Process showing random fact for user"""
    async with state.proxy() as data:

        if message.data == RateCommand.NEXT:
            search_type = data['current_task']
        else:
            search_type = message.data

    random_fact, random_fact_title = await get_random_rated_fact(state, search_type)
    async with state.proxy() as data:
        data['last_rated_topic_name'] = random_fact_title
    await process_showing_main_menu(bot, message, f'{random_fact_title}\n\n{random_fact}')


async def process_showing_main_menu(bot: Bot, message: types.CallbackQuery, text: str):
    """Process showing main keyboard to interact with bot with required text"""
    commands = get_all_enum_values(RateCommand)
    await bot.send_message(
        message.from_user.id,
        text,
        reply_markup=create_inline_keyboard(
            commands + [CurrentTask.GET_NEW_FACT.value, CurrentTask.GET_TOP_FACT.value, CurrentTask.LOGIN_PAGE.value],
        ),
    )


async def rate_fact(state: FSMContext, rate_command: str):
    """Process http request to rate random fact"""
    async with state.proxy() as data:
        session_key = data['session_key']
    session = ClientSession(cookies={'PROCRASTINATION_SESSION': session_key}, json_serialize=ujson.dumps)
    async with session.post(URL.RATE_FACT.value, json={'command': rate_command}):
        await session.close()


async def get_random_rated_fact(state: FSMContext, search_type: str) -> tuple[str, str]:
    """Process Http request to get random rated fact"""
    if search_type == CurrentTask.GET_NEW_FACT:
        url = URL.RANDOM_RATED_FACT.value + SearchType.NEW_FACTS.value
    else:
        url = URL.RANDOM_RATED_FACT.value + SearchType.TOP_FACTS.value
    async with state.proxy() as data:
        session_key = data['session_key']
    session = ClientSession(cookies={'PROCRASTINATION_SESSION': session_key})
    async with session.get(url) as response:
        result = await response.json(loads=ujson.loads)
        await session.close()
    return result['random_rated_fact'], result['title_name']


async def process_authorization_error_scenario(
        message: types.Message,
        response: Union[dict[str], str],
        process_type: str,
):
    """Process authorization errors"""
    if isinstance(response, dict):
        error = response['error']
    else:
        error = response
    await message.answer(
        error + '. ' + f' Get back to the login page or start {process_type} '
                       f'process again by typing your username again',
        reply_markup=create_inline_keyboard([CurrentTask.LOGIN_PAGE.value]),
    )
    await AuthorizationForm.username.set()


async def show_login_menu(bot: Bot, chat_id: int):
    """Process showing login menu"""
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


async def process_successful_authorization(message: types.Message, authorization_type: str):
    """Process successful authorization"""
    await message.answer(
        f'Successful {authorization_type}', reply_markup=create_inline_keyboard(
            [
                'Get random fact',
                'Try something new',
                CurrentTask.LOGIN_PAGE.value,
            ],
            callback_queries=
            (
                CurrentTask.GET_TOP_FACT.value,
                CurrentTask.GET_NEW_FACT.value,
                CurrentTask.LOGIN_PAGE.value
            )
        ),
    )
    await MainForm.work_process.set()


async def register_user(user_info: dict[str]) -> tuple[Union[dict[str], str], bool]:
    """Process Http request to api to register user"""
    session = ClientSession(json_serialize=ujson.dumps)
    async with session.post(URL.REGISTER.value, json=user_info) as response:
        content_type = response.content_type
        if content_type != ContentType.JSON.value:
            successful = False
            error_text = await response.text()
            return error_text, successful
        result = await response.json(loads=ujson.loads)
        await session.close()
    if 'result' in result.keys() and result['result'] == 500:
        successful = True
        return result, successful
    successful = False
    return result, successful


async def login_user(user_info: dict[str], state: FSMContext) -> tuple[dict[str], bool]:
    """Process Http request to login user"""
    session = ClientSession(json_serialize=ujson.dumps)
    async with session.post(URL.LOGIN.value, json=user_info) as response:
        result = await response.json(loads=ujson.loads)
        await session.close()
    if 'result' in result.keys() and result['result'] == 500:
        successful = True
        async with state.proxy() as data:
            data['session_key'] = response.cookies['PROCRASTINATION_SESSION']
        return result, successful
    successful = False
    return result, successful


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

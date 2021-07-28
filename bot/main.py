"""Main bot handlers"""
from typing import Union
from aiogram import Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.dispatcher import filters
from aiogram.dispatcher import FSMContext
from loguru import logger
from shared.constants import CurrentTask, RateCommand
from bot.authorization_handlers import register_authorization_module
from bot.constants import bot, dp, AuthorizationForm, MainForm
from bot.utilities import (
    show_login_menu,
    process_showing_random_fact,
    get_all_enum_values,
    rate_fact,
)


@dp.message_handler(commands='start')
@dp.callback_query_handler(state=MainForm.start)
async def processing_start_command_working(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(message, types.Message):
        logger.debug(f'User {message.from_user.id} has started working with bot')
        await show_login_menu(bot, message.from_user.id)
        await MainForm.start.set()
        return
    if message.data == 'No':
        async with state.proxy() as data:
            data['current_task'] = CurrentTask.REGISTRATION.value
        logger.debug(f'Starting up registration process by telegram user: {message.from_user.id}')
        await bot.send_message(
            message.from_user.id,
            'Type your username',
        )
        await AuthorizationForm.username.set()
        return
    async with state.proxy() as data:
        data['current_task'] = CurrentTask.LOGIN.value
    logger.debug(f'Starting up authentication process by telegram user: {message.from_user.id}')
    await bot.send_message(message.from_user.id, 'Type your username')
    await AuthorizationForm.username.set()
    return


@dp.callback_query_handler(filters.Regexp(regexp=CurrentTask.LOGIN_PAGE.value), state='*')
async def get_back_to_login_page(message: types.CallbackQuery, state: FSMContext):
    """Get user back to main page"""
    await state.reset_data()
    await show_login_menu(bot, message.from_user.id)
    await MainForm.start.set()
    return


@dp.callback_query_handler(state=MainForm.work_process)
async def process_getting_random_fact(message: types.CallbackQuery, state: FSMContext):
    """Get random rated fact"""
    commands = get_all_enum_values(RateCommand)
    if message.data in commands:
        await rate_fact(state, message.data)
    await process_showing_random_fact(bot, state, message, commands)
    return


async def on_startup(dispatcher: Dispatcher):
    logger.info('Register modules handlers')
    register_authorization_module(dispatcher)
    logger.info('Finished Starting up bot')


async def on_shutdown(dispatcher: Dispatcher):
    logger.warning('Shutting down bot')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
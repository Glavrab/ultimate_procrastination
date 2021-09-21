from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger

from bot.constants import AuthorizationForm, MainForm
from bot.utilities import register_user, create_inline_keyboard, login_user, process_authorization_error_scenario
from shared.constants import CurrentTask


async def process_username(message: types.Message, state: FSMContext):
    """Process username submission"""
    async with state.proxy() as data:
        data['user_info'] = {
                'username': message.text,
                'password': ' ',
            }
    logger.debug(f'Telegram user: {message.from_user.id} has submitted username {message.text}')
    await message.answer('Type your password')
    await AuthorizationForm.password.set()


async def process_password(message: types.Message, state: FSMContext):
    """Process password submission"""
    async with state.proxy() as data:
        data['user_info']['password'] = message.text
    if data['current_task'] == CurrentTask.REGISTRATION.value:
        logger.debug(f'Telegram user:{message.from_user.id} has submitted password:{message.text}')
        await message.answer('Repeat your password please')
        await AuthorizationForm.repeated_password.set()
        return
    user_info = await state.get_data('user_info')
    response, successful = await login_user(user_info['user_info'], state)
    if not successful:
        await process_authorization_error_scenario(message, response, 'login')
        return
    await state.set_data({'session_key': response['PROCRASTINATION_SESSION']})
    await message.answer('Successful login!', reply_markup=create_inline_keyboard(['Get random fact']))
    await MainForm.work_process.set()


async def process_repeated_password(message: types.Message, state: FSMContext):
    """Process repeated password submission"""
    async with state.proxy() as data:
        data['user_info']['repeated_password'] = message.text
    logger.debug(f'Telegram user: {message.from_user.id} has submitted repeated password: {message.text}')
    await message.answer('Last step type your email')
    await AuthorizationForm.email.set()


async def process_email(message: types.Message, state: FSMContext):
    """Process email submission"""
    user_to_register = await state.get_data('user_info')
    user_to_register['user_info']['email'] = message.text
    logger.debug(f'Telegram user: {message.from_user.id} has submitted email: {message.text}')
    response = await register_user(user_to_register['user_info'])
    if 'result' not in response.keys():
        await process_authorization_error_scenario(message, response, 'registration')
        return
    user_info = {'username': user_to_register['username'], 'password': user_to_register['password']}
    await login_user(user_info, state)
    logger.debug(f'Successful registration by user: {user_info["username"]}')
    await message.answer('Successful registration!', reply_markup=create_inline_keyboard(['Get random fact']))
    await MainForm.work_process.set()


def register_authorization_module(dp: Dispatcher):
    """Register authorization module handlers"""
    dp.register_message_handler(process_username, state=AuthorizationForm.username)
    dp.register_message_handler(process_password, state=AuthorizationForm.password)
    dp.register_message_handler(process_repeated_password, state=AuthorizationForm.repeated_password)
    dp.register_message_handler(process_email, state=AuthorizationForm.email)
    logger.info('Finished registration of authorization module')

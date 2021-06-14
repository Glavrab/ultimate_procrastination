"""Main bot handlers"""
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
from shared.project_settings import settings
from bot.utilities import create_inline_keyboard

bot = Bot(settings.telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())


class MainState(StatesGroup):
    """States for main app"""
    logging_state = State()
    registration_state = State()


@dp.message_handler(commands='start')
async def processing_start_command_working(message: types.Message):
    logger.debug(f'User {message.from_user.id} has started working with bot')
    await message.answer(
        'Welcome to yours procrastination supporter, have you already registered?',
        reply_markup=create_inline_keyboard
        (
            [
                'Yes',
                'No',
            ]
        )
    )


async def on_startup(dispatcher: Dispatcher):
    logger.info('Starting up bot')


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
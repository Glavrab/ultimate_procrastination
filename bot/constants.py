from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from shared.project_settings import settings

bot = Bot(settings.telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())


class AuthorizationForm(StatesGroup):
    """States for registration"""
    username = State()
    password = State()
    repeated_password = State()
    email = State()


class MainForm(StatesGroup):
    """States for main app"""
    start = State()
    work_process = State()

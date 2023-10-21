import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.middlewares.logging import LoggingMiddleware

storage = MemoryStorage()

load_dotenv(dotenv_path='.env')
TOKEN = os.environ['TOKEN']
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

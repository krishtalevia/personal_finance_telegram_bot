import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import auth
from model import init_db
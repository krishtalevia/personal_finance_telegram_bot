import datetime
from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

PERIODS = {
    "день": "day",
    "неделя": "week",
    "месяц": "month",
    "год": "year",
}
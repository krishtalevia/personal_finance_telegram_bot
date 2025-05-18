from aiogram import Router, types
from aiogram.filters import Command, CommandObject

router = Router()

@router.message(Command('help'))
async def help_handler(message: types.Message):
    pass
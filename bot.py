import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import auth, start, income, expense, transactions, goals, statistics
from model import init_db

async def main():
    bot = Bot(token=TOKEN) 
    dp = Dispatcher()

    init_db()

    dp.include_routers(start.router)
    dp.include_routers(auth.router)
    dp.include_routers(income.router)
    dp.include_routers(expense.router)
    dp.include_routers(transactions.router)
    dp.include_routers(goals.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
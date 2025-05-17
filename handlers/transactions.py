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

def get_date_range_for_period(period_keyword):
    today = datetime.date.today()
    period_start = None
    period_end = today

    if period_keyword == "day":
        period_start = today
    elif period_keyword == "week":
        period_start = today - datetime.timedelta(days=today.weekday())
    elif period_keyword == "month":
        period_start = today.replace(day=1)
    elif period_keyword == "year":
        period_start = today.replace(month=1, day=1)
    
    if period_start:
        return period_start.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d')
    return None, None

@router.message(Command('view_transactions'))
async def view_transactions_handler(message: types.Message):
    telegram_id = message.from_user.id

    user = db_manager.get_user(telegram_id)
    if not user:
        await message.answer('❌ Вы не зарегистрированы. Используйте команду /register для регистрации.')
        return
    
    if not db_manager.is_user_authorized(telegram_id):
        await message.answer('❌ Вы не авторизованы. Используйте команду /login для авторизации.')
        return
    
    args_str = message.get_args()
    args_list = args_str.split() if args_str else []

    period_start_str = None
    period_end_str = None
    category_name_filter = None
    
    current_period_keyword = "month" 

    if not args_list:
        period_start_str, period_end_str = get_date_range_for_period(current_period_keyword)
    else:
        potential_period = args_list[0].lower()
        if potential_period in PERIODS:
            period_keyword_from_user = PERIODS[potential_period]
            period_start_str, period_end_str = get_date_range_for_period(period_keyword_from_user)
            if len(args_list) > 1:
                category_name_filter = " ".join(args_list[1:])
        
        else:
            category_name_filter = " ".join(args_list)
            period_start_str, period_end_str = get_date_range_for_period(current_period_keyword)

    if not period_start_str or not period_end_str:
        await message.answer("⚠️ Не удалось определить период. Попробуйте: 'день', 'неделя', 'месяц', 'год'.")
        return
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

@router.message(Command('statistics'))
async def statistics_handler(message: types.Message):
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

    period_keyword_from_user = "month"
    period_display_name = "Текущий месяц"

    if args_list:
        potential_period_arg = args_list[0].lower()
        if potential_period_arg in PERIODS:
            period_keyword_from_user = PERIODS[potential_period_arg]
            for display, keyword_val in PERIODS.items():
                if keyword_val == period_keyword_from_user:
                    period_display_name = display.capitalize()
                    break

    period_start_str, period_end_str = get_date_range_for_period(period_keyword_from_user)

    if not period_start_str or not period_end_str:
        await message.answer("⚠️ Не удалось определить период для статистики.")
        return
    
    try:
        transactions = db_manager.get_transactions(
            telegram_id, 
            period_start_str=period_start_str, 
            period_end_str=period_end_str
        )

    except Exception as e:
        await message.answer("❌ Произошла ошибка при получении транзакций для статистики.")
        return
    
    total_income = 0.0
    total_expense = 0.0
    incomes_by_category = {}
    expenses_by_category = {} 

    if transactions:
        for tr in transactions:
            tr_type = tr[1] 
            tr_amount = tr[2]
            tr_category = tr[3]
            
            if tr_type == 'income':
                total_income += tr_amount
                incomes_by_category[tr_category] = incomes_by_category.get(tr_category, 0) + tr_amount
            elif tr_type == 'expense':
                total_expense += tr_amount
                expenses_by_category[tr_category] = expenses_by_category.get(tr_category, 0) + tr_amount
    
    net_balance = total_income - total_expense

    response_lines = [
        f"📊 Статистика за период: {period_display_name} ({period_start_str} - {period_end_str})\n",
        f"🟢 Общий доход: {total_income:.2f}",
        f"🔴 Общий расход: {total_expense:.2f}",
        f"⚖️ Чистый баланс: {net_balance:.2f}"
    ]

    if expenses_by_category:
        response_lines.append("\n📈 Структура расходов:")
        
        sorted_expenses = sorted(expenses_by_category.items(), key=lambda item: item[1], reverse=True)
        for category, amount in sorted_expenses:
            percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
            response_lines.append(f"  - {category}: {amount:.2f} ({percentage:.1f}%)")
    else:
        if total_expense == 0 and transactions:
             response_lines.append("\n📈 Расходов за период не было.")

    await message.answer("\n".join(response_lines))
# Импортируем необходимые библиотеки
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from datetime import datetime, timedelta
import pytz
from telegram.ext import ChatMemberHandler, filters

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Массив расписания занятий
schedule_data = [
    {'date': '10.09.2024', 'time': '18:00', 'title': "Занятие по JS - Спринт 1 Занятие 1"},
    {'date': '17.09.2024', 'time': '18:00', 'title': "Занятие по JS - Спринт 1 Занятие 2"},
    {'date': '24.09.2024', 'time': '01:00', 'title': "Занятие по JS - Спринт 1 Занятие 3"},
    {'date': '24.09.2024', 'time': '18:00', 'title': "Занятие по JS - Спринт 1 Занятие 3"},
    {'date': '01.10.2024', 'time': '18:00', 'title': "Занятие по JS - Спринт 1 Занятие 4"},

    {'date': '09.09.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 1"},
    {'date': '16.09.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 2"},
    {'date': '23.09.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 3"},
    {'date': '30.09.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 4"},
    {'date': '03.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 3"},
    {'date': '04.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 1 Занятие 3 (доп)"},

    {'date': '08.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 Занятие 1"},
    {'date': '09.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 (доп)"},
    {'date': '15.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 Занятие 2"},
    {'date': '16.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 (доп)"},
    {'date': '18.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 (доп)"},
    {'date': '22.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 Занятие 3"},
    {'date': '29.10.2024', 'time': '18:00', 'title': "Занятие по React - Спринт 2 Занятие 4"},
 

]

# Часовой пояс
tz = pytz.timezone('Europe/Moscow')

# Команда для просмотра расписания
async def schedule_command(update: Update, context: CallbackContext):
    await show_schedule(update)

# Команда для добавления занятия
ADMIN_USER_IDS = [697761704]  # Замените на ваши ID пользователей

async def add_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("У вас нет прав на добавление занятий.")
        return

    await update.message.reply_text("Введите дату занятия (в формате ДД.ММ.ГГГГ):")
    context.user_data['adding'] = True
    context.user_data['step'] = 'date'  # Добавляем шаг
    context.user_data['current_event'] = {}

async def handle_message(update: Update, context: CallbackContext):
    if 'adding' in context.user_data and context.user_data['adding']:
        step = context.user_data['step']
        if step == 'date':
            context.user_data['current_event']['date'] = update.message.text
            await update.message.reply_text("Введите время занятия (в формате ЧЧ:ММ):")
            context.user_data['step'] = 'time'
        elif step == 'time':
            context.user_data['current_event']['time'] = update.message.text
            await update.message.reply_text("Введите название занятия:")
            context.user_data['step'] = 'title'
        elif step == 'title':
            context.user_data['current_event']['title'] = update.message.text
            new_event = context.user_data['current_event']
            schedule_data.append(new_event)  # Добавляем новое занятие в расписание
            await update.message.reply_text(f"Занятие '{new_event['title']}' добавлено в расписание на {new_event['date']} в {new_event['time']}.")
            context.user_data.clear()  # Очистка состояния после завершения добавления

# Функция для отображения расписания
# Функция для отображения расписания
async def show_schedule(query):
    now = datetime.now(tz)  # Текущее время с учетом часового пояса
    # Фильтруем расписание, оставляя только предстоящие занятия
    upcoming_events = [
        event for event in schedule_data
        if datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M').astimezone(tz) > now
    ]

    if upcoming_events:
        message = "📅 Расписание предстоящих занятий на месяц:\n\n"
        for event in upcoming_events:
            if "доп" in event['title']:
                type_message = "📝 Это дополнительное занятие.\n"
            else:
                type_message = "📚 Это основное занятие.\n"

            if "JS" in event['title']:
                message += (
                    f"🌟 **Занятие по JavaScript!** 🚀\n"
                    f"{type_message}"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨\n\n"
                )
            elif "React" in event['title']:
                message += (
                    f"⚛️ **Занятие по React!** 🌐\n"
                    f"{type_message}"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻\n\n"
                )
            else:
                message += (
                    f"{type_message}"
                    f"🗓️ {event['date']} ⏰ {event['time']} - {event['title']}\n\n"
                )
    else:
        message = "На данный момент занятий больше нет."

    await query.edit_message_text(message)  # Правильное использование для редактирования сообщения

# Функция для отображения только доп. или основных занятий
async def show_filtered_schedule(update: Update, extra: bool):
    now = datetime.now(tz)  # Текущее время с учетом часового пояса
    
    # Фильтруем только предстоящие занятия
    sorted_schedule = sorted(
        [event for event in schedule_data if datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M').astimezone(tz) > now],
        key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", '%d.%m.%Y %H:%M').astimezone(tz)
    )

    if extra:
        # Фильтруем только доп. занятия
        filtered_schedule = [event for event in sorted_schedule if "доп" in event['title']]
        message_title = "📅 Расписание доп. занятий:\n\n"
    else:
        # Фильтруем только основные занятия
        filtered_schedule = [event for event in sorted_schedule if "доп" not in event['title']]
        message_title = "📅 Расписание основных занятий:\n\n"

    if filtered_schedule:
        message = message_title
        for event in filtered_schedule:
            if "доп" in event['title']:
                type_message = "📝 Это дополнительное занятие.\n"
            else:
                type_message = "📚 Это основное занятие.\n"

            if "JS" in event['title']:
                message += (
                    f"🌟 **Занятие по JavaScript!** 🚀\n"
                    f"{type_message}"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨\n\n"
                )
            elif "React" in event['title']:
                message += (
                    f"⚛️ **Занятие по React!** 🌐\n"
                    f"{type_message}"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻\n\n"
                )
            else:
                message += (
                    f"{type_message}"
                    f"🗓️ {event['date']} ⏰ {event['time']} - {event['title']}\n\n"
                )
    else:
        message = "На данный момент занятий больше нет."

    await update.message.edit_text(message)  # Правильное использование для редактирования сообщения



# Функция для отображения только доп. или основных занятий
async def show_filtered_schedule(update: Update, extra: bool):
    now = datetime.now(tz)  # Текущее время с учетом часового пояса
    
    # Фильтруем только предстоящие занятия
    sorted_schedule = sorted(
        [event for event in schedule_data if datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M').astimezone(tz) > now],
        key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", '%d.%m.%Y %H:%M').astimezone(tz)
    )

    if extra:
        # Фильтруем только доп. занятия
        filtered_schedule = [event for event in sorted_schedule if "доп" in event['title']]
        message_title = "📅 Расписание доп. занятий:\n\n"
    else:
        # Фильтруем только основные занятия
        filtered_schedule = [event for event in sorted_schedule if "доп" not in event['title']]
        message_title = "📅 Расписание основных занятий:\n\n"

    if filtered_schedule:
        message = message_title
        for event in filtered_schedule:
            if "JS" in event['title']:
                message += (
                    f"🌟 **Занятие по JavaScript!** 🚀\n"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨\n\n"
                )
            elif "React" in event['title']:
                message += (
                    f"⚛️ **Занятие по React!** 🌐\n"
                    f"🗓️ Дата: {event['date']}\n"
                    f"⏰ Время: {event['time']}\n"
                    f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻\n\n"
                )
            else:
                message += f"🗓️ {event['date']} ⏰ {event['time']} - {event['title']}\n\n"
    else:
        message = "На данный момент занятий больше нет."

    await update.message.edit_text(message)  # Правильное использование для редактирования сообщения

# Команда для вывода списка команд
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Доступные команды:\n"
        "/start - Ниже есть кнопка показать расписание или используйте команду /schedule\n"
        "/next - Следующее занятие\n"
        "/schedule - Показать расписание занятий на месяц\n"
        "/help - Показать список команд и их описание\n"
        "/add - Добавить новое занятие в расписание (только для администраторов!)\n"
    )
    await update.message.reply_text(help_text)

# Функция для отправки уведомлений
tz_moscow = pytz.timezone('Europe/Moscow')

# Функция для отправки уведомлений
async def notify_about_event(application, chat_id, event):
    try:
        logger.info(f"Sending notification for event: {event['title']} to chat_id: {chat_id}")
        
        # Преобразуем время события в московский часовой пояс
        event_datetime = datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M')
        event_datetime_moscow = tz_moscow.localize(event_datetime)

        if "JS" in event['title']:
            if "доп" in event['title']:
                message = (
                    f"💡 Напоминание: через 30 минут начнётся:\n"
                    f"🌟 **Дополнительное занятие по JavaScript!** 🚀\n"
                    f"🗓️ Дата: {event_datetime_moscow.strftime('%d.%m.%Y')}\n"
                    f"⏰ Время: {event_datetime_moscow.strftime('%H:%M')}\n"
                    f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨"
                )
            else:
                message = (
                    f"💡 Напоминание: через 30 минут начнётся:\n"
                    f"🌟 **Основное занятие по JavaScript!** 🚀\n"
                    f"🗓️ Дата: {event_datetime_moscow.strftime('%d.%m.%Y')}\n"
                    f"⏰ Время: {event_datetime_moscow.strftime('%H:%M')}\n"
                    f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨"
                )
        elif "React" in event['title']:
            if "доп" in event['title']:
                message = (
                    f"💡 Напоминание: через 30 минут начнётся:\n"
                    f"⚛️ **Дополнительное занятие по React!** 🌐\n"
                    f"🗓️ Дата: {event_datetime_moscow.strftime('%d.%m.%Y')}\n"
                    f"⏰ Время: {event_datetime_moscow.strftime('%H:%M')}\n"
                    f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻"
                )
            else:
                message = (
                    f"💡 Напоминание: через 30 минут начнётся:\n"
                    f"⚛️ **Основное занятие по React!** 🌐\n"
                    f"🗓️ Дата: {event_datetime_moscow.strftime('%d.%m.%Y')}\n"
                    f"⏰ Время: {event_datetime_moscow.strftime('%H:%M')}\n"
                    f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻"
                )
        else:
            message = (
                f"💡 Напоминание: через 30 минут начнётся '{event['title']}' в "
                f"{event_datetime_moscow.strftime('%H:%M')}!"
            )
        
        await application.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

async def check_schedule(context: CallbackContext):
    application = context.application
    chat_id = context.job.chat_id
    now = datetime.now(tz_moscow)  # Текущее московское время
    logger.info(f"Checking schedule at {now}")

    for event in schedule_data:
        event_datetime = datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M')
        event_datetime_moscow = tz_moscow.localize(event_datetime)  # Преобразуем в московский часовой пояс
        logger.info(f"Event '{event['title']}' datetime: {event_datetime_moscow}")

        # Проверяем, если до начала события осталось 30 минут или меньше и уведомление еще не отправлено
        if not event.get('notified') and now + timedelta(minutes=30) >= event_datetime_moscow > now:
            logger.info(f"Sending notification for event '{event['title']}'")
            await notify_about_event(application, chat_id, event)
            event['notified'] = True  # Отмечаем, что уведомление было отправлено
        elif event_datetime_moscow <= now:
            event['notified'] = False  # Сбрасываем флаг уведомления для прошедших событий 
# Функция для получения следующего занятия
async def next_event_command(update: Update, context: CallbackContext):
    now = datetime.now(tz)  # Получаем текущее время с учетом часового пояса
    logger.info("Команда /next получена.")
    
    upcoming_events = [
        event for event in schedule_data
        if datetime.strptime(f"{event['date']} {event['time']}", '%d.%m.%Y %H:%M').astimezone(tz) > now
    ]
    
    logger.info(f"Предстоящие занятия: {upcoming_events}")

    if upcoming_events:
        next_event = min(
            upcoming_events,
            key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", '%d.%m.%Y %H:%M').astimezone(tz)
        )
        
        if "JS" in next_event['title']:
            message = (
                f"🌟 **Следующее занятие по JavaScript!** 🚀\n"
                f"🗓️ Дата: {next_event['date']}\n"
                f"⏰ Время: {next_event['time']}\n"
                f"📚 Готовьтесь к увлекательному погружению в мир JS! 💻✨"
            )
        elif "React" in next_event['title']:
            message = (
                f"⚛️ **Следующее занятие по React!** 🌐\n"
                f"🗓️ Дата: {next_event['date']}\n"
                f"⏰ Время: {next_event['time']}\n"
                f"🌟 Давайте создадим потрясающие интерфейсы вместе! 🎉💻"
            )
        else:
            message = f"Следующее занятие: '{next_event['title']}' на {next_event['date']} в {next_event['time']}."
        
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Занятий больше нет.")

# Функция для обработки нажатия на кнопку
# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Обязательно нужно подтверждать callback запрос

    # Обрабатываем нажатие на разные кнопки
    if query.data == 'show_schedule':
        await show_schedule(query)  # Передаем query
    elif query.data == 'show_extra':
        await show_filtered_schedule(query, extra=True)
    elif query.data == 'show_main':
        await show_filtered_schedule(query, extra=False)

    query = update.callback_query
    await query.answer()  # Обязательно нужно подтверждать callback запрос

    # Обрабатываем нажатие на разные кнопки
    if query.data == 'show_schedule':
        await show_schedule(query)  # Pass query directly
    elif query.data == 'show_extra':
        await show_filtered_schedule(query, extra=True)
    elif query.data == 'show_main':
        await show_filtered_schedule(query, extra=False)
# Функция для отображения только доп. или основных занятий
# Функция для отображения только доп. или основных занятий
from telegram import Update
from telegram.ext import CallbackQueryHandler
from datetime import datetime

# Функция для создания кнопки
# Обновляем команду /start для добавления новых кнопок
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📅 Показать расписание", callback_data='show_schedule')],
        [InlineKeyboardButton("🔧 Показать только доп", callback_data='show_extra')],
        [InlineKeyboardButton("📚 Показать основные", callback_data='show_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать! Выберите опцию ниже:', reply_markup=reply_markup)

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Обязательно нужно подтверждать callback запрос

    # Обрабатываем нажатие на разные кнопки
    if query.data == 'show_schedule':
        await show_schedule(query)  # Передаем сообщение
    elif query.data == 'show_extra':
        await show_filtered_schedule(query, extra=True)
    elif query.data == 'show_main':
        await show_filtered_schedule(query, extra=False)

from telegram.ext import ChatMemberHandler

# Функция приветствия новых пользователей
async def greet_new_user(update: Update, context: CallbackContext):
    new_members = update.message.new_chat_members  # Получаем список новых пользователей
    for member in new_members:
        if not member.is_bot:  # Проверяем, что новый участник не бот
            first_name = member.first_name  # Получаем имя нового участника
            username = member.username if member.username else first_name  # Получаем username, если он есть
            greeting_message = (
                f"👋 Привет, {first_name}! Добро пожаловать в нашу группу! 🎉\n"
                "Команды бота: 🤖\n"
                "🗓 /start - для получения расписания,\n"
                "🗓 /next - получить расписание на ближайший урок.\n"
                "Если тебе что-то непонятно или нужна помощь, не стесняйся задавать вопросы! 💻✨"
            )
            await update.message.reply_text(greeting_message)  # Отправляем приветственное сообщение

# Подключаем обработчик событий добавления новых участников
if __name__ == '__main__':
    TOKEN = '7728288925:AAGF00CJj_u7hD5vn2Qh7hWXpT-iPtJvWxY'
    GROUP_CHAT_ID = -1002238351805  # Замени на ID твоей группы

    # Создание бота
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем команды
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("next", next_event_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Один обработчик для всех шагов
    app.add_handler(CallbackQueryHandler(button_handler, pattern='show_schedule'))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_user))

# Добавляем обработчики для кнопок фильтрации
    app.add_handler(CallbackQueryHandler(button_handler, pattern='show_extra'))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='show_main'))

    # Использование JobQueue для планирования регулярных проверок расписания
    job_queue = app.job_queue
    job_queue.run_repeating(check_schedule, interval=60, first=10, chat_id=GROUP_CHAT_ID)

    logger.info("Bot started")
    # Запуск бота
    app.run_polling()

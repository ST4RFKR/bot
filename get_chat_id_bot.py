from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Функция для получения chat_id
async def get_chat_id(update: Update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

if __name__ == '__main__':
    # Вставь сюда свой токен
    app = ApplicationBuilder().token('7728288925:AAGF00CJj_u7hD5vn2Qh7hWXpT-iPtJvWxY').build()

    # Команда /get_chat_id для получения идентификатора группы
    app.add_handler(CommandHandler("get_chat_id", get_chat_id))

    # Запуск бота
    app.run_polling()

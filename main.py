from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

def creds_loading():
    with open('credentials.txt') as f:
        token = f.readline().strip()
        bot_username = f.readline().strip()

    return token, bot_username


def main():
    token, bot_username = creds_loading()
    bot_loading(token, bot_username)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton('Начать вести журнал', callback_data = 'consent')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        f"Привет {user.mention_html()}!\nЭтот бот был создан как вольный проект по запросу прекрасной дамы.\nОн позволит тебе создать журнал дисфункциональных мыслей с помощью нашего диалога.", reply_markup=reply_markup
    )


async def query_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await chat_add_dialogue(update.callback_query, context)


async def chat_add_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.edit_text('Теперь создай пустую группу и добавь меня туда.\n\nКак только я буду добавлен')


def bot_loading(token, bot_username):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(query_buttons))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


    


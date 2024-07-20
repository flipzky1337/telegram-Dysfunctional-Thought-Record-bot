from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters
from telegram.constants import ParseMode

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


def status_change_handling(chat_member_update: ChatMemberUpdated):
    status_change = chat_member_update.difference().get('status')
    old_is_member, new_is_member = chat_member_update.difference().get('is_member', (None, None))

    if status_change is None:
        return None
    
    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = status_change_handling(update.my_chat_member)
    if result is None:
        return
    
    was_member, is_member = result

    cause_name = update.effective_user.full_name

    chat = update.effective_chat
    if chat.type == Chat.GROUP or Chat.SUPERGROUP:
        if not was_member and is_member:
            print(f'{cause_name} added you to chat')
        elif was_member and not is_member:
            print(f'{cause_name} deleted you from the chat')


def bot_loading(token, bot_username):
    app = Application.builder().token(token).build()

    #start command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(query_buttons))


    #chat member tracking
    app.add_handler(ChatMemberHandler(track_group, ChatMemberHandler.MY_CHAT_MEMBER))


    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


    


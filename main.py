from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, ChatMember, \
    ChatMemberUpdated, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, \
    ChatMemberHandler, PicklePersistence, filters, ConversationHandler

from database import Database

SITUATION, THOUGHTS, REACTIONS, PROS, CONS, CONCLUSIONS = range(6)


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
        [InlineKeyboardButton('Начать вести журнал', callback_data='consent')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        f"Привет {user.mention_html()}!\nЭтот бот был создан как вольный проект по запросу прекрасной дамы.\nОн позволит вам создать журнал дисфункциональных мыслей с помощью нашего диалога.",
        reply_markup=reply_markup
    )


async def query_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await chat_add_dialogue(update.callback_query,
                            context)  # idk why, it just won't take update without the .callback_query


async def chat_add_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.edit_text(
        'Теперь создайте пустую группу и добавьте меня туда. Как только я буду добавлен, вернитесь в этот диалог.')


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


async def user_group_storing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.GROUP:
        if not db.check_if_exists(str(update.effective_user.id)):
            db.set(str(update.effective_user.id), str(update.effective_chat.id))
            db.save()
            await update.message.reply_html('Чат успешно привязан! Вернитесь в диалог для продолжения.')
            await default_state(update, context)
        else:
            await update.message.reply_html(
                'Вы уже имеете привязанную группу, используйте /unlink.')

    else:
        await update.message.reply_html('Ататай. Вводите эту команду в группе!')


async def unlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if db.check_if_exists(str(update.effective_user.id)):
        db.remove(str(update.effective_user.id))
        db.save()
        await update.message.reply_html('Чат успешно отвязан!')


async def default_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton('Добавить запись ✍️')],
               [KeyboardButton('Отвязать группу '),
                InlineKeyboardButton('Донат 😍')]]
    await context.bot.send_message(chat_id=update.effective_user.id, text='Выберите действие:',
                                   reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,
                                                                    one_time_keyboard=True))


async def new_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id] = {}
    await update.message.reply_html('Опишите событие, вызвавшее неприятную эмоцию.')

    return SITUATION


async def situation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['situation'] = update.message.text
    await update.message.reply_html(
        'Запишите содержание мыслей, интерпретацию ситуации и вашей реакции.\nОцените, насколько правдоподобны для вас эти мысли от 1 до 100%.')

    return THOUGHTS


async def thoughts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['thoughts'] = update.message.text
    await update.message.reply_html(
        'Запишите какие реакции у вас вызвала эта ситуация: эмоции, чувства, ощущения, действия.\nОцените интенсивность реакций от 1 до 100%.')

    return REACTIONS


async def reactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['reactions'] = update.message.text
    await update.message.reply_html(
        'Какие есть доказательства правдивости мыслей?\nКакие факты говорят, что всё верно?\nВ чем преимущество, польза так мыслить?')

    return PROS


async def pros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['pros'] = update.message.text
    await update.message.reply_html(
        'Какие есть опровержения правдивости мыслей?\nВ чем можно усомниться?\nЧто говорит об обратном?\nКак объяснить ситуацию иначе?')

    return CONS


async def cons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['cons'] = update.message.text
    await update.message.reply_html('Как лучше реагировать в будущем?\nО чем следует помнить?')

    return CONCLUSIONS


async def conclusions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_journal[update.effective_user.id]['conclusions'] = update.message.text

    ready_message = f'<b>Ситуация</b>\n\n{db_journal[update.effective_user.id]['situation']}\n\n<b>Мысли</b>\n\n{db_journal[update.effective_user.id]['thoughts']}\n\n<b>Реакция</b>\n\n{db_journal[update.effective_user.id]['reactions']}\n\n<b>За</b>\n\n{db_journal[update.effective_user.id]['pros']}\n\n<b>Против</b>\n\n{db_journal[update.effective_user.id]['cons']}\n\n<b>Выводы</b>\n\n{db_journal[update.effective_user.id]['conclusions']}'

    await context.bot.send_message(chat_id=db.get(str(update.effective_user.id)),
                                   text=ready_message, parse_mode='html')
    db_journal[update.effective_user.id] = {}
    await update.message.reply_html('Запись успешно добавлена!')

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('ok')
    return ConversationHandler.END


async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html('<b>За любую поддержку выражаю глубокое спасибо и вкусно кушаю</b>\nТинькофф - 2200 7010 1874 8803, за другими реквизитами пишите мне в ЛС @saveitsky')


async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = status_change_handling(update.my_chat_member)
    if result is None:
        return

    was_member, is_member = result

    cause_name = update.effective_user.full_name

    chat = update.effective_chat
    if chat.type == Chat.GROUP or Chat.SUPERGROUP:
        if not was_member and is_member:
            await update.effective_chat.send_message(
                'Я вижу что вы меня добавили. Теперь для доступа к полному функционалу привяжите журнал с помощью /link :)')
        elif was_member and not is_member:
            await update.effective_user.send_message(
                'Я был удалён из вашего журнала, добавьте меня обратно если хотите продолжить.')


def bot_loading(token, bot_username):
    bot_persistence = PicklePersistence(filepath='persistence')

    app = Application.builder().token(token).persistence(persistence=bot_persistence).build()
    global db
    db = Database()

    global db_journal
    db_journal = {}

    # command handlers
    app.add_handler(CommandHandler('start', start))

    app.add_handler(CallbackQueryHandler(query_buttons))

    # chat member tracking
    app.add_handler(ChatMemberHandler(track_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CommandHandler('link', user_group_storing))
    app.add_handler(CommandHandler('unlink', unlink))

    # conversation handlers
    new_record_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Добавить запись"), new_record)],
        states={
            SITUATION: [MessageHandler(filters.TEXT, situation)],
            THOUGHTS: [MessageHandler(filters.TEXT, thoughts)],
            REACTIONS: [MessageHandler(filters.TEXT, reactions)],
            PROS: [MessageHandler(filters.TEXT, pros)],
            CONS: [MessageHandler(filters.TEXT, cons)],
            CONCLUSIONS: [MessageHandler(filters.TEXT, conclusions)]
        },
        fallbacks=[CommandHandler('cancel', default_state)],
    )

    app.add_handler(new_record_conv)

    # message handlers used in default state
    app.add_handler(MessageHandler(filters.Regex('Отвязать группу'), unlink))
    app.add_handler(MessageHandler(filters.Regex('Донат'), donate))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

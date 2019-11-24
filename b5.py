import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, \
    CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from private import user_creds, user_dict, srv_address, regex, PROXY, TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PASS1, PASS2, PASS3 = range(3)


def start(update: Update, context: CallbackContext):
    text = 'Привет, я бот Фабик. Отправь мне свой номер и я напомню твои пароли.'
    contact_button = KeyboardButton('Отправить контакт', request_contact=True)
    kbd = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    update.message.reply_text(text, reply_markup=kbd)
    return PASS1


def check_phone(update: Update, context: CallbackContext):
    contact = update.message.contact
    number = contact.phone_number
    if number[0] == '+':
        number = number[1:]
    logger.info("User %s %s - phone number %s", contact.first_name, contact.last_name, number)
    context.user_data['phone'] = number
    try:
        _ = user_creds[number]
        update.message.reply_text('Так-так. А напиши-ка мне пароль - название нашего посёлка.')
    except KeyError:
        update.message.reply_text('No such number.')
        return ConversationHandler.END
    return PASS2


def get_contact(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Вход в комп", callback_data='1'),
                 InlineKeyboardButton("Почта", callback_data='2')],
                [InlineKeyboardButton("Терминальник", callback_data='3'),
                 InlineKeyboardButton("UNF", callback_data='4')],
                [InlineKeyboardButton("Всё сразу", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Точно. Какой пароль показать? Или все сразу?', reply_markup=reply_markup)
    return PASS3


def pass_button(update: Update, context: CallbackContext):
    query = update.callback_query.message
    bot = context.bot
    bot.edit_message_text(chat_id=query.chat_id, message_id=query.message_id,
                          text="Напоминаю адрес сервера - {}".format(srv_address))
    bot.send_message(chat_id=query.chat_id, message_id=query.message_id, text="Selected option: {}".format(query.data))
    choice = int(query.data)
    if not choice:
        bot.send_message(chat_id=query.chat_id, message_id=query.message_id, text="Wow: 0")
    else:
        bot.send_message(chat_id=query.chat_id, message_id=query.message_id, text="Smth simple")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    return ConversationHandler.END


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    updater = Updater(TOKEN, request_kwargs=PROXY, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PASS1: [MessageHandler(Filters.contact, check_phone, pass_user_data=True)],
            PASS2: [MessageHandler(Filters.regex(regex), get_contact, pass_user_data=True)],
            PASS3: [CallbackQueryHandler(pass_button)]
        },

        fallbacks=[CommandHandler('cancel', cancel)], per_user=True
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

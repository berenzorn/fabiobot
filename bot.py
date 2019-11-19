import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from private import user_creds, srv_address, regex, PROXY, TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PASS1, PASS2, PASS3 = range(3)

def start(update, context):
    text = 'Привет, я бот Фабик. Отправь мне свой номер и я напомню твои пароли.'
    contact_button = KeyboardButton('Отправить контакт', request_contact=True)
    kbd = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    update.message.reply_text(text, reply_markup=kbd)
    return PASS1

def check_phone(update, context):
    contact = update.message.contact
    number = contact.phone_number
    if number[0] == '+':
        number = number[1:]
    logger.info("User %s %s - phone number %s", contact.first_name, contact.last_name, number)
    context.user_data['phone'] = number
    try:
        temp = user_creds[number]
        update.message.reply_text('Так-так. А напиши-ка мне пароль - название нашего посёлка.')
    except KeyError:
        update.message.reply_text('No such number.')
        return ConversationHandler.END
    return PASS2

def get_contact(update, context):
    number = context.user_data['phone']
    update.message.reply_text('Точно. Напоминаю адрес сервера - {}'.format(srv_address))
    for i in user_creds[number]:
        if i is not None:
            update.message.reply_text('Пароль: {}'.format(i))
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

if __name__ == '__main__':
    updater = Updater(TOKEN, request_kwargs=PROXY, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PASS1: [MessageHandler(Filters.contact, check_phone, pass_user_data=True)],
            PASS2: [MessageHandler(Filters.regex(regex), get_contact, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

import logging

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, \
    CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from private import user_creds, user_dict, srv_address, regex, PROXY, TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PASS1, PASS2, PASS3, PASS4, PASS5 = range(5)


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
    result = requests.get(f"http://127.0.0.1:5000/check?text={number}")
    if result.status_code == 200:
        update.message.reply_text('Так-так. А напиши-ка мне пароль - название нашего посёлка.')
    elif result.status_code == 404:
        update.message.reply_text('Нету у меня такого номера. Возможно база ещё не заполнена.')
        return ConversationHandler.END
    else:
        update.message.reply_text('Internal error.')
        return ConversationHandler.END
    return PASS2


def get_contact(update: Update, context: CallbackContext):
    update.message.reply_text('Точно. Напоминаю адрес сервера - {}'.format(srv_address))
    keyboard = [[InlineKeyboardButton("Вход в комп", callback_data='1'),
                 InlineKeyboardButton("Почта", callback_data='2'),
                 InlineKeyboardButton("Терминальник", callback_data='3'),
                 InlineKeyboardButton("УНФ", callback_data='4')],
                [InlineKeyboardButton("Всё сразу", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Какой пароль показать? Или все сразу?', reply_markup=reply_markup)
    return PASS4


def get_inline_contact(update: Update, context: CallbackContext):
    print("1st pass3")
    bot = context.bot
    print("2nd pass3")
    query = update.callback_query
    print("Im in pass3")
    keyboard = [[InlineKeyboardButton("Вход в комп", callback_data='1'),
                 InlineKeyboardButton("Почта", callback_data='2'),
                 InlineKeyboardButton("Терминальник", callback_data='3'),
                 InlineKeyboardButton("УНФ", callback_data='4')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                          text="Какой пароль показать?".format(srv_address), reply_markup=reply_markup)
    return PASS4


def pass_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    print("Im in pass4")
    types = ['Всё сразу', 'Система', 'Почта', 'Сервер', 'УНФ']
    choice = int(query.data)
    number = context.user_data['phone']
    if not choice:
        user_pass = requests.get(f"http://127.0.0.1:5000/all?text={number}").text.split("\n")
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                              text=f"{types[1]}.\nЛогин: {user_pass[0]}\nПароль: {user_pass[1]}")
        for i in range(1, 4):
            bot.send_message(chat_id=query.message.chat_id, message_id=query.message.message_id,
                             text=f"{types[i+1]}.\nЛогин: {user_pass[2*i]}\nПароль: {user_pass[2*i+1]}")
    else:
        user_pass = requests.get(f"http://127.0.0.1:5000/msg?type={choice}&text={number}").text.split(" ")
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                              text=f"{types[choice]}.\nЛогин: {user_pass[0]}\nПароль: {user_pass[1]}")
    keyboard = [[InlineKeyboardButton("Да, ещё пароль", callback_data='1'),
                 InlineKeyboardButton("Не, не надо", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=query.message.chat_id, message_id=query.message.message_id,
                     text='Чем-нибудь могу ещё помочь?', reply_markup=reply_markup)
    return PASS5


def one_more(update: Update, context: CallbackContext):
    query = update.callback_query
    choice = int(query.data)
    print("Im in pass5")
    if choice:
        print("Ret to pass3")
        return PASS3
    context.bot.send_message(chat_id=query.message.chat_id, message_id=query.message.message_id,
                             text='Агась. Хорошего дня)')
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
            PASS3: [CallbackQueryHandler(get_inline_contact)],
            PASS4: [CallbackQueryHandler(pass_button)],
            PASS5: [CallbackQueryHandler(one_more)]
        },

        fallbacks=[CommandHandler('cancel', cancel)], per_user=True
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

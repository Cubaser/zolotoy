import logging
import os

from telebot import TeleBot
from dotenv import load_dotenv

from goldparser import gold_parse

load_dotenv()
logging.basicConfig(
    filename='main.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

USERS = list(map(int, os.getenv('USERS').split(', ')))

bot = TeleBot(os.getenv('BOT_TOKEN'))


def send_message(message, chat_id):
    logging.debug('Попытка отправить сообщение в ТГ')
    try:
        bot.send_message(chat_id, message)
        logging.debug('Сообщение отправлено в ТГ')
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения в ТГ: {error}')


def do_parse(choose_url, chat_id):
    if chat_id in USERS:
        send_message(chat_id, 'Начинаю парсить, погоди чучуть')
        try:
            file, message = gold_parse(choose_url)
            logging.debug('Начало парсинга')
            logging.debug('Попытка отправить файл')
            with open(file, 'rb') as doc:
                bot.send_document(chat_id, doc, caption=message)
        except Exception as error:
            logging.error(f'Возникла ошибка при парсинге: {error}')
    else:
        send_message(chat_id, 'У тебя нет прав просить меня парсить')


@bot.message_handler(content_types=['text'])
def parse(message):
    chat = message.chat
    chat_id = chat.id
    text = message.text.lower()
    if text == 'парси цепи':
        do_parse(1, chat_id)
    elif text == 'парси браслеты':
        do_parse(0, chat_id)
    else:
        bot.send_message(
            chat_id=chat_id,
            text='Неверная команда, '
                 'Напиши мне "Парси цепи" или "Парси браслеты"'
        )


@bot.message_handler(commands=['start'])
def wake_up(message):
    chat = message.chat
    chat_id = chat.id
    message = (f'Пользователь {message.chat.username},'
               f' с id {message.from_user.id}')
    logging.info(message)
    bot.send_message(
        chat_id=chat_id,
        text='Привет я парсер! Напиши мне "Парси цепи" или "Парси браслеты"'
    )


bot.polling(interval=int(os.getenv('INTERVAL')))

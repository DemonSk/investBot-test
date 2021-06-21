from main import tickerfromuser
import telebot
from feargreed import getfear

bot = telebot.TeleBot('Api key')
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('TSLA', 'AAPL', 'GOOG', 'AMZN')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, 'Hello, I am invest bot. I can help you with your investments. Type Company ticker to begin', reply_markup=keyboard1)


@bot.message_handler(commands=['fear'])
def start_message(message):
    bot.send_message(
        message.chat.id, f'Fear at market is {getfear()}', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text:
        bot.send_message(message.chat.id, f'Checking for {message.text.upper()}. Please wait')
        price = round(float(tickerfromuser(message.text.upper())), 2)
        bot.send_message(message.chat.id, f'I think, {message.text.upper()} will be at {price} in 5 days')
    elif message.text.lower() == 'end':
        bot.send_message(message.chat.id, 'Good bye')


bot.polling()

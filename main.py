import requests
import telebot
from bs4 import BeautifulSoup as BS
from telebot import types

URL = 'https://kaktus.media/?lable=8&date=2023-11-03&order=time'
KEY_API = '6745320123:AAF-i2f9lDqInAlUOdUMHhYh5q-4ipGKHSg'

bot = telebot.TeleBot(KEY_API)

def parser(url):
    r = requests.get(url) 
    soup = BS(r.text, "html.parser")
    news = soup.find_all("div", class_="Tag--article")
    result = []
    for item in news:
        news_text = item.text.strip()
        news_link = item.find("a")["href"]
    
        result.append({"text": news_text, "link": news_link})
    return result

list_news = parser(URL)
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_nickname = message.from_user.username
    if user_nickname is None:
        user_nickname = message.from_user.first_name 
    bot.send_message(user_id, f"Здравствуйте, {user_nickname}! Выберите номер новости.")
    send_news(user_id, 0)

def send_news(user_id, news_number):
    numbers = min(20, len(list_news))
    if numbers > 0:
        news_item = list_news[news_number]
        news_text = news_item["text"]
        news_link = news_item["link"]
        bot.send_message(user_id, news_text)
        bot.send_message(user_id, news_link)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1, numbers + 1):
            button = types.KeyboardButton(str(i))
            markup.add(button)
        quit_button = types.KeyboardButton("Quit")
        markup.add(quit_button) 
        bot.send_message(user_id, "Выберите номер новости", reply_markup=markup)
    else:
        bot.send_message(user_id, "Новостей нет")

@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_number(message):
    user_id = message.chat.id
    news_number = int(message.text) - 1
    if 0 <= news_number < len(list_news):
        send_news(user_id, news_number)
    else:
        bot.send_message(user_id, "Неправильный номер новости")

@bot.message_handler(func=lambda message: message.text == "Quit")
def quit(message):
    user_id = message.chat.id
    bot.send_message(user_id, "До свидания!")
@bot.message_handler(func=lambda message: not message.text.isdigit())
def handle_invalid_number(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Такого номера нет. Выберите номер из предложенных.")
if __name__ == "__main__":
    bot.polling(none_stop=True)
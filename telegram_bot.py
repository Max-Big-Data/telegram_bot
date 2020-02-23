import telebot
from telebot import types
import const
from geopy.distance import vincenty

bot = telebot.TeleBot(const.API_TOKEN)

markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn_address = types.KeyboardButton('Адреса магазинов', request_location=True)
btn_payment = types.KeyboardButton('Способы оплаты')
btn_delivery = types.KeyboardButton('Способы доставки')
markup_menu.add(btn_address, btn_payment, btn_delivery)

markup_inline_payment = types.InlineKeyboardMarkup()
btn_in_cash = types.InlineKeyboardButton('Наличные', callback_data='cash')
btn_in_card = types.InlineKeyboardButton('Карточкой', callback_data='card')
btn_in_invoice = types.InlineKeyboardButton('Банковский перевод', callback_data='invoice')
markup_inline_payment.add(btn_in_cash, btn_in_card, btn_in_invoice)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я умный бот. Чем могу помочь?", reply_markup=markup_menu)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Способы доставки":
        bot.reply_to(message, "Доставка курьером, самовывоз, почтой.", reply_markup=markup_menu)
    elif message.text == "Способы оплаты":
        bot.reply_to(message, "В наших магазинах доступны сповобы оплаты", reply_markup=markup_inline_payment)
    else:
        bot.reply_to(message, message.text, reply_markup=markup_menu)


@bot.message_handler(func=lambda message: True, content_types=['location'])
def magazin_location(message):
    lat = message.location.latitude
    lon = message.location.longitude

    distance = []
    for m in const.MAGAZINS:
        result = vincenty((m['lat_m'], m['lon_m']), (lat, lon)).kilometers
        distance.append(result)
    index = distance.index(min(distance))

    bot.send_message(message.chat.id, 'Ближайший к вам магазин')
    bot.send_venue(message.chat.id,
                   const.MAGAZINS[index]['lat_m'],
                   const.MAGAZINS[index]['lon_m'],
                   const.MAGAZINS[index]['title'],
                   const.MAGAZINS[index]['address'])


@bot.callback_query_handler(func=lambda call: True)
def call_back_payment(call):
    if call.data == "cash":
        bot.send_message(call.message.chat.id, text="""
        Наличная оплата производится в рублях в кассе магазина.
        """, reply_markup=markup_inline_payment)


bot.polling()

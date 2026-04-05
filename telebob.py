import telebot
from telebot import types

BOT_TOKEN = '8695292670:AAFvMpCrl3Tn0G1GR5tkS4Hh5waFiFG2Feo'

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}


noise_sources = []
noise_time = []
noise_persistence = []
noise_symptoms = []


keyboard_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_time = types.InlineKeyboardMarkup(row_width=2)
keyboard_persistence = types.InlineKeyboardMarkup(row_width=2)
keyboard_symptoms = types.InlineKeyboardMarkup(row_width=2)

for i in noise_sources:
    keyboard_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_time:
    keyboard_time.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_persistence:
    keyboard_persistence.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_symptoms:
    keyboard_symptoms.add(types.InlineKeyboardButton(i, callback_data=i))
keyboard_symptoms.add(types.InlineKeyboardButton("Готово", callback_data='Ready'))





@bot.message_handler(commands = ['start'])
def start(message):

    bot.send_message(message.chat.id, 'hello world')

    user_id = message.chat.id
    user_data[user_id] = {'last_request':None, 'complaint_step':'source', 'source':None, 'place':None, 'time':None, 'persistence':None, 'duration':None, 'symptoms':[]}

@bot.message_handler(commands = ['complaint'])
def complaint_start(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {'last_request':'complaint', 'complaint_step':'source', 'source':None, 'place':None, 'time':None, 'persistence':None, 'duration':None, 'symptoms':[]}
    user_data[user_id]['last_request'] = 'complaint'
    bot.send_message(user_id, "Выберите источник шума", reply_markup=keyboard_sources)

@bot.message_handler(content_types = ['text'])
def text(message):
    user_id = message.chat.id
    if user_id not in user_data:
        bot.send_message(user_id, "Выберите действие")
        return
    data = message.text
    match user_data[user_id]['last_request']:
        case 'complaint':
            if user_data[user_id]['complaint_step'] == 'place':
                user_data[user_id]['place'] = data
                bot.send_message(user_id, "Выберите время, когда был зафиксирован шум", reply_markup=keyboard_time)
                user_data[user_id]['complaint_step'] = 'time'
            elif user_data[user_id]['complaint_step'] == 'duration':
                user_data[user_id]['duration'] = data
                bot.send_message(user_id, "Выберите симптомы, вызываемые шумом", reply_markup=keyboard_symptoms)
                user_data[user_id]['complaint_step'] = 'symptoms'
        case _:
            return 1

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    bot.answer_callback_query(call.id)
    
    user_id = call.message.chat.id
    data = call.data
    match user_data[user_id]['last_request']:
        case 'complaint':
            if user_data[user_id]['complaint_step'] == 'source':
                user_data[user_id]['source'] = data
                bot.send_message(user_id, "Введите адрес, где зафиксирован шум")
                user_data[user_id]['complaint_step'] = 'place'
            elif user_data[user_id]['complaint_step'] == 'time':
                user_data[user_id]['time'] = data
                bot.send_message(user_id, "Выберите, как часто вы слышите шум", reply_markup=keyboard_persistence)
                user_data[user_id]['complaint_step'] = 'persistence'
            elif user_data[user_id]['complaint_step'] == 'persistence':
                user_data[user_id]['persistence'] = data
                bot.send_message(user_id, "Введите сколько часов длится шум")
                user_data[user_id]['complaint_step'] = 'duration'
            elif user_data[user_id]['complaint_step'] == 'symptoms':                
                if data != 'Ready':
                    if data not in symptoms:
                        user_data[user_id]['symptoms'].append(data)
                else:
                    user_data[user_id]['complaint_step'] = 'ready'
                    bot.send_message(user_id, "Ваше обращение готово")

bot.polling()

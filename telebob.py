import telebot
from telebot import types

BOT_TOKEN = '8695292670:AAFvMpCrl3Tn0G1GR5tkS4Hh5waFiFG2Feo'

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

#Группы шума
noise_groups_sources = [
    "Шум от транспорта",
    "Шум от стройки",
    "Шум от соседей",
    "Шум от инфраструктуры",
    "Шум от животных",
    "Шум от предприятий и организаций"
]
#Источники транспотного шума
noise_transport_sources = [
    "Транспорт на магистралях",
    "Громкая работа двигателей",
    "Состояние трамвайных путей",
    "Железнодорожный транспорт"
]
#Источники строительного шума
noise_building_sources = [
    "Работы вне разрешенного времени",
    "Использование громкого инструмента"
]
#Источники шума от соседей
noise_neighbour_sources = [
    "Громкие бытовые приборы",
    "Ремонтные работы вне разрешенного времени",
    "Поведение соседей"
]
#Источники шума от инфраструктуры
noise_infrastructure_sources = [
    "Громкая работа элементов вентиляции",
    "Громкая работа элементов жилого дома"
]
#Источники шума от животных
noise_animal_sources = [
    "Животные во дврое",
    "Животные в квартире"
]
#Источники шума от предприятий и организаций
noise_commercial_sources = [
    "Громкая реклама",
    "Общественное заведение",
    "Шумное предприятие"
]
#Временные промежутки
noise_time = [
    "Ночь (23:00-07:00)",
    "Утро (07:00-11:00)",
    "День (11:00-18:00)",
    "Вечер (18:00-23:00)",
    "Только в светлое время суток",
    "Только в темное время суток",
    "Круглосуточно"
]
#Длительность шума
noise_persistence = [
    "Несколько дней",
    "Несколько недель",
    "Несколько месяцев",
    "Год и более"
]
#Вызываемые шумом симптомы
noise_symptoms = [
    "Нарушение сна",
    "Головные боли",
    "Звон в ушах",
    "Головокружение",
    "Раздражительность"
]


keyboard_groups_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_transport_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_building_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_neighbour_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_infrastructure_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_animal_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_commercial_sources = types.InlineKeyboardMarkup(row_width=2)
keyboard_time = types.InlineKeyboardMarkup(row_width=2)
keyboard_persistence = types.InlineKeyboardMarkup(row_width=2)
keyboard_symptoms = types.InlineKeyboardMarkup(row_width=2)

for i in noise_groups_sources:
    keyboard_groups_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_transport_sources:
    keyboard_transport_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_building_sources:
    keyboard_building_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_neighbour_sources:
    keyboard_neighbour_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_infrastructure_sources:
    keyboard_infrastructure_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_animal_sources:
    keyboard_animal_sources.add(types.InlineKeyboardButton(i, callback_data=i))
for i in noise_commercial_sources:
    keyboard_commercial_sources.add(types.InlineKeyboardButton(i, callback_data=i))
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
    user_data[user_id] = {
        'last_request':None,
        'complaint_step':'source',
        'source':None,
        'place':None,
        'time':None,
        'persistence':None,
        'duration':None,
        'symptoms':[]
    }

@bot.message_handler(commands = ['complaint'])
def complaint_start(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {
            'last_request':'complaint',
            'complaint_step':'source',
            'source':None,
            'place':None,
            'time':None,
            'persistence':None,
            'duration':None,
            'symptoms':[]
        }
    user_data[user_id]['last_request'] = 'complaint'
    bot.send_message(user_id, "Выберите источник шума", reply_markup=keyboard_groups_sources)

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

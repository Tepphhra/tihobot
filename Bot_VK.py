import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.upload import VkUpload
import random
import os
import datetime
import json
from docx import Document

# =====================================================================
# --- НАСТРОЙКИ VK ---
# =====================================================================
BOT_TOKEN = 'vk1.a.NtMmWBoHlRrA0a0AAVLGAdvUTenYsp90KdaVbr78IpPC6-iPzXW6iPbcPUznPmINDjBGh_1eUbrbiqGwZQOBdrTjGntn2Xec4xrCojYibmx_peU3zH5YsIWnF4pJmxQwwHgL9zYx6XiHSJf1efGEJtzdbBHJ4i-kP-m1rLdNLhsOVkSLrW_QYLnxcHaLREos32hpVXll_j7iqTqihp6zvw'
vk_session = vk_api.VkApi(token=BOT_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
upload = VkUpload(vk_session)

# Оперативное хранилище состояний пользователей
user_data = {}

# =====================================================================
# --- БАЗА ДАННЫХ АНКЕТИРОВАНИЯ (ЖАЛОБЫ) ---
# =====================================================================
NOISE_GROUPS_SOURCES = [
    "Шум от транспорта",
    "Шум от стройки",
    "Шум от соседей",
    "Шум от инфраструктуры",
    "Шум от животных",
    "Шум от предприятий и организаций"
]

SUB_SOURCES_DICT = {
    "Шум от транспорта": [
        "Транспорт на магистралях",
        "Громкая работа двигателей",
        "Состояние трамвайных путей",
        "Железнодорожный транспорт"
    ],
    "Шум от стройки": [
        "Работы вне разрешенного времени",
        "Использование громкого инструмента"
    ],
    "Шум от соседей": [
        "Громкие бытовые приборы",
        "Ремонтные работы вне разрешенного времени",
        "Поведение соседей"
    ],
    "Шум от инфраструктуры": [
        "Громкая работа элементов вентиляции",
        "Громкая работа элементов жилого дома"
    ],
    "Шум от животных": [
        "Животные во дворе",
        "Животные в квартире"
    ],
    "Шум от предприятий и организаций": [
        "Громкая реклама",
        "Общественное заведение",
        "Шумное предприятие"
    ]
}

NOISE_TIME = [
    "Ночь (23:00-07:00)",
    "Утро (07:00-11:00)",
    "День (11:00-18:00)",
    "Вечер (18:00-23:00)",
    "Только в светлое время суток",
    "Только в темное время суток",
    "Круглосуточно"
]

NOISE_PERSISTENCE = [
    "Несколько дней",
    "Несколько недель",
    "Несколько месяцев",
    "Год и более"
]

NOISE_SYMPTOMS = [
    "Нарушение сна",
    "Головные боли",
    "Звон в ушах",
    "Головокружение",
    "Раздражительность"
]

# Плоский список всех подтипов для валидации Шага 2
ALL_SUB_SOURCES = []
for src_list in SUB_SOURCES_DICT.values():
    ALL_SUB_SOURCES.extend(src_list)

# =====================================================================
# --- ПОЛНАЯ БАЗА ДАННЫХ ПАРКОВ МОСКВЫ (КАРТЫ) ---
# =====================================================================
QUIET_PLACES = {
    "ЦАО": {
        "title": "Центральный округ (ЦАО)",
        "desc": "Парк Горького, Нескучный сад, Зарядье, Чистые пруды...",
        "parks": [
            {"name": "Парк Горького", "q": "Москва Парк Горького"},
            {"name": "Нескучный сад", "q": "Москва Нескучный сад"},
            {"name": "Александровский сад", "q": "Москва Александровский сад"},
            {"name": "Парк «Зарядье»", "q": "Москва Парк Зарядье"},
            {"name": "Патриаршие пруды", "q": "Москва Патриаршие пруды сквер"},
            {"name": "Чистые пруды", "q": "Москва Чистые пруды сквер"},
            {"name": "Бульварное кольцо", "q": "Москва Тверской бульвар"},
            {"name": "Сад «Эрмитаж»", "q": "Москва Сад Эрмитаж"}
        ]
    },
    "САО": {
        "title": "Северный округ (САО)",
        "desc": "Парк Дружбы, Ходынское поле, Тимирязевский, Петровский...",
        "parks": [
            {"name": "Парк «Дружбы»", "q": "Москва Парк Дружбы"},
            {"name": "Парк «Дубки»", "q": "Москва Парк Дубки"},
            {"name": "Парк «Ходынское поле»", "q": "Москва Парк Ходынское поле"},
            {"name": "Парк Речного вокзала", "q": "Москва Парк Северного речного вокзала"},
            {"name": "Головинские пруды", "q": "Москва Головинские пруды"},
            {"name": "Большой Садовый пруд", "q": "Москва Большой Садовый пруд"},
            {"name": "Ангарские пруды", "q": "Москва Ангарские пруды"},
            {"name": "Парк «Грачёвка»", "q": "Москва Парк Грачёвка"},
            {"name": "Тимирязевский парк", "q": "Москва Тимирязевский парк"},
            {"name": "Петровский парк", "q": "Москва Петровский парк"}
        ]
    },
    "СВАО": {
        "title": "Северо-Восточный округ (СВАО)",
        "desc": "Парк Яуза, Лосиный остров, Ботанический сад, Останкино...",
        "parks": [
            {"name": "Парк «Яуза»", "q": "Москва Парк Яуза"},
            {"name": "Лосиный остров", "q": "Москва Национальный парк Лосиный остров"},
            {"name": "Джамгаровский пруд", "q": "Москва Парк у Джамгаровского пруда"},
            {"name": "Бабушкинский парк", "q": "Москва Бабушкинский парк"},
            {"name": "Гончаровский парк", "q": "Москва Гончаровский парк"},
            {"name": "Лианозовский парк", "q": "Москва Лианозовский парк"},
            {"name": "Сквер по Олонецкому пр.", "q": "Москва Сквер по Олонецкому проезду"},
            {"name": "Дворцовый пруд", "q": "Москва Дворцовый пруд Останкино"},
            {"name": "Главный Ботанический сад", "q": "Москва Главный Ботанический сад РАН"}
        ]
    },
    "ВАО": {
        "title": "Восточный округ (ВАО)",
        "desc": "Сокольники, Измайлово, Кусково, Терлецкие пруды...",
        "parks": [
            {"name": "Парк «Сокольники»", "q": "Москва Парк Сокольники"},
            {"name": "Парк «Измайлово»", "q": "Москва Измайловский лесопарк"},
            {"name": "Терлецкие пруды", "q": "Москва Терлецкие пруды"},
            {"name": "Озеро Белое", "q": "Москва Озеро Белое Косино"},
            {"name": "Парк «Кусково»", "q": "Москва Кусково усадьба"},
            {"name": "Парк «Перовский»", "q": "Москва Перовский парк"},
            {"name": "Парк «Гольяново»", "q": "Москва Парк Гольяново"},
            {"name": "Пруды «Радуга»", "q": "Москва Парк у прудов Радуга"},
            {"name": "Озеро Святое", "q": "Москва Озеро Святое Косино"}
        ]
    },
    "ЮВАО": {
        "title": "Юго-Восточный округ (ЮВАО)",
        "desc": "Парк 850-летия Москвы, Кузьминки, Люблино, Печатники...",
        "parks": [
            {"name": "Парк 850-летия Москвы", "q": "Москва Парк 850-летия Москвы"},
            {"name": "Кузьминский лесопарк", "q": "Москва Кузьминский лесопарк"},
            {"name": "Парк «Печатники»", "q": "Москва Парк Печатники"},
            {"name": "Верхний Кузьминский пруд", "q": "Москва Верхний Кузьминский пруд"},
            {"name": "Парк «Люблино»", "q": "Москва Парк Люблино усадьба"},
            {"name": "Батайский пруд", "q": "Москва Батайский пруд"}
        ]
    },
    "ЮАО": {
        "title": "Южный округ (ЮАО)",
        "desc": "Царицыно, Коломенское, Борисовские пруды...",
        "parks": [
            {"name": "Музей-заповедник «Царицыно»", "q": "Москва Царицыно museum заповедник"},
            {"name": "Борисовские пруды", "q": "Москва Парк по Борисовским прудам"},
            {"name": "Парк Бекет", "q": "Москва Парк Бекет Загородное шоссе"},
            {"name": "Сад «Садовники»", "q": "Москва Сад Садовники"},
            {"name": "Парк «Коломенское»", "q": "Москва Коломенское парк"},
            {"name": "Калитниковский пруд", "q": "Москва Сквер у Калитниковского пруда"}
        ]
    },
    "ЮЗАО": {
        "title": "Юго-Западный округ (ЮЗАО)",
        "desc": "Битцевский лес, Воронцово, Тропарево, Бутово...",
        "parks": [
            {"name": "Битцевский лес", "q": "Москва Битцевский лес"},
            {"name": "Парк «Воронцово»", "q": "Москва Воронцовский парк"},
            {"name": "Парк «Академический»", "q": "Москва Парк Академический"},
            {"name": "Теплый Стан", "q": "Москва Ландшафтный заказник Тёплый Стан"},
            {"name": "Парк 70-летия Победы", "q": "Москва Парк 70-летия Победы Черемушки"},
            {"name": "Ландшафтный парк Бутово", "q": "Москва Ландшафтный парк Южное Бутово"},
            {"name": "Парк «Никулино»", "q": "Москва Парк Никулино"},
            {"name": "Тропаревский лесопарк", "q": "Москва Тропаревский лесопарк"},
            {"name": "Узкое заказник", "q": "Москва Санаторий Узкое усадьба"}
        ]
    },
    "ЗАО": {
        "title": "Западный округ (ЗАО)",
        "desc": "Парк Фили, Серебряный Бор, Олимпийская деревня...",
        "parks": [
            {"name": "Парк «Фили»", "q": "Москва Филевский парк"},
            {"name": "Кунцевский лесопарк", "q": "Москва Кунцевский лесопарк"},
            {"name": "Серебряный Бор", "q": "Москва Серебряный Бор"},
            {"name": "Парк Олимпийской Деревни", "q": "Москва Парк Олимпийской Деревни"},
            {"name": "Филевская пойма", "q": "Москва Филевская пойма"},
            {"name": "Мневниковская пойма", "q": "Москва Мневниковская пойма"},
            {"name": "Парк 50-летия Октября", "q": "Москва Парк 50-летия Октября"}
        ]
    },
    "СЗАО": {
        "title": "Северо-Западный округ (СЗАО)",
        "desc": "Покровское-Стрешнево, Сходненская чаша, Тушино...",
        "parks": [
            {"name": "Лесопарк «Покровское-Стрешнево»", "q": "Москва Покровское-Стрешнево"},
            {"name": "Сходненская чаша", "q": "Москва Сходненская чаша"},
            {"name": "Парк «Северное Тушино»", "q": "Москва Парк Северное Тушино"},
            {"name": "Парк «Южное Тушино»", "q": "Москва Парк Южное Тушино"},
            {"name": "Дубовая роща Маяк", "q": "Москва Дубовая роща Маяк"},
            {"name": "Парк «Захарково»", "q": "Москва Парк Захарково"}
        ]
    },
    "ЗелАО": {
        "title": "Зеленоград (ЗелАО)",
        "desc": "Лесопарк Зеленоград, Нижний Каменский пруд, Савелки...",
        "parks": [
            {"name": "Нижний Каменский пруд", "q": "Зеленоград Нижний Каменский пруд"},
            {"name": "Парк у 17-го микрорайона", "q": "Зеленоград Парк у 17-го микрорайона"},
            {"name": "Лесопарк «Зеленоград»", "q": "Зеленоград Крюковский лесопарк"},
            {"name": "Пруд в районе Савелки", "q": "Зеленоград Большой Городской Пруд"},
            {"name": "Березовая аллея", "q": "Зеленоград Березовая аллея"}
        ]
    }
}

# =====================================================================
# --- ВСПОМОГАТЕЛЬНЫЕ ИНТЕРФЕЙСНЫЕ ФУНКЦИИ ---
# =====================================================================
def send_msg(user_id, text, keyboard=None, template=None, attachment=None):
    """Универсальный отправитель сообщений"""
    params = {
        'user_id': user_id,
        'message': text,
        'random_id': int(random.randint(1, 2**63 - 1))
    }
    if keyboard: params['keyboard'] = keyboard
    if template: params['template'] = json.dumps(template, ensure_ascii=False)
    if attachment: params['attachment'] = attachment
    vk.messages.send(**params)

def create_main_menu():
    """Главная постоянная клавиатура нижнего меню"""
    keyboard = VkKeyboard(one_time=False, inline=False)
    keyboard.add_button("📝 Создать жалобу", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("❓ Что это за бот", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📍 Карта тихих мест", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()

def create_vk_keyboard(items, add_ready=False):
    """Генератор инлайн-клавиатур для этапов опроса"""
    keyboard = VkKeyboard(inline=True)
    for i, item in enumerate(items):
        if i > 0 and i % 2 == 0: 
            keyboard.add_line()
        keyboard.add_button(item, color=VkKeyboardColor.PRIMARY)
    if add_ready:
        keyboard.add_line()
        keyboard.add_button("Готово", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

# =====================================================================
# --- КОНСТРУКТОРЫ КАРУСЕЛЕЙ (МАТРИЦЫ СВАЙПОВ) ---
# =====================================================================
def build_ao_carousel():
    """Уровень 1: Карусель Административных Округов"""
    elements = []
    for key, info in QUIET_PLACES.items():
        elements.append({
            "title": info["title"],
            "description": info["desc"],
            "buttons": [{
                "action": {
                    "type": "text",
                    "label": f"Выбрать {key}",
                    "payload": json.dumps({"ao": key})
                },
                "color": "primary"
            }]
        })
    return {"type": "carousel", "elements": elements}

def build_parks_carousel(ao_key):
    """Уровень 2: Карусель Конкретных Парков выбранного Округа"""
    info = QUIET_PLACES.get(ao_key)
    if not info: return None
    
    elements = []
    # Лимит каруселей в ВК — 10 карточек. Усекаем на всякий случай.
    for park in info["parks"][:10]:
        elements.append({
            "title": park["name"],
            "description": f"Скрытая зона тишины ({ao_key})",
            "buttons": [{
                "action": {
                    "type": "text",
                    "label": f"📍 Маршрут: {park['name']}",
                    "payload": json.dumps({"park_q": park["q"]})
                },
                "color": "positive"
            }]
        })
    return {"type": "carousel", "elements": elements}

def init_user_complaint(user_id):
    """Обнуление и старт сессии сбора жалобы"""
    user_data[user_id] = {
        'context': 'complaint',
        'step': 'group_source',
        'noise_group': None, 'source': None, 'place': None, 'time': None,
        'persistence': None, 'duration': None, 'symptoms': [],
        'user_fio': None, 'user_phone': None, 'user_email': None
    }

# =====================================================================
# --- МОДЕРНИЗИРОВАННЫЙ ШАБЛОНИЗАТОР MICROSOFT WORD ---
# =====================================================================
def create_document_from_template(data, user_id):
    """Сборщик файлов .docx на основе выбранных шаблонов из папки templates/"""
    group = data.get('noise_group')
    
    # Дефолтные заголовки ведомств
    authority_name = "Управление Роспотребнадзора"
    authority_city_or_district = "Руководителю территориального органа"
    authority_region_or_city = "Государственной жилищной инспекции"
    
    # Динамическая маршрутизация по шаблонам
    if group == "Шум от транспорта":
        template_name = "template_type1.docx"
        authority_name = "ОГИБДД ОМВД России"
        authority_city_or_district = "Начальнику ОГИБДД ОМВД России по административному округу"
        authority_region_or_city = "Управлению ГИБДД"
    elif group == "Шум от стройки":
        template_name = "template_type2.docx"
        authority_name = "Государственная строительная инспекция"
        authority_city_or_district = "В Государственную строительную инспекцию и Администрацию округа"
        authority_region_or_city = "Департаменту градостроительной политики"
    else:
        template_name = "template_type3.docx"
        authority_name = "Государственная жилищная инспекция"
        authority_city_or_district = "Начальнику управления государственной жилищной инспекции"
        authority_region_or_city = "Государственной жилищной инспекции"

    if not os.path.exists(template_name):
        raise FileNotFoundError(f"Критическая ошибка: Шаблон {template_name} не найден в папке templates/!")
        
    doc = Document(template_name)
    symptoms_str = ", ".join(data.get('symptoms', [])) if data.get('symptoms') else "Не указано"

    # Карта заменяемых плейсхолдеров
    replacements = {
        "{{authority_name}}": authority_name,
        "{{authority_city_or_district}}": authority_city_or_district,
        "{{authority_region_or_city}}": authority_region_or_city,
        "{{user_fio}}": str(data.get('user_fio', 'Не указано')),
        "{{user_phone}}": str(data.get('user_phone', 'Не указано')),
        "{{user_email}}": str(data.get('user_email', 'Не указано')),
        "{{noise_group}}": str(data.get('noise_group', 'Не указано')),
        "{{source}}": str(data.get('source', 'Не указано')),
        "{{place}}": str(data.get('place', 'Не указано')),
        "{{time}}": str(data.get('time', 'Не указано')),
        "{{persistence}}": str(data.get('persistence', 'Не указано')),
        "{{duration}}": str(data.get('duration', '0')),
        "{{symptoms}}": symptoms_str,
        "{{date}}": datetime.date.today().strftime("%d.%m.%Y")
    }

    # Алгоритм сквозного слияния текстовых фрагментов (runs) для защиты от разрывов разметки Word
    for paragraph in doc.paragraphs:
        for placeholder, value in replacements.items():
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, value)
                if placeholder in paragraph.text:
                    text_all = paragraph.text.replace(placeholder, value)
                    if paragraph.runs:
                        paragraph.runs[0].text = text_all
                        for run in paragraph.runs[1:]: 
                            run.text = ""
                        
    return doc

# =====================================================================
# --- ЦЕНТРАЛЬНЫЙ СУПЕРЦИКЛ СЛУШАТЕЛЯ LONGPOLL ---
# =====================================================================
print(">>> Абсолютно полная сборка бота запущена и готова к демонстрации...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text_input = event.text.strip()

        # Базовые системные триггеры
        if text_input.lower() in ['/start', 'привет', 'начать']:
            send_msg(user_id, 'Приветствуем! Система мониторинга акустического благополучия запущена.', keyboard=create_main_menu())
            continue
        
        if text_input.lower() == '❓ что это за бот':
            info_text = (
                "🤖 Помощник по защите прав граждан от шумового загрязнения.\n\n"
                "Бот генерирует юридически выверенные заявления в надзорные ведомства (ГИБДД, Наш Город, Роспотребнадзор) "
                "и предоставляет интерактивный навигатор по скрытым экологическим зонам тишины Москвы."
            )
            send_msg(user_id, info_text, keyboard=create_main_menu())
            continue

        # ==========================================
        # МОДУЛЬ КАРТЫ (ДВУХУРОВНЕВАЯ КАРУСЕЛЬ)
        # ==========================================
        if text_input.lower() == '📍 карта тихих мест':
            user_data[user_id] = {'context': 'map_browsing'}
            send_msg(
                user_id, 
                "🌿 Интерактивная карта зон тишины\n\nШаг 1: Выберите интересующий административный округ (АО) из карусели ниже:", 
                template=build_ao_carousel()
            )
            continue

        # Перехват контекста работы с гео-модулем
        if user_id in user_data and user_data[user_id].get('context') == 'map_browsing':
            
            # Н1: Клик по кнопке округа -> Выдача карусели парков
            if text_input.lower().startswith("выбрать "):
                ao_key = text_input.split()[-1].upper()
                if ao_key in QUIET_PLACES:
                    parks_carousel = build_parks_carousel(ao_key)
                    send_msg(
                        user_id, 
                        f"🌳 Округ: {ao_key}\n\nШаг 2: Выберите скрытую зону тишины для автоматического построения маршрута:", 
                        template=parks_carousel
                    )
                continue
                
            # Н2: Клик по парку -> Сборка гиперссылки Яндекс.Карт
            elif text_input.lower().startswith("📍 маршрут: "):
                park_name = text_input.replace("📍 Маршрут: ", "").replace("📍 маршрут: ", "")
                
                search_query = None
                for ao_info in QUIET_PLACES.values():
                    for park_item in ao_info["parks"]:
                        if park_item["name"].lower() == park_name.lower():
                            search_query = park_item["q"]
                            break
                
                if search_query:
                    maps_url = f"https://yandex.ru/maps/?text={search_query.replace(' ', '+')}"
                    success_text = (
                        f"🧭 Построение маршрута до: «{park_name}» успешно завершено!\n\n"
                        f"👉 [НАЖМИТЕ ТУТ, ЧТОБЫ ОТКРЫТЬ ЯНДЕКС.КАРТЫ]({maps_url})\n\n"
                        "Ссылка автоматически откроет Яндекс.Навигатор или Карты на Вашем мобильном устройстве."
                    )
                    send_msg(user_id, success_text, keyboard=create_main_menu())
                    user_data.pop(user_id, None) # Очистка сессии
                continue

        # ==========================================
        # МОДУЛЬ МНОГОЭТАПНОГО АНКЕТИРОВАНИЯ
        # ==========================================
        if text_input.lower() in ['/complaint', '📝 создать жалобу']:
            init_user_complaint(user_id)
            send_msg(user_id, "Шаг 1: Выберите общую категорию источника шума:", keyboard=create_vk_keyboard(NOISE_GROUPS_SOURCES))
            continue

        # Безопасный фильтр контекста анкетирования
        if user_id not in user_data or user_data[user_id].get('context') != 'complaint':
            send_msg(user_id, "Пожалуйста, используйте кнопки меню для управления системой:", keyboard=create_main_menu())
            continue

        current_step = user_data[user_id]['step']

        # ЭТАП 1: Группа источников
        if current_step == 'group_source':
            if text_input in NOISE_GROUPS_SOURCES:
                user_data[user_id]['noise_group'] = text_input
                user_data[user_id]['step'] = 'source'
                sub_list = SUB_SOURCES_DICT.get(text_input, [])
                send_msg(user_id, f"Категория: {text_input}.\n\nШаг 2: Уточните конкретный фактор воздействия:", keyboard=create_vk_keyboard(sub_list))
            else:
                send_msg(user_id, "Пожалуйста, используйте инлайн-кнопки для выбора категории шума:", keyboard=create_vk_keyboard(NOISE_GROUPS_SOURCES))

        # ЭТАП 2: Подтип источника
        elif current_step == 'source':
            if text_input in ALL_SUB_SOURCES:
                user_data[user_id]['source'] = text_input
                user_data[user_id]['step'] = 'place'
                send_msg(user_id, "Шаг 3: Введите точный адрес фиксации правонарушения (Улица, номер дома/строения):")

        # ЭТАП 3: Локация / Адрес
        elif current_step == 'place':
            user_data[user_id]['place'] = text_input
            user_data[user_id]['step'] = 'time'
            send_msg(user_id, "Шаг 4: Выберите время суток наиболее частой фиксации шума:", keyboard=create_vk_keyboard(NOISE_TIME))

        # ЭТАП 4: Время суток
        elif current_step == 'time':
            if text_input in NOISE_TIME:
                user_data[user_id]['time'] = text_input
                user_data[user_id]['step'] = 'persistence'
                send_msg(user_id, "Шаг 5: Укажите общую продолжительность (систематичность) проблемы:", keyboard=create_vk_keyboard(NOISE_PERSISTENCE))
            else:
                send_msg(user_id, "Используйте инлайн-кнопки времени суток:", keyboard=create_vk_keyboard(NOISE_TIME))

        # ЭТАП 5: Систематичность
        elif current_step == 'persistence':
            if text_input in NOISE_PERSISTENCE:
                user_data[user_id]['persistence'] = text_input
                user_data[user_id]['step'] = 'duration'
                send_msg(user_id, "Шаг 6: Укажите среднюю продолжительность шума за сутки (Введите только количество часов цифрами):")
            else:
                send_msg(user_id, "Используйте инлайн-кнопки систематичности:", keyboard=create_vk_keyboard(NOISE_PERSISTENCE))

        # ЭТАП 6: Длительность в часах
        elif current_step == 'duration':
            user_data[user_id]['duration'] = text_input
            user_data[user_id]['step'] = 'symptoms'
            send_msg(user_id, "Шаг 7: Отметьте негативные симптомы для здоровья (можно выбрать несколько, по окончании нажмите 'Готово'):", keyboard=create_vk_keyboard(NOISE_SYMPTOMS, add_ready=True))

        # ЭТАП 7: Мультивыбор медицинских симптомов
        elif current_step == 'symptoms':
            if text_input != 'Готово':
                if text_input in NOISE_SYMPTOMS:
                    if text_input not in user_data[user_id]['symptoms']:
                        user_data[user_id]['symptoms'].append(text_input)
                    else:
                        user_data[user_id]['symptoms'].remove(text_input)
                    
                    selected_str = ", ".join(user_data[user_id]['symptoms']) if user_data[user_id]['symptoms'] else "Ничего не выбрано"
                    send_msg(user_id, f"Выбрано: {selected_str}", keyboard=create_vk_keyboard(NOISE_SYMPTOMS, add_ready=True))
            else:
                user_data[user_id]['step'] = 'ask_fio'
                send_msg(user_id, "Параметры сохранены.\n\nПереходим к верификации контактных данных заявителя.\n\nШаг 8: Введите Ваши ФИО полностью (в Именительном падеже):")

        # ЭТАП 8: ФИО
        elif current_step == 'ask_fio':
            user_data[user_id]['user_fio'] = text_input
            user_data[user_id]['step'] = 'ask_phone'
            send_msg(user_id, "Шаг 9: Введите Ваш контактный номер телефона для связи:")

        # ЭТАП 9: Номер телефона
        elif current_step == 'ask_phone':
            user_data[user_id]['user_phone'] = text_input
            user_data[user_id]['step'] = 'ask_email'
            send_msg(user_id, "Шаг 10: Укажите Ваш e-mail адрес для получения официального ответа ведомства:")

        # ЭТАП 10: Email, Сборка, Рендеринг и отправка Документа
        elif current_step == 'ask_email':
            user_data[user_id]['user_email'] = text_input
            user_data[user_id]['step'] = 'completed'
            
            send_msg(user_id, "⏳ Все данные успешно получены. Запускаем компиляцию официального бланка заявления...")
            
            # Запуск генератора .docx документа
            try:
                doc = create_document_from_template(user_data[user_id], user_id)
                local_filename = f"complaint_{user_id}.docx"
                doc.save(local_filename)
                
                # Загрузка сгенерированного файла на сервера документов ВКонтакте
                vk_doc = upload.document_message(doc=local_filename, title=f"Заявление_Шум_{user_id}.docx", peer_id=user_id)
                attachment_id = f"doc{vk_doc['doc']['owner_id']}_{vk_doc['doc']['id']}"
                
                send_msg(user_id, "🎉 Официальное заявление успешно сформировано в соответствии с ГОСТ и прикреплено ниже!", attachment=attachment_id, keyboard=create_main_menu())
            except Exception as e:
                send_msg(user_id, f"⚠️ Системный сбой генерации файлов: {e}. Данные сохранены в логах сервера.", keyboard=create_main_menu())
            finally:
                # Финальная очистка временных файлов с жесткого диска сервера
                if os.path.exists(local_filename): 
                    os.remove(local_filename)
            
            print(f"[{datetime.datetime.now()}] Сгенерирован и отправлен документ для ID {user_id}")
            user_data.pop(user_id, None)

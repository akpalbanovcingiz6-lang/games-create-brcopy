import telebot
import time
import ftplib
import requests
import io
import json
import os
import threading
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
TOKEN = "токен сюжыыыы"
ADMIN_ID = айди админа тг 
ADMIN_USERNAME = "@ЮЗ дамина"
HOST_USER_ID = "хост айди"
GITHUB_TOKEN = "токен Ги зби"
GITHUB_REPO = "репу"
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

bot = telebot.TeleBot(TOKEN)
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Главное меню"),
    telebot.types.BotCommand("/help", "Помощь"),
    telebot.types.BotCommand("/admin", "Панель администратора")
])
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

original_send = bot.send_message
def safe_send(*args, **kwargs):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    try:
        return original_send(*args, **kwargs)
    except Exception as e:
        print(f"Игнор ошибки отправки (юзер заблокировал бота): {e}")
bot.send_message = safe_send
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

user_data = {}
promocodes = {}
promo_lock = threading.Lock()
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

def load_data():
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    global user_data, promocodes
    try:
        with open("bot_data.json", "r") as f:
            data = json.load(f)
            user_data = {int(k): v for k, v in data.get("users", {}).items()}
            promocodes = data.get("promos", {})
    except FileNotFoundError:
        pass
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

def save_data():
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    try:
        with open("bot_data.json", "w") as f:
            json.dump({"users": user_data, "promos": promocodes}, f)
    except Exception:
        pass
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

def auto_save():
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    while True:
        time.sleep(10)
        save_data()
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

threading.Thread(target=auto_save, daemon=True).start()
load_data()
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

def get_user(uid):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    if uid not in user_data:
        user_data[uid] = {}
    return user_data[uid]
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

def send_with_banner(chat_id, text, markup=None):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    try:
        with open('banner.jpg', 'rb') as photo:
            if markup:
                bot.send_photo(chat_id, photo, caption=text, reply_markup=markup, parse_mode='HTML')
            else:
                bot.send_photo(chat_id, photo, caption=text, parse_mode='HTML')
    except FileNotFoundError:
        if markup:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(chat_id, text, parse_mode='HTML')
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(commands=['start', 'help'])
def start(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    cid = message.chat.id
    u = get_user(cid)
    u['username'] = message.from_user.username
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🛠 Создать проект", callback_data="menu_create_project"),
        InlineKeyboardButton("🛒 Магазин", callback_data="systems_store")
    )
    markup.row(
        InlineKeyboardButton("⚙️ Pawn Компилятор", callback_data="pawn_compiler"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    markup.row(
        InlineKeyboardButton("🎰 Слоты", callback_data="roll_dice"),
        InlineKeyboardButton("🪙 Монетка", callback_data="coin_flip"),
        InlineKeyboardButton("🎟 Промо", callback_data="enter_promo")
    )
    markup.row(
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help_menu"),
        InlineKeyboardButton("👨‍💻 Админ", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    )
    
    text = (
        "⚡️ <b>СИСТЕМА АВТО-РАЗВЕРТЫВАНИЯ СЕРВЕРОВ</b> ⚡️\n\n"
        "🚀 <i>Мы соберем, настроим и запустим Ваш проект за пару минут в автоматическом режиме. Без лишних нервов и консолей.</i>\n\n"
        "👇 <b>Выберите действие ниже:</b>"
    )
    send_with_banner(cid, text, markup)
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    if message.chat.id == ADMIN_ID or message.from_user.username == ADMIN_USERNAME.strip('@'):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
                   InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"))
        markup.add(InlineKeyboardButton("🎟 Создать промокод", callback_data="admin_create_promo"))
        markup.add(InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users"))
        markup.add(InlineKeyboardButton("🎁 Выдать товар (Юзернейм)", callback_data="admin_give_item"))
        bot.send_message(message.chat.id, "👑 <b>Секретная панель управления</b>", reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде.")
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    cid = call.message.chat.id
    u = get_user(cid)
    
    if call.data == "back_to_main":
        try: bot.delete_message(cid, call.message.message_id)
        except: pass
        start(call.message)
        return

    elif call.data == "menu_create_project":
        sm = InlineKeyboardMarkup()
        sm.add(InlineKeyboardButton("⭐️ Купить за звезды", callback_data="pay_stars"))
        sm.add(InlineKeyboardButton("💳 Оплатить картой", callback_data="pay_card"))
        sm.add(InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_main"))
        try:
            bot.edit_message_caption("🛠 <b>Создание нового проекта</b>\n\nВыберите способ оплаты за автоматическую развертку сервера:", cid, call.message.message_id, reply_markup=sm, parse_mode="HTML")
        except:
            bot.send_message(cid, "🛠 <b>Создание нового проекта</b>\n\nВыберите способ оплаты за автоматическую развертку сервера:", reply_markup=sm, parse_mode="HTML")
        return

    elif call.data == "start_setup":
        if u.get('can_setup'):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("✅ Я добавил доступ", callback_data="host_added"))
            send_with_banner(cid, f"Добавьте этот ID в соавторы на хостинге:\n<code>{HOST_USER_ID}</code>\n\nЗатем нажмите кнопку:", markup)
        return

    elif call.data in ["help", "help_menu"]:
        text = (
            "💡 <b>Справка по установке (Maze Host)</b>\n\n"
            "Мы рекомендуем использовать <b>Maze Host</b>!\n\n"
            "Где найти данные в панели Maze Host:\n"
            "📡 <b>IP сервера:</b> На главной странице.\n"
            "📁 <b>FTP данные:</b> В разделе <b>«FTP»</b> (IP, Логин, Пароль).\n"
            "🗄 <b>База Данных:</b> В разделе <b>«Базы данных»</b> (Логин, Пароль, Имя базы).\n"
            "🔑 <b>Доступ:</b> В разделе <b>«Соавторы»</b> добавьте наш ID.\n\n"
            "<b>Команды:</b> /start, /help, /admin"
        )
        bot.send_message(cid, text, parse_mode="HTML")
        try: bot.answer_callback_query(call.id)
        except: pass
        return
    
    elif call.data == "pay_stars":
        base_price = 200
        disc = u.get('discount', 0)
        final_price = int(base_price * (1 - disc / 100))
        text = f"⭐️ <b>К оплате: {final_price} Звезд</b>\n\n🎁 Отправьте {final_price} звезд подарками на аккаунт @whygoldzy (например, 2 подарка по 100 звезд).\n\n📸 <i>А затем отправьте сюда скриншот отправки подарков.</i>"
        send_with_banner(cid, text)
        u['state'] = "waiting_stars_receipt"
        
    elif call.data == "pay_card":
        base_price = 200
        disc = u.get('discount', 0)
        final_price = int(base_price * (1 - disc / 100))
        text = f"💸 <b>К оплате: {final_price} RUB</b> <i>(Скидка {disc}%)</i>\n\n💳 <code>+79519282286</code> (Сбер)\n\n📸 <i>Отправьте сюда фотографию чека.</i>" if disc > 0 else f"💸 <b>К оплате: {base_price} RUB</b>\n\n💳 <code>+79519282286</code> (Сбер)\n\n📸 <i>Отправьте сюда фотографию чека.</i>"
        send_with_banner(cid, text)
        u['state'] = "waiting_receipt"
        
    elif call.data == "enter_promo":
        bot.send_message(cid, "🎟 <b>Введите промокод:</b>\n<i>(на скидку или бесплатный сервер)</i>", parse_mode="HTML")
        u['state'] = "waiting_promo"
        
    elif call.data == "profile":
        status = "🟢 Готов к установке" if u.get('can_setup') else "🔴 Ожидает оплаты"
        disc = u.get('discount', 0)
        ddos = u.get('ddos_prot', False)
        ddos_status = "Включена 🛡" if ddos else "Выключена ⚠️"
        
        last_roll = u.get('last_dice_roll', 0)
        hours_left = 24 - (time.time() - last_roll)/3600
        if hours_left < 0: hours_left = 0
        
        text = f"👤 <b>Ваш цифровой профиль</b>\n\n🆔 ID: <code>{cid}</code>\n🔑 Статус: <b>{status}</b>\n🎁 Активная скидка: <b>{disc}%</b>\n🎰 Слоты: через {int(hours_left)} ч.\n🛡 Защита от DDoS: <b>{ddos_status}</b>\n\n<i>Оплатите сервер или введите промокод для изменения статуса.</i>"
        
        markup = InlineKeyboardMarkup()
        if u.get('can_setup'):
            markup.add(InlineKeyboardButton("⚙️ Перейти к настройке", callback_data="start_setup"))
        markup.add(InlineKeyboardButton("🔄 Переключить DDoS защиту", callback_data="toggle_ddos"))
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        
        bot.send_message(cid, text, reply_markup=markup, parse_mode="HTML")
        try: bot.answer_callback_query(call.id)
        except: pass

    elif call.data == "toggle_ddos":
        u['ddos_prot'] = not u.get('ddos_prot', False)
        bot.answer_callback_query(call.id, "🔄 Статус защиты изменен на сервере!", show_alert=False)
        call.data = "profile"
        callback_handler(call)
        return

    elif call.data in ["play_slots", "play_bowling", "play_darts"]:
        em = "🎰" if call.data == "play_slots" else ("🎳" if call.data == "play_bowling" else "🎯")
        bot.send_dice(cid, emoji=em)
        try: bot.answer_callback_query(call.id)
        except: pass
        return

    elif call.data == "coin_flip":
        res = random.choice(["🦅 Орел", "🪙 Решка"])
        bot.send_message(cid, f"🪙 Монетка подброшена...\n\nВыпало: <b>{res}</b>!", parse_mode="HTML")
        try: bot.answer_callback_query(call.id)
        except: pass
        return

    elif call.data == "roll_dice":
        current_time = time.time()
        last_roll = u.get('last_dice_roll', 0)
        if current_time - last_roll < 86400:
            bot.answer_callback_query(call.id, "🚫 Крутить слоты можно только раз в день! Приходи завтра.", show_alert=True)
            return
            
        u['last_dice_roll'] = current_time
        bot.send_message(cid, "🎰 <b>Крутим слоты...</b>\nВыбей три одинаковых символа (бары, виноград, лимоны или семерки) и получи бесплатный сервер!", parse_mode="HTML")
        msg = bot.send_dice(cid, emoji="🎰")
        
        def check_slots(message_obj, chat_id, user_obj):
            # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
            time.sleep(4)
            val = message_obj.dice.value
            if val in [1, 22, 43, 64]:
                user_obj['can_setup'] = True
                bot.send_message(chat_id, "🎉 <b>ДЖЕКПОТ! ТРИ В РЯД!</b>\nВы получили бесплатную сборку сервера.\nЗайдите в 'Мой профиль' или переходите к настройке.", parse_mode="HTML")
            else:
                bot.send_message(chat_id, "😢 <b>Не повезло.</b>\nКомбинация не совпала. Жду тебя завтра!", parse_mode="HTML")
            # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
                
        threading.Thread(target=check_slots, args=(msg, cid, u)).start()
        try: bot.answer_callback_query(call.id)
        except: pass

    elif call.data == "systems_store":
        sm = InlineKeyboardMarkup()
        sm.add(InlineKeyboardButton("💎 Система VIP — 100₽", callback_data="buy_sys_vip"))
        sm.add(InlineKeyboardButton("🚘 Система Гаражей — 150₽", callback_data="buy_sys_garage"))
        sm.add(InlineKeyboardButton("📦 Система Кейсов — 200₽", callback_data="buy_sys_cases"))
        sm.add(InlineKeyboardButton("🔑 Авторизация (Лаунчер) — 250₽", callback_data="buy_sys_login"))
        sm.add(InlineKeyboardButton("🎟 Промокоды — 100₽", callback_data="buy_sys_promo"))
        sm.add(InlineKeyboardButton("👑 Админ-Панель — 300₽", callback_data="buy_sys_admin"))
        bot.send_message(cid, "🛒 <b>Магазин Pawn-систем</b>\n\nЗдесь лежат готовые скрипты. Выбирай нужную:", reply_markup=sm, parse_mode="HTML")
        try: bot.answer_callback_query(call.id)
        except: pass

    elif call.data == "pawn_compiler":
        sm = InlineKeyboardMarkup()
        sm.add(InlineKeyboardButton("⭐️ Купить за 25 звезд", callback_data="pay_pawn_stars"))
        sm.add(InlineKeyboardButton("💳 Оплатить картой (25₽)", callback_data="pay_pawn_card"))
        sm.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        bot.send_message(cid, "⚙️ <b>Облачный Pawn Компилятор</b>\n\nСтоимость одной компиляции: <b>25 рублей</b> или <b>25 звезд</b>.\nВыберите способ оплаты:", reply_markup=sm, parse_mode="HTML")
        try: bot.answer_callback_query(call.id)
        except: pass

    elif call.data == "pay_pawn_stars":
        bot.send_invoice(
            cid, title="⚙️ Компиляция .pwn", description="Разовая облачная компиляция скрипта",
            invoice_payload="pawn_payment", provider_token="", currency="XTR",
            prices=[LabeledPrice("Компиляция", 25)]
        )
        
    elif call.data == "pay_pawn_card":
        text = "💸 <b>Переведите 25 рублей на карту:</b>\n\n💳 <code>+79519282286</code> (Сбер)\n\n📸 <i>А затем отправьте сюда фотографию чека.</i>"
        send_with_banner(cid, text)
        u['state'] = "waiting_pawn_receipt"
        
    elif call.data.startswith("buy_sys_"):
        sys_name = call.data.replace("buy_sys_", "")
        prices = {"vip": 100, "garage": 150, "cases": 200, "login": 250, "promo": 100, "admin": 300}
        names = {"vip": "Система VIP", "garage": "Система Гаражей", "cases": "Система Кейсов", "login": "Авторизация (Лаунчер)", "promo": "Промокоды", "admin": "Админ-Панель"}
        prompts = {
            "vip": "gta_samp_vip_player_luxury_car_mansion_neon_style",
            "garage": "gta_samp_underground_garage_with_tuned_cars",
            "cases": "gta_samp_glowing_lootbox_case_with_weapons_and_money",
            "login": "gta_samp_launcher_login_screen_hacker_style",
            "promo": "gta_samp_promocode_ticket_with_money_and_stars",
            "admin": "gta_samp_server_admin_panel_dashboard_hacker_screen"
        }
        
        if sys_name in prices:
            price = prices[sys_name]
            name = names[sys_name]
            ai_prompt = prompts.get(sys_name, "gta_samp_roleplay_server_gameplay")
            
            sm = InlineKeyboardMarkup()
            sm.add(InlineKeyboardButton("💳 Оплатить картой", callback_data=f"pay_script_{sys_name}"))
            sm.add(InlineKeyboardButton("🔙 Назад", callback_data="systems_store"))
            
            text = f"🛒 <b>Покупка скрипта: {name}</b>\n\nСтоимость: <b>{price}₽</b>\n\n<i>Оплатите картой, и бот сразу после подтверждения чека пришлет вам готовый .pwn файл.</i>"
            
            img_url = f"https://image.pollinations.ai/prompt/{ai_prompt}?width=800&height=400&nologo=true"
            bot.send_photo(cid, img_url, caption=text, reply_markup=sm, parse_mode='HTML')
            
            try: bot.answer_callback_query(call.id)
            except: pass

    elif call.data.startswith("pay_script_"):
        sys_name = call.data.replace("pay_script_", "")
        u['state'] = f"waiting_script_receipt_{sys_name}"
        text = f"💸 <b>Переведите оплату на карту:</b>\n\n💳 <code>+79519282286</code> (Сбер)\n\n📸 <i>А затем отправьте сюда фотографию чека.</i>"
        bot.send_message(cid, text, parse_mode='HTML')
        try: bot.answer_callback_query(call.id)
        except: pass

    elif call.data == "admin_stats":
        bot.send_message(cid, f"📊 Статистика:\nПользователей: {len(user_data)}\nАктивных промокодов: {len(promocodes)}")

    elif call.data == "admin_broadcast":
        bot.send_message(cid, "📢 <b>Введите текст для рассылки всем пользователям:</b>\n<i>(Для отмены отправьте /cancel)</i>", parse_mode="HTML")
        u['state'] = "admin_waiting_broadcast"
        
    elif call.data == "admin_create_promo":
        bot.send_message(cid, "🛠 <b>Создание промокода</b>\n\nФормат (бесплатный сервер):\n<code>ПРОМОКОД КОЛ-ВО</code>\n\nФормат (на скидку %):\n<code>ПРОМОКОД КОЛ-ВО СКИДКА</code>\n\nПример: <code>SALE50 10 50</code>", parse_mode="HTML")
        u['state'] = "admin_waiting_promo_create"
        
    elif call.data == "admin_users":
        bot.send_message(cid, f"👥 Всего пользователей в базе: {len(user_data)}")
        
    elif call.data == "admin_give_item":
        bot.send_message(cid, "Введите юзернейм или ID пользователя, которому нужно выдать доступ:")
        u['state'] = "admin_waiting_give"

    elif call.data.startswith("approve_"):
        user_id = int(call.data.split("_")[1])
        get_user(user_id)['can_setup'] = True
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Я добавил доступ", callback_data="host_added"))
        
        text = f"✅ <b>Ваша оплата успешно подтверждена!</b>\n\nДобавьте этот ID/логин в соавторы на хостинге:\n<code>{HOST_USER_ID}</code>\n\nКак добавите, нажмите кнопку:"
        send_with_banner(user_id, text, markup)
        bot.send_message(cid, "✅ Вы подтвердили оплату клиента.")
        
    elif call.data.startswith("reject_"):
        user_id = int(call.data.split("_")[1])
        bot.send_message(user_id, "❌ <b>Оплата отклонена.</b> Ваш чек не прошел проверку.", parse_mode="HTML")
        bot.send_message(cid, "❌ Вы отклонили чек.")
        
    elif call.data.startswith("apprpawn_"):
        user_id = int(call.data.split("_")[1])
        get_user(user_id)['state'] = "waiting_pwn_file"
        bot.send_message(user_id, "✅ <b>Оплата компиляции подтверждена!</b>\n\nОтправьте мне ваш файл <code>.pwn</code>", parse_mode="HTML")
        bot.send_message(cid, "✅ Вы разрешили пользователю компиляцию.")
        
    elif call.data.startswith("rejpawn_"):
        user_id = int(call.data.split("_")[1])
        bot.send_message(user_id, "❌ <b>Оплата отклонена.</b> Ваш чек не прошел проверку.", parse_mode="HTML")
        bot.send_message(cid, "❌ Вы отклонили чек.")

    elif call.data.startswith("apprscript_"):
        parts = call.data.split("_")
        user_id = int(parts[1])
        sys_name = parts[2]
        
        file_path = f"{sys_name}.pwn"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                bot.send_document(user_id, f, caption="✅ <b>Оплата подтверждена!</b> Держи свой скрипт.", parse_mode="HTML")
            bot.send_message(cid, f"✅ Вы выдали скрипт {sys_name} пользователю.")
        else:
            bot.send_message(cid, f"❌ Ошибка: файл {file_path} не найден на сервере! Юзеру скрипт НЕ отправлен.")
            bot.send_message(user_id, "⚠️ Оплата подтверждена, но файл скрипта временно недоступен. Обратитесь к администратору.")
        
    elif call.data == "host_added":
        if not u.get('can_setup'):
            bot.answer_callback_query(call.id, "У вас нет активной подписки.", show_alert=True)
            return
        
        try: bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.message_id, reply_markup=None)
        except: pass
            
        bot.send_message(cid, "Отлично. Теперь отправьте данные от FTP:\n<code>IP Логин Пароль</code> (через пробел)", parse_mode="HTML")
        u['state'] = "waiting_ftp"
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    cid = message.chat.id
    u = get_user(cid)
    if u.get('state') == "waiting_pwn_file":
        if message.document.file_name.endswith('.pwn'):
            bot.send_message(cid, "⏳ Файл получен. Запуск компилятора pawncc...\n\n<i>[СИСТЕМА]: Функция облачной компиляции пока не привязана к серверу с Linux (pawncc). Это визуальная заглушка.</i>", parse_mode="HTML")
            u['state'] = None
        else:
            bot.send_message(cid, "❌ Мне нужен исходник с расширением .pwn!")
    else:
        bot.send_message(cid, "Я сейчас не жду от тебя файлы.")
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    cid = message.chat.id
    u = get_user(cid)
    if u.get('state') == "waiting_receipt":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Выдать сервер", callback_data=f"approve_{cid}"))
        markup.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{cid}"))
        
        bot.forward_message(ADMIN_ID, cid, message.message_id)
        bot.send_message(ADMIN_ID, f"⚠️ <b>Новый чек на СЕРВЕР от {message.from_user.first_name} (@{message.from_user.username})!</b>", reply_markup=markup, parse_mode="HTML")
        bot.send_message(cid, "⏳ <b>Ваш чек отправлен на проверку.</b> Ожидайте...", parse_mode="HTML")
        u['state'] = None
        
    elif u.get('state') == "waiting_stars_receipt":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Выдать сервер", callback_data=f"approve_{cid}"))
        markup.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{cid}"))
        
        bot.forward_message(ADMIN_ID, cid, message.message_id)
        bot.send_message(ADMIN_ID, f"⚠️ <b>Новый скриншот оплаты ЗВЕЗДАМИ от {message.from_user.first_name} (@{message.from_user.username})!</b>\nПроверь свои подарки.", reply_markup=markup, parse_mode="HTML")
        bot.send_message(cid, "⏳ <b>Ваш скриншот отправлен администратору.</b> Ожидайте...", parse_mode="HTML")
        u['state'] = None

    elif u.get('state') == "waiting_pwn_receipt":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Разрешить компиляцию", callback_data=f"apprpawn_{cid}"))
        markup.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"rejpawn_{cid}"))
        
        bot.forward_message(ADMIN_ID, cid, message.message_id)
        bot.send_message(ADMIN_ID, f"⚠️ <b>Новый чек на КОМПИЛЯЦИЮ (25₽) от {message.from_user.first_name} (@{message.from_user.username})!</b>", reply_markup=markup, parse_mode="HTML")
        bot.send_message(cid, "⏳ <b>Ваш чек отправлен на проверку.</b> Ожидайте...", parse_mode="HTML")
        u['state'] = None

    elif str(u.get('state', '')).startswith("waiting_script_receipt_"):
        sys_name = u['state'].replace("waiting_script_receipt_", "")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Выдать скрипт", callback_data=f"apprscript_{cid}_{sys_name}"))
        markup.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"rejpawn_{cid}"))
        
        bot.forward_message(ADMIN_ID, cid, message.message_id)
        bot.send_message(ADMIN_ID, f"⚠️ <b>Новый чек на ПОКУПКУ СКРИПТА ({sys_name}) от {message.from_user.first_name} (@{message.from_user.username})!</b>", reply_markup=markup, parse_mode="HTML")
        bot.send_message(cid, "⏳ <b>Ваш чек отправлен на проверку.</b> Ожидайте...", parse_mode="HTML")
        u['state'] = None
        
    else:
        bot.send_message(cid, "Я сейчас не жду от тебя чек.")
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    payload = message.successful_payment.invoice_payload
    if payload == "pawn_payment":
        get_user(message.chat.id)['state'] = "waiting_pwn_file"
        bot.send_message(message.chat.id, "✅ <b>Оплата звездами прошла (Компилятор)!</b>\n\nОтправьте мне ваш файл <code>.pwn</code>", parse_mode="HTML")
    else:
        get_user(message.chat.id)['can_setup'] = True
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Я добавил доступ", callback_data="host_added"))
        text = f"✅ <b>Оплата звездами за сервер прошла!</b>\n\nДобавьте этот ID в соавторы на хостинге:\n<code>{HOST_USER_ID}</code>\n\nЗатем нажмите кнопку:"
        send_with_banner(message.chat.id, text, markup)
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
    cid = message.chat.id
    u = get_user(cid)
    state = u.get('state')
    
    if state == "admin_waiting_broadcast":
        if message.text == "/cancel":
            bot.send_message(cid, "🛑 Рассылка отменена.")
        else:
            bot.send_message(cid, "⏳ <b>Начинаю рассылку...</b>", parse_mode="HTML")
            success = 0
            for uid in list(user_data.keys()):
                try:
                    bot.send_message(uid, f"📢 <b>Сообщение от администрации:</b>\n\n{message.text}", parse_mode="HTML")
                    success += 1
                    time.sleep(0.1)
                except:
                    pass
            bot.send_message(cid, f"✅ <b>Рассылка завершена!</b>\nДоставлено: {success} пользователям.", parse_mode="HTML")
        u['state'] = None
        
    elif state == "admin_waiting_promo_create":
        data = message.text.split()
        if len(data) >= 2 and data[1].isdigit():
            p_name = data[0]
            uses = int(data[1])
            disc = int(data[2]) if len(data) == 3 and data[2].isdigit() else 0
            
            promocodes[p_name] = {'uses': uses, 'discount': disc}
            p_type = f"Скидка {disc}%" if disc > 0 else "Бесплатный сервер"
            bot.send_message(cid, f"✅ <b>Промокод создан!</b>\nКод: <code>{p_name}</code>\nЛимит: {uses}\nТип: {p_type}", parse_mode="HTML")
            u['state'] = None
        else:
            bot.send_message(cid, "❌ Ошибка формата. Читайте инструкцию выше.")

    elif state == "waiting_promo":
        promo = message.text
        is_valid = False
        disc = 0
        with promo_lock:
            if promo in promocodes and promocodes[promo]['uses'] > 0:
                promocodes[promo]['uses'] -= 1
                disc = promocodes[promo].get('discount', 0)
                is_valid = True
        
        if is_valid:
            if disc > 0:
                u['discount'] = disc
                bot.send_message(cid, f"🎉 <b>Ура! Промокод активирован.</b>\nВам начислена скидка <b>{disc}%</b> на оплату сервера!\nЗайдите в меню и выберите способ оплаты.", parse_mode="HTML")
            else:
                u['can_setup'] = True
                bot.send_message(cid, "✅ <b>Промокод на бесплатный сервер активирован!</b>", parse_mode="HTML")
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("✅ Я добавил доступ", callback_data="host_added"))
                text = f"Добавьте этот ID в соавторы на хостинге:\n<code>{HOST_USER_ID}</code>\n\nЗатем нажмите кнопку:"
                send_with_banner(cid, text, markup)
            u['state'] = None
        else:
            bot.send_message(cid, "❌ Промокод не найден, либо его уже кто-то забрал.")
            u['state'] = None
            
    elif state == "admin_waiting_give":
        target = message.text.replace('@', '')
        t_id = None
        if target.isdigit():
            t_id = int(target)
        else:
            for uid, d in user_data.items():
                if d.get('username') == target:
                    t_id = uid
                    break
        if t_id:
            get_user(t_id)['can_setup'] = True
            bot.send_message(cid, f"✅ Доступ успешно выдан пользователю {target}!")
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("✅ Я добавил доступ", callback_data="host_added"))
            send_with_banner(t_id, f"🎁 <b>Администратор выдал вам доступ к серверу!</b>\n\nДобавьте ID <code>{HOST_USER_ID}</code> в соавторы и нажмите кнопку:", markup)
        else:
            bot.send_message(cid, "❌ Юзер не найден. Он должен хотя бы раз нажать /start в боте.")
        u['state'] = None
        
    elif state == "waiting_ftp":
        data = message.text.split()
        if len(data) == 3 and "." in data[0]:
            u['ftp_data'] = data
            u['state'] = "waiting_server_name"
            bot.send_message(cid, "✅ <b>FTP данные приняты.</b>\n\nНапишите желаемое <b>Название сервера</b>:", parse_mode="HTML")
        else:
            bot.send_message(cid, "❌ Неверный формат или IP-адрес без точек. Нужно: IP Логин Пароль (через пробел)")
            
    elif state == "waiting_server_name":
        u['server_name'] = message.text
        u['state'] = "waiting_server_ip"
        bot.send_message(cid, f"✅ Название <b>{message.text}</b> принято.\n\nТеперь напишите <b>IP вашего сервера</b> (если порт нестандартный, укажите через двоеточие, например <code>141.94.184.107:8888</code>):", parse_mode="HTML")
        
    elif state == "waiting_server_ip":
        ip_input = message.text.strip()
        if "." in ip_input:
            if ":" in ip_input:
                parts = ip_input.split(":", 1)
                u['server_ip'] = parts[0]
                u['server_port'] = int(parts[1]) if parts[1].isdigit() else 7777
            else:
                u['server_ip'] = ip_input
                u['server_port'] = 7777
                
            u['state'] = "waiting_bonuses"
            bot.send_message(cid, "✅ <b>IP принят.</b>\n\nУкажите стартовые бонусы (через пробел: Деньги Донат):\nПример: <code>5000000 1000</code>", parse_mode="HTML")
        else:
            bot.send_message(cid, "❌ Это не IP-адрес. Укажите нормальный IP с точками.")

    elif state == "waiting_bonuses":
        bonuses = message.text.split()
        if len(bonuses) == 2 and bonuses[0].isdigit() and bonuses[1].isdigit():
            u['bonus_money'] = bonuses[0]
            u['bonus_donate'] = bonuses[1]
            u['state'] = "waiting_mysql"
            bot.send_message(cid, "🗄 <b>Данные от БД.</b>\nВведи логин, пароль и имя базы через пробел.\nПример: <code>u1234_user pass123 u1234_base</code>", parse_mode="HTML")
        else:
            bot.send_message(cid, "❌ Неверный формат. Нужно два числа через пробел (только цифры).")

    elif state == "waiting_mysql":
        mysql_data = message.text.split()
        if len(mysql_data) != 3:
            bot.send_message(cid, "❌ Нужно три значения: Логин Пароль Имя_базы")
            return
        
        u['db_user'] = mysql_data[0]
        u['db_pass'] = mysql_data[1]
        u['db_name'] = mysql_data[2]
        u['state'] = None
        u['in_progress'] = True
        
        gm = InlineKeyboardMarkup()
        gm.add(InlineKeyboardButton("🔴 Слоты", callback_data="play_slots"), InlineKeyboardButton("🟢 Боулинг", callback_data="play_bowling"))
        gm.add(InlineKeyboardButton("🔵 Дартс", callback_data="play_darts"))
        
        msg = bot.send_message(cid, "⚙️ <b>Начинаю заливку мода на FTP...</b>\n\n⏳ <i>Это долгий процесс (от 5 до 15 минут). Чтобы не скучать, поиграй пока в официальные мини-игры Telegram:</i>", reply_markup=gm, parse_mode="HTML")
        print(f"\n=====================================")
        print(f"[{cid}] СТАРТ УСТАНОВКИ: {u['server_name']}")
        print(f"=====================================")
        # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
        
        try:
            bot.edit_message_text(f"⚙️ <b>Прогресс:</b> [10%]\nУстанавливаю соединение с FTP... Бот работает, не завис! ⏳", chat_id=cid, message_id=msg.message_id, reply_markup=gm, parse_mode="HTML")
            print(f"[{cid}] Подключение к FTP: {u['ftp_data'][0]}")
            ftp = ftplib.FTP()
            ftp.connect(u['ftp_data'][0], timeout=120)
            ftp.login(u['ftp_data'][1], u['ftp_data'][2])
            ftp.set_pasv(True)
            
            try:
                bot.edit_message_text(f"⚙️ <b>Прогресс:</b> [40%]\nЗаливаю тысячи файлов на хостинг...\n\n✅ <i>Бот не завис, просто жди (5-15 минут). Тыкай мини-игры ниже:</i>", chat_id=cid, message_id=msg.message_id, reply_markup=gm, parse_mode="HTML")
            except:
                pass
            print(f"[{cid}] Настройка конфигов и заливка мода на FTP...")
            
            port_line = f"port {u.get('server_port', 7777)}\n" if u.get('server_port', 7777) != 7777 else ""
            cfg_content = (
                f"echo Executing Server Config...\n"
                f"lanmode 0\n"
                f"query 1\n"
                f"rcon_password bybapassword123\n"
                f"maxplayers 50\n"
                f"bind {u['server_ip']}\n"
                f"{port_line}"
                f"hostname {u['server_name']}\n"
                f"gamemode0 Tomaris 1\n"
                f"plugins mysql streamer sscanf\n"
                f"mysql_host {u['server_ip']}\n"
                f"mysql_user {u['db_user']}\n"
                f"mysql_pass {u['db_pass']}\n"
                f"mysql_db {u['db_name']}\n"
            )
            cfg_io = io.BytesIO(cfg_content.encode('utf-8'))
            try:
                ftp.storbinary('STOR server.cfg', cfg_io)
            except Exception as e:
                print(f"[{cid}] Ошибка загрузки server.cfg: {e}")
            
            local_mod_dir = "modbyba"
            if os.path.exists(local_mod_dir):
                def upload_ftp_tree(ftp_conn, local_dir):
                    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
                    for item in os.listdir(local_dir):
                        local_path = os.path.join(local_dir, item)
                        if item in ["byba.sql", "server.cfg"]:
                            continue
                        if os.path.isfile(local_path):
                            try:
                                with open(local_path, 'rb') as f:
                                    ftp_conn.storbinary(f'STOR {item}', f)
                            except Exception as e:
                                print(f"[{cid}] Ошибка файла {item}: {e}")
                        elif os.path.isdir(local_path):
                            try: ftp_conn.mkd(item)
                            except: pass
                            try:
                                ftp_conn.cwd(item)
                                upload_ftp_tree(ftp_conn, local_path)
                                ftp_conn.cwd("..")
                            except Exception as e:
                                print(f"[{cid}] Ошибка папки {item}: {e}")
                    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
                
                upload_ftp_tree(ftp, local_mod_dir)
            
            try:
                try:
                    ftp.cwd('scriptfiles')
                except Exception:
                    ftp.mkd('scriptfiles')
                    ftp.cwd('scriptfiles')
                
                ini_content = f"host = {u['server_ip']}\nusername = {u['db_user']}\npassword = {u['db_pass']}\ndatabase = {u['db_name']}\n"
                ini_io = io.BytesIO(ini_content.encode('utf-8'))
                ftp.storbinary('STOR bymisters_mysql_settings.ini', ini_io)
                ftp.cwd('..')
                print(f"[{cid}] Файл bymisters_mysql_settings.ini перезаписан на FTP!")
            except Exception as e:
                print(f"[{cid}] Ошибка записи bymisters_mysql_settings.ini: {e}")
                
            ftp.quit()
            
            try:
                bot.delete_message(cid, msg.message_id)
            except:
                pass
                
            send_with_banner(cid, f"✅ <b>Установка успешно завершена!</b>\n\nМод залит на хостинг.\nСервер: {u['server_name']}\nIP: {u['server_ip']}\nВыданы бонусы: {u['bonus_money']} виртов, {u['bonus_donate']} доната.\nЖдите APK.")
            print(f"[{cid}] Сборка мода завершена, отправка БД...")
            
            sql_path = os.path.join(local_mod_dir, "byba.sql")
            if os.path.exists(sql_path):
                with open(sql_path, "rb") as sql_file:
                    caption = "🗄 <b>ОБЯЗАТЕЛЬНО К ВЫПОЛНЕНИЮ!</b>\n\nЗайдите в phpMyAdmin на вашем хостинге и импортируйте этот файл (byba.sql) в вашу базу данных. Если этого не сделать, мод работать не будет!"
                    bot.send_document(cid, sql_file, caption=caption, parse_mode="HTML")
                    print(f"[{cid}] База данных отправлена юзеру")
            else:
                bot.send_message(cid, "⚠️ <b>Ошибка:</b> файл byba.sql не найден в папке modbyba на телефоне.", parse_mode="HTML")
            apk_msg = bot.send_message(cid, "⏳ <b>Генерация облачного JSON-конфига...</b>", parse_mode="HTML")
            
            gh_headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            gist_data = {
                "description": f"Config for {u['server_name']}",
                "public": True,
                "files": {
                    "settings.json": {
                        "content": json.dumps({"ip": u['server_ip'], "port": u.get('server_port', 7777)})
                    }
                }
            }
            
            print(f"[{cid}] Создание Gist...")
            gist_resp = requests.post("https://api.github.com/gists", headers=gh_headers, json=gist_data)
            
            if gist_resp.status_code != 201:
                raise Exception(f"Отказ GitHub API при создании JSON (Код {gist_resp.status_code}): {gist_resp.text}")
                
            gist_url = gist_resp.json()['files']['settings.json']['raw_url']
            print(f"[{cid}] Gist создан: {gist_url}")
            
            bot.edit_message_text("⏳ <b>Передача параметров на GitHub Actions...</b>", chat_id=cid, message_id=apk_msg.message_id, parse_mode="HTML")
            
            gh_data = {
                "ref": "main",
                "inputs": {
                    "server_name": u['server_name'],
                    "api_link": gist_url,
                    "chat_id": str(cid)
                }
            }
            
            print(f"[{cid}] Отправка POST запроса в GitHub Actions...")
            gh_resp = requests.post(f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/build.yml/dispatches", headers=gh_headers, json=gh_data)
            
            if gh_resp.status_code == 204:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("📄 Посмотреть ваш JSON", url=gist_url))
                bot.edit_message_text("✅ <b>Сборка лаунчера запущена!</b>\n\nGitHub Actions начал компиляцию приложения. Это займет 3-5 минут.\n<i>Как только всё будет готово, бот автоматически пришлет вам файл.</i>", chat_id=cid, message_id=apk_msg.message_id, reply_markup=markup, parse_mode="HTML")
                print(f"[{cid}] УСПЕХ: GitHub принял команду на сборку")
                u['can_setup'] = False
                u['state'] = None
            else:
                raise Exception(f"Отказ GitHub Actions (Код {gh_resp.status_code}): {gh_resp.text}")
                
            u['in_progress'] = False
            
        except Exception as e:
            bot.send_message(cid, f"❌ <b>Произошла ошибка при установке:</b>\n<code>{e}</code>", parse_mode="HTML")
            print(f"[{cid}] ГЛОБАЛЬНАЯ ОШИБКА: {e}")
            u['in_progress'] = False
        # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН

print("Бот запущен и готов к работе...")
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка сети: {e}")
        time.sleep(5)
    # АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
# АВТОР СЛИВА ЛОНЕКС И БЛЕЙН
import asyncio
import json
import logging
import os
import re
from datetime import datetime

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN", "8982437206:AAEylAk110v45GO16pk-Onlf4-SQsrdZNGA")


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. Serverda BOT_TOKEN environment variable o‘rnating."
    )

ADMIN_ID = 7414653407
ADMIN_USERNAME = "@rymbyvv"
SUB_CHANNELS = ["@rymbyvv_otziv"]
DATA_FILE = "bot_database.json"

PAYMENT_CARD = os.getenv("PAYMENT_CARD") or "9860 3566 3465 1745"
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER") or "Elvira kuralova"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())


def default_prices():
    return {
        "stars": {
            str(s): int(s * 220)
            for s in range(50, 951, 50)
        },
        "gifts": {
            "gift_13_1": 2700,
            "gift_13_2": 2700,
            "gift_21_1": 4600,
            "gift_21_2": 4600,
            "gift_43_1": 9000,
            "gift_43_2": 9000,
            "gift_85_1": 18000,
            "gift_85_2": 18000
        },
        "premium": {
            "prem_1": 45000,
            "prem_3": 180000,
            "prem_6": 310000,
            "prem_12": 435000
        },
        "sell_gifts": {
            "sell_gift_bear": 2000,
            "sell_gift_heart": 2000,
            "sell_gift_box": 3300,
            "sell_gift_rose": 3300,
            "sell_gift_rocket": 6600,
            "sell_gift_cake": 6600,
            "sell_gift_gem": 13200,
            "sell_gift_ring": 13200
        },
        "custom_star": 220,
        "referral_reward": 1.5,
        "menu_emojis": {},
        "purchase_history": [],
        "texts": {
            "uz": {
                "main_title": "Asosiy menyu",
                "main_trust": "Biz bilan ishonchli savdo qiling",
                "main_channel": "@rymbyvv_otziv kanalidagi yangiliklarni kuzatib boring",
                "main_hint": "Kerakli xizmatni tanlang",
                "deposit_title": "Hisob to'ldirish",
                "deposit_prompt": "Hisobingizni qanchaga to'ldirmoqchisiz?",
                "deposit_minmax": "Minimum: <b>1.000 so'm</b>\nMaksimum: <b>22.500 so'm</b>",
                "deposit_input": "Miqdorni yozing:",
                "payment_card_label": "Karta:",
                "payment_owner_label": "Ega:",
                "payment_transfer": "Kartaga <b>{amount} so'm</b> o'tkazing.",
                "payment_done_instruction": "To'lovni amalga oshirgach, <b>To'lovni amalga oshirdim</b> tugmasini bosing.",
                "payment_timer": "Bu oyna <b>5 daqiqa</b> amal qiladi.",
                "payment_keep_receipt": "Chekni saqlab qo'ying.",
                "payment_done_button": "To'lovni amalga oshirdim",
                "payment_cancel_button": "Bekor qilish",
                "receipt_request": "<b>To'lov chekini yuboring.</b>\n\nIltimos, to'lov qilganingizni tasdiqlovchi <b>rasm yoki screenshot</b>ni shu yerga yuboring.\n\nChekni 5 daqiqa ichida yuboring.",
                "receipt_accepted": "<b>Chek qabul qilindi!</b>\n\nTo'lovingiz tekshirilmoqda.\n5 daqiqa ichida balansingizga qo'shilmasa,\nadminga murojaat qiling.",
                "profile_title": "Profil", "language": "Til", "choose_lang": "Interfeys tilini tanlang:",
                "referral_title": "Referal tizimi", "contact_text": "Referal mukofotidan foydalanish uchun O'zbekiston (+998) yoki Rossiya (+7) raqamingizni yuboring.",
                "account": "Sizning hisobingiz", "balance_label": "Pul balansi:"
            },
            "ru": {
                "main_title": "Главное меню",
                "main_trust": "Совершайте покупки с нами безопасно",
                "main_channel": "Следите за новостями канала @rymbyvv_otziv",
                "main_hint": "Выберите нужную услугу",
                "deposit_title": "Пополнение счёта",
                "deposit_prompt": "На какую сумму хотите пополнить счёт?",
                "deposit_minmax": "Минимум: <b>1.000 сум</b>\nМаксимум: <b>22.500 сум</b>",
                "deposit_input": "Введите сумму:",
                "payment_card_label": "Карта:",
                "payment_owner_label": "Владелец:",
                "payment_transfer": "Переведите на карту <b>{amount} сум</b>.",
                "payment_done_instruction": "После оплаты нажмите кнопку <b>Я оплатил</b>.",
                "payment_timer": "Это окно действует <b>5 минут</b>.",
                "payment_keep_receipt": "Сохраните чек.",
                "payment_done_button": "Я оплатил",
                "payment_cancel_button": "Отмена",
                "receipt_request": "<b>Отправьте чек об оплате.</b>\n\nОтправьте сюда <b>фото или скриншот</b>, подтверждающий оплату.\n\nОтправьте чек в течение 5 минут.",
                "receipt_accepted": "<b>Чек принят!</b>\n\nВаш платёж проверяется.\nЕсли баланс не пополнится в течение 5 минут,\nобратитесь к администратору.",
                "profile_title": "Профиль", "language": "Язык", "choose_lang": "Выберите язык интерфейса:",
                "referral_title": "Реферальная система", "contact_text": "Для получения реферального вознаграждения отправьте номер Узбекистана (+998) или России (+7).",
                "account": "Ваш счёт", "balance_label": "Баланс:"
            }
        }
    }


def load_data():
    defaults = default_prices()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            saved_prices = data.get("prices", {})
            saved_texts = data.get("texts", {})
            if isinstance(saved_texts, dict):
                if "uz" in saved_texts or "ru" in saved_texts:
                    for code in ("uz", "ru"):
                        if isinstance(saved_texts.get(code), dict):
                            defaults["texts"][code].update({k: str(v) for k, v in saved_texts[code].items() if k in defaults["texts"][code]})
                else:
                    defaults["texts"]["uz"].update({k: str(v) for k, v in saved_texts.items() if k in defaults["texts"]["uz"]})

            for group in defaults:
                if group == "custom_star":
                    value = saved_prices.get(group)
                    if isinstance(value, (int, float)):
                        defaults[group] = int(value)
                elif group == "referral_reward":
                    value = saved_prices.get(group)
                    if isinstance(value, (int, float)):
                        defaults[group] = float(value)
                elif group == "texts":
                    continue
                elif isinstance(saved_prices.get(group), dict):
                    for key in defaults[group]:
                        if key in saved_prices[group]:
                            try:
                                defaults[group][key] = int(saved_prices[group][key])
                            except Exception:
                                pass

            return {
                "user_balances": {int(k): int(v) for k, v in data.get("user_balances", {}).items()},
                "user_stars_balances": {int(k): float(v) for k, v in data.get("user_stars_balances", {}).items()},
                "user_referrals": {int(k): int(v) for k, v in data.get("user_referrals", {}).items()},
                "registered_users": set(int(k) for k in data.get("registered_users", [])),
                "verified_phones": {str(k): str(v) for k, v in data.get("verified_phones", {}).items()},
                "user_languages": {str(k): str(v) for k, v in data.get("user_languages", {}).items()},
                "user_join_dates": {str(k): str(v) for k, v in data.get("user_join_dates", {}).items()},
                "referral_pending": {str(k): int(v) for k, v in data.get("referral_pending", {}).items()},
                "referral_processed": {str(k): True for k in data.get("referral_processed", [])},
                "purchase_history": data.get("purchase_history", []),
                "menu_emojis": data.get("menu_emojis", {}),
                "texts": defaults["texts"],
                "prices": defaults
            }
        except Exception:
            pass

    return {
        "user_balances": {},
        "user_stars_balances": {},
        "user_referrals": {},
        "registered_users": set(),
        "verified_phones": {},
        "user_languages": {},
        "user_join_dates": {},
        "referral_pending": {},
        "referral_processed": {},
        "purchase_history": [],
        "menu_emojis": {},
        "texts": defaults["texts"],
        "prices": defaults
    }


db = load_data()
user_balances = db["user_balances"]
user_stars_balances = db["user_stars_balances"]
user_referrals = db["user_referrals"]
registered_users = db["registered_users"]
verified_phones = db.get("verified_phones", {})
user_languages = db.get("user_languages", {})
user_join_dates = db.get("user_join_dates", {})
referral_pending = db.get("referral_pending", {})
referral_processed = db.get("referral_processed", {})
purchase_history = db.get("purchase_history", [])
menu_emojis = db.get("menu_emojis", {})
texts = db.get("texts", default_prices()["texts"])
prices = db["prices"]

last_menu_messages = {}
active_orders = {}
pending_payments = {}
payment_expiry_tasks = {}


class DepositState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()

class BuyState(StatesGroup):
    waiting_for_target = State()

class CustomStarsState(StatesGroup):
    waiting_for_stars_amount = State()

class GiftProcess(StatesGroup):
    waiting_for_receipt = State()
    waiting_for_card_details = State()

class WithdrawStarsState(StatesGroup):
    waiting_for_username = State()

class ContactState(StatesGroup):
    waiting_for_contact = State()

class EmojiState(StatesGroup):
    waiting_for_key = State()
    waiting_for_id = State()

class AdminState(StatesGroup):
    waiting_for_user_id_add = State()
    waiting_for_amount_add = State()
    waiting_for_user_id_sub = State()
    waiting_for_amount_sub = State()
    waiting_for_user_id_check = State()
    waiting_for_broadcast = State()
    waiting_for_price = State()
    waiting_for_referral_reward = State()
    waiting_for_message_user_id = State()
    waiting_for_user_message = State()
    waiting_for_delete_user_id = State()
    waiting_for_delete_message_id = State()
    waiting_for_text = State()


def save_data():
    data = {
        "user_balances": user_balances,
        "user_stars_balances": user_stars_balances,
        "user_referrals": user_referrals,
        "registered_users": list(registered_users),
        "verified_phones": verified_phones,
        "user_languages": user_languages,
        "user_join_dates": user_join_dates,
        "referral_pending": referral_pending,
        "referral_processed": list(referral_processed.keys()) if isinstance(referral_processed, dict) else list(referral_processed),
        "purchase_history": purchase_history,
        "menu_emojis": menu_emojis,
        "texts": texts,
        "prices": prices
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def money(n):
    return f"{int(n):,}".replace(",", ".")

def format_stars(value):
    return f"{float(value):g}"

def lang(user_id):
    return user_languages.get(str(user_id), "uz")

LANG_TEXT = {
    "uz": {
        "settings": "Sozlamalar", "profile": "Profil", "language": "Til", "choose_lang": "Interfeys tilini tanlang:",
        "uzbek": "O'zbekcha", "russian": "Русский", "back": "Orqaga", "refresh": "Yangilash",
        "deposit": "Hisob to'ldirish", "stars": "Stars olish", "gift": "Gift olish", "premium": "Premium olish", "balance": "Hisobim",
        "sell": "Gift sotish", "referral": "Referal tizimi", "top": "Top reyting", "admin": "Admin (Aloqa)", "settings_btn": "Sozlamalar",
        "main_title": "Asosiy menyu", "main_trust": "Biz bilan ishonchli savdo qiling", "main_hint": "Kerakli xizmatni tanlang", "profile_title": "Profil", "id": "ID", "username": "Username",
        "joined": "A'zo bo'lingan", "language_label": "Til", "today": "Bugungi", "week": "Haftalik", "month": "Oylik", "top_buyers": "Top oluvchilar",
        "no_data": "Hozircha reyting uchun ma'lumot yetarli emas.", "referral_title": "Referal tizimi", "withdraw": "Stars yechib olish",
        "contact_title": "Telefon raqamini tasdiqlash", "contact_text": "Referal mukofotidan foydalanish uchun O'zbekiston (+998) yoki Rossiya (+7) raqamingizni yuboring.",
        "share_contact": "Raqamni yuborish", "bad_phone": "Faqat +998 yoki +7 raqamlariga ruxsat beriladi.", "phone_ok": "Raqam tasdiqlandi.",
    },
    "ru": {
        "settings": "Настройки", "profile": "Профиль", "language": "Язык", "choose_lang": "Выберите язык интерфейса:",
        "uzbek": "O'zbekcha", "russian": "Русский", "back": "Назад", "refresh": "Обновить",
        "deposit": "Пополнить счёт", "stars": "Купить Stars", "gift": "Купить Gift", "premium": "Купить Premium", "balance": "Мой счёт",
        "sell": "Продать Gift", "referral": "Реферальная система", "top": "Топ рейтинг", "admin": "Админ (Связь)", "settings_btn": "Настройки",
        "main_title": "Главное меню", "main_trust": "Совершайте покупки с нами безопасно", "main_hint": "Выберите нужную услугу", "profile_title": "Профиль", "id": "ID", "username": "Username",
        "joined": "Дата регистрации", "language_label": "Язык", "today": "Сегодня", "week": "Неделя", "month": "Месяц", "top_buyers": "Топ покупателей",
        "no_data": "Пока недостаточно данных для рейтинга.", "referral_title": "Реферальная система", "withdraw": "Вывести Stars",
        "contact_title": "Подтверждение номера", "contact_text": "Для реферального вознаграждения отправьте номер Узбекистана (+998) или России (+7).",
        "share_contact": "Отправить номер", "bad_phone": "Разрешены только номера +998 или +7.", "phone_ok": "Номер подтверждён.",
    }
}

def tr(user_id, key):
    return LANG_TEXT.get(lang(user_id), LANG_TEXT["uz"]).get(key, LANG_TEXT["uz"].get(key, key))

def editable_text(key, fallback="", user_id=0):
    code = lang(user_id) if user_id else "uz"
    bucket = texts.get(code, {}) if isinstance(texts, dict) else {}
    if isinstance(bucket, dict) and key in bucket:
        return str(bucket[key])
    return str(fallback)

def custom_tag(key):
    eid = menu_emojis.get(key)
    return f'<tg-emoji emoji-id="{eid}">✨</tg-emoji> ' if eid else ''

def p_btn(text, cb, key):
    eid = menu_emojis.get(key)
    return types.InlineKeyboardButton(text=text, callback_data=cb, icon_custom_emoji_id=eid if eid else None)

def p_url_btn(text, url, key):
    eid = menu_emojis.get(key)
    return types.InlineKeyboardButton(text=text, url=url, icon_custom_emoji_id=eid if eid else None)

def phone_allowed(phone):
    digits = re.sub(r"\D", "", phone or "")
    return digits.startswith("998") or digits.startswith("7")

def top_period_start(period):
    from datetime import timedelta
    now = datetime.now()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "week":
        return now - timedelta(days=7)
    return now - timedelta(days=30)

def build_top_text(user_id, period):
    start = top_period_start(period)
    rows = {}
    for item in purchase_history:
        try:
            dt = datetime.fromisoformat(item.get("time", ""))
            if dt < start:
                continue
            uid = str(item.get("user_id"))
            rows.setdefault(uid, {"name": item.get("name") or uid, "total": 0, "count": 0})
            rows[uid]["total"] += int(item.get("price", 0))
            rows[uid]["count"] += 1
        except Exception:
            continue
    ranked = sorted(rows.values(), key=lambda x: (-x["total"], -x["count"]))[:10]
    title = tr(user_id, "today" if period == "today" else "week" if period == "week" else "month")
    text = f"<blockquote>{custom_tag('top')}<b>{tr(user_id,'top_buyers')} — {title}</b>\n\n"
    if not ranked:
        return text + tr(user_id, "no_data") + "</blockquote>"
    for i, row in enumerate(ranked, 1):
        text += f"{i}. <b>{row['name']}</b> — {money(row['total'])} so'm ({row['count']} ta)\n"
    return text + "</blockquote>"

def get_balance(user_id):
    return user_balances.get(user_id, 0)

def update_balance(user_id, amount):
    user_balances[user_id] = get_balance(user_id) + amount
    save_data()

def get_stars_balance(user_id):
    return user_stars_balances.get(user_id, 0.0)

def add_star_referral(user_id):
    reward = float(prices.get("referral_reward", 1.5))
    user_stars_balances[user_id] = round(get_stars_balance(user_id) + reward, 2)
    user_referrals[user_id] = user_referrals.get(user_id, 0) + 1
    save_data()


def build_products():
    stars = {}
    for s in range(50, 951, 50):
        p = prices["stars"].get(str(s), s * 220)
        stars[f"stars_{s}"] = {
            "name": f"{s} Stars - {money(p)} so'm",
            "formatted": f"{custom_tag('stars')}<b>{s} Stars</b> - {money(p)} so'm",
            "price": int(p),
            "count": s
        }

    gifts_info = {
        "gift_13_1": 13, "gift_13_2": 13,
        "gift_21_1": 21, "gift_21_2": 21,
        "gift_43_1": 43, "gift_43_2": 43,
        "gift_85_1": 85, "gift_85_2": 85
    }

    gifts = {}
    for key, count in gifts_info.items():
        p = prices["gifts"][key]
        gifts[key] = {
            "name": f"{count} stars - {money(p)} so'm",
            "formatted": f"{custom_tag(key)}{count} stars - {money(p)} so'm",
            "price": int(p)
        }

    premium_names = {
        "prem_1": "1 oy", "prem_3": "3 oy", "prem_6": "6 oy", "prem_12": "1 yil"
    }

    premium = {}
    for key, title in premium_names.items():
        p = prices["premium"][key]
        premium[key] = {
            "name": f"{title} - {money(p)} so'm",
            "formatted": f"{custom_tag(key)}<b>{title}</b> - {money(p)} so'm",
            "price": int(p)
        }

    return stars, gifts, premium


STARS_PRICES, GIFT_PRICES, PREMIUM_PRICES = build_products()
ALL_PRODUCTS = {}
ALL_PRODUCTS.update(STARS_PRICES)
ALL_PRODUCTS.update(GIFT_PRICES)
ALL_PRODUCTS.update(PREMIUM_PRICES)

def refresh_products():
    global STARS_PRICES, GIFT_PRICES, PREMIUM_PRICES, ALL_PRODUCTS
    STARS_PRICES, GIFT_PRICES, PREMIUM_PRICES = build_products()
    ALL_PRODUCTS = {}
    ALL_PRODUCTS.update(STARS_PRICES)
    ALL_PRODUCTS.update(GIFT_PRICES)
    ALL_PRODUCTS.update(PREMIUM_PRICES)

async def check_all_subs(user_id):
    unsubscribed = []
    for channel in SUB_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                unsubscribed.append(channel)
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xatolik: {e}")
            unsubscribed.append(channel)
    return unsubscribed

def get_sub_keyboard(unsubscribed_channels):
    builder = InlineKeyboardBuilder()
    for ch in unsubscribed_channels:
        builder.row(
            types.InlineKeyboardButton(
                text=f"{ch} ga obuna bo'lish",
                url=f"https://t.me/{ch.replace('@', '')}",
                icon_custom_emoji_id=menu_emojis.get("channel_btn")
            )
        )
    builder.row(
        p_btn("Obunani tekshirish", "check_subscription", "check_btn")
    )
    return builder.as_markup()

def price_group_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        p_btn("Stars narxlari", "price_group_stars", "stars"),
        p_btn("Gift narxlari", "price_group_gifts", "gift")
    )
    builder.row(
        p_btn("Premium narxlari", "price_group_premium", "premium"),
        p_btn("Gift sotish narxlari", "price_group_sell", "sell")
    )
    builder.row(
        p_btn("1 Stars narxi", "price_edit_custom_star", "custom_stars")
    )
    builder.row(
        p_btn("Admin Panel", "admin_panel", "back")
    )
    return builder.as_markup()

def get_main_inline_menu(user_id=None):
    uid = user_id or 0
    builder = InlineKeyboardBuilder()
    builder.row(p_btn(tr(uid, "deposit"), "deposit", "deposit"))
    builder.row(p_btn(tr(uid, "stars"), "buy_stars", "stars"), p_btn(tr(uid, "gift"), "buy_gift", "gift"))
    builder.row(p_btn(tr(uid, "premium"), "buy_premium", "premium"), p_btn(tr(uid, "balance"), "my_balance", "balance"))
    builder.row(p_btn(tr(uid, "sell"), "sell_gift_menu", "sell"), p_btn(tr(uid, "referral"), "referral_system", "referral"))
    builder.row(p_btn(tr(uid, "top"), "top_rating", "top"), p_btn(tr(uid, "settings_btn"), "settings", "settings"))
    builder.row(p_url_btn(tr(uid, "admin"), f"https://t.me/{ADMIN_USERNAME.replace('@','')}", "admin"))
    if uid == ADMIN_ID:
        builder.row(p_btn("Admin Panel", "admin_panel", "settings"))
    return builder.as_markup()

def get_bottom_reply_keyboard(user_id=0):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=tr(user_id, "refresh")))
    return builder.as_markup(resize_keyboard=True)

def main_menu_text(user_id=0):
    title = editable_text("main_title", tr(user_id, "main_title"), user_id)
    trust = editable_text("main_trust", tr(user_id, "main_trust"), user_id)
    channel = editable_text("main_channel", "@rymbyvv_otziv kanalidagi yangiliklarni kuzatib boring", user_id)
    hint = editable_text("main_hint", tr(user_id, "main_hint"), user_id)
    return (
        f"<blockquote>{custom_tag('main_title')}<b>{title}</b>\n\n"
        f"{custom_tag('main_trust')}{trust}\n\n"
        f"{custom_tag('main_channel')}{channel}\n\n"
        f"{custom_tag('main_hint')}{hint}</blockquote>"
    )

def back_main_keyboard(user_id=0):
    builder = InlineKeyboardBuilder()
    builder.row(p_btn(tr(user_id, "back"), "back_main", "back"))
    return builder.as_markup()

async def safe_delete(message):
    try:
        await message.delete()
    except Exception:
        pass

async def delete_previous_menu(user_id):
    if user_id in last_menu_messages:
        try:
            await bot.delete_message(chat_id=user_id, message_id=last_menu_messages[user_id])
        except Exception:
            pass
        last_menu_messages.pop(user_id, None)

def get_admin_panel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        p_btn("Statistika", "admin_stats", "top"),
        p_btn("Foydalanuvchi balansi", "admin_check_bal", "balance")
    )
    builder.row(
        p_btn("Balans Qo'shish", "admin_add_bal", "deposit"),
        p_btn("Balans Ayirish", "admin_sub_bal", "sell")
    )
    builder.row(p_btn("Narxlarni boshqarish", "admin_prices", "custom_stars"))
    builder.row(p_btn("Premium Emoji boshqarish", "admin_emojis", "premium"))
    builder.row(p_btn("Textlarni o'zgartirish", "admin_texts", "settings"))
    builder.row(
        p_btn("Referal mukofoti", "admin_referral_reward", "referral"),
        p_btn("Foydalanuvchiga xabar", "admin_user_message", "admin")
    )
    builder.row(p_btn("Bot xabarini o'chirish", "admin_delete_message", "cancel"))
    builder.row(p_btn("Xabar Yuborish", "admin_broadcast", "channel_btn"))
    builder.row(p_btn("Bosh Menyu", "back_main", "back"))
    return builder.as_markup()


@dp.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback, state):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        f"<blockquote>{custom_tag('settings')}<b>Admin Panel</b>\n\nKerakli bo'limni tanlang:</blockquote>",
        reply_markup=get_admin_panel_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback):
    if callback.from_user.id != ADMIN_ID:
        return
    total_money = sum(user_balances.values())
    total_stars = sum(user_stars_balances.values())
    text = (
        f"<blockquote>{custom_tag('top')}<b>Bot Statistikasi:</b>\n\n"
        f"Barcha foydalanuvchilar: <b>{len(registered_users)} ta</b>\n"
        f"Umumiy balans: <b>{money(total_money)} so'm</b>\n"
        f"Umumiy referal Stars: <b>{format_stars(total_stars)} Stars</b></blockquote>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Admin Panel", "admin_panel", "back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


# BARCHA PREMIUM EMOJI KALITLARI
EMOJI_CATEGORIES = {
    "cat_main": "🏠 Asosiy menyu tugmalari",
    "cat_prem": "💎 Premium bo'limi",
    "cat_gifts": "🎁 Giftlar bo'limi",
    "cat_top": "🏆 Reyting & Sozlamalar",
    "cat_actions": "⚙️ Boshqa tugmalar"
}

CATEGORY_ITEMS = {
    "cat_main": [
        ("deposit", "Hisob to'ldirish tugmasi"),
        ("stars", "Stars olish tugmasi"),
        ("gift", "Gift olish tugmasi"),
        ("premium", "Premium olish tugmasi"),
        ("balance", "Hisobim tugmasi"),
        ("sell", "Gift sotish tugmasi"),
        ("referral", "Referal tizimi tugmasi"),
        ("top", "Top reyting tugmasi"),
        ("settings", "Sozlamalar tugmasi"),
        ("admin", "Admin (Aloqa) tugmasi"),
    ],
    "cat_prem": [
        ("prem_auto", "Profilga kirmasdan (Avto)"),
        ("prem_admin", "Profilga kirib (Admin orqali)"),
        ("prem_1", "Premium (1 oy)"),
        ("prem_3", "Premium (3 oy)"),
        ("prem_6", "Premium (6 oy)"),
        ("prem_12", "Premium (1 yil)"),
    ],
    "cat_gifts": [
        ("gift_13_1", "Gift 13 Stars (1)"),
        ("gift_13_2", "Gift 13 Stars (2)"),
        ("gift_21_1", "Gift 21 Stars (1)"),
        ("gift_21_2", "Gift 21 Stars (2)"),
        ("gift_43_1", "Gift 43 Stars (1)"),
        ("gift_43_2", "Gift 43 Stars (2)"),
        ("gift_85_1", "Gift 85 Stars (1)"),
        ("gift_85_2", "Gift 85 Stars (2)"),
        ("sell_gift_bear", "Gift sotish: Bear"),
        ("sell_gift_heart", "Gift sotish: Heart"),
        ("sell_gift_box", "Gift sotish: Box"),
        ("sell_gift_rose", "Gift sotish: Rose"),
        ("sell_gift_rocket", "Gift sotish: Rocket"),
        ("sell_gift_cake", "Gift sotish: Cake"),
        ("sell_gift_gem", "Gift sotish: Gem"),
        ("sell_gift_ring", "Gift sotish: Ring"),
    ],
    "cat_top": [
        ("lang_uz", "Til: O'zbekcha"),
        ("lang_ru", "Til: Русский"),
        ("top_today", "Top: Bugun"),
        ("top_week", "Top: Hafta"),
        ("top_month", "Top: Oy"),
        ("profile", "O'zimning profilimga"),
        ("target_other", "Boshqa profilga"),
    ],
    "cat_actions": [
        ("back", "Orqaga tugmasi"),
        ("refresh", "Yangilash tugmasi"),
        ("custom_stars", "Boshqa miqdorda Stars"),
        ("channel_btn", "Kanalga obuna bo'lish"),
        ("check_btn", "Obunani tekshirish"),
        ("payment_done", "To'lovni amalga oshirdim"),
        ("cancel", "Bekor qilish tugmasi"),
        ("confirm_buy", "Xaridni tasdiqlash"),
    ]
}


@dp.callback_query(F.data == "admin_emojis")
async def admin_emojis_categories(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    for cat_id, cat_name in EMOJI_CATEGORIES.items():
        b.row(types.InlineKeyboardButton(text=cat_name, callback_data=cat_id))
    b.row(p_btn("Admin Panel", "admin_panel", "back"))
    await callback.message.edit_text(
        "<b>🎨 Premium Emoji boshqarish</b>\n\nBo'limni tanlang:",
        reply_markup=b.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.in_(set(EMOJI_CATEGORIES.keys())))
async def admin_emojis_list(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    cat = callback.data
    items = CATEGORY_ITEMS.get(cat, [])
    b = InlineKeyboardBuilder()
    for key, label in items:
        curr_id = menu_emojis.get(key)
        status = f"ID: {curr_id}" if curr_id else "yo'q"
        b.row(types.InlineKeyboardButton(text=f"{label} — {status}", callback_data=f"emoji_edit_{key}"))
    b.row(p_btn("Bo'limlar", "admin_emojis", "back"))
    await callback.message.edit_text(
        f"<b>🎨 {EMOJI_CATEGORIES.get(cat)}</b>\n\nEmoji ID qo'ymoqchi bo'lgan tugmangizni tanlang:",
        reply_markup=b.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("emoji_edit_"))
async def emoji_edit_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.replace("emoji_edit_", "")
    await state.update_data(emoji_key=key)
    curr_id = menu_emojis.get(key, "Mavjud emas")
    await callback.message.edit_text(
        f"<b>🎨 Tugma:</b> <code>{key}</code>\n\n"
        f"Hozirgi Premium Emoji ID: <code>{curr_id}</code>\n\n"
        "Yangi custom emoji ID ni yuboring.\n"
        "O'chirib tashlash uchun <code>0</code> yuboring.",
        reply_markup=back_main_keyboard(ADMIN_ID)
    )
    await state.set_state(EmojiState.waiting_for_id)
    await callback.answer()


@dp.message(EmojiState.waiting_for_id)
async def emoji_edit_save(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    raw = (message.text or '').strip()
    if not raw.isdigit():
        await message.answer("⚠️ Faqat raqamli custom emoji ID yuboring.")
        return
    data = await state.get_data()
    key = data.get('emoji_key')
    if raw == '0':
        menu_emojis.pop(key, None)
    else:
        menu_emojis[key] = raw
    save_data()
    refresh_products()
    await state.clear()
    await safe_delete(message)
    await message.answer("✅ Premium emoji muvaffaqiyatli saqlandi!", reply_markup=get_admin_panel_keyboard())


TEXT_GROUPS = {
    "main": [
        ("main_title", "Asosiy menyu sarlavhasi"),
        ("main_trust", "Ishonchli savdo matni"),
        ("main_channel", "Kanal yangiliklari matni"),
        ("main_hint", "Xizmat tanlash matni"),
    ],
    "payment": [
        ("deposit_title", "Hisob to'ldirish sarlavhasi"),
        ("deposit_prompt", "Hisob to'ldirish savoli"),
        ("deposit_minmax", "Minimum / maksimum matni"),
        ("deposit_input", "Miqdor kiritish matni"),
        ("payment_card_label", "Karta yozuvi"),
        ("payment_owner_label", "Karta egasi yozuvi"),
        ("payment_transfer", "To'lov summasi matni"),
        ("payment_done_instruction", "To'lov ko'rsatmasi"),
        ("payment_timer", "5 daqiqalik muddat matni"),
        ("payment_keep_receipt", "Chekni saqlash matni"),
        ("payment_done_button", "To'lov tugmasi"),
        ("payment_cancel_button", "Bekor qilish tugmasi"),
        ("receipt_request", "Chek yuborish oynasi"),
        ("receipt_accepted", "Chek qabul qilindi matni"),
    ],
    "other": [
        ("profile_title", "Profil sarlavhasi"),
        ("language", "Til tugmasi"),
        ("choose_lang", "Til tanlash matni"),
        ("referral_title", "Referal tizimi sarlavhasi"),
        ("contact_text", "Telefon tasdiqlash matni"),
        ("account", "Hisob sarlavhasi"),
        ("balance_label", "Pul balansi yozuvi"),
    ],
}


@dp.callback_query(F.data == "admin_texts")
async def admin_texts_handler(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    b = InlineKeyboardBuilder()
    b.row(p_btn("Asosiy menyu", "text_group_main", "main_title"))
    b.row(p_btn("To'lov oynalari", "text_group_payment", "deposit"))
    b.row(p_btn("Profil / Referal / Sozlamalar", "text_group_other", "settings"))
    b.row(p_btn("Admin Panel", "admin_panel", "back"))
    await callback.message.edit_text("<b>📝 Textlarni o'zgartirish</b>\n\nKerakli bo'limni tanlang:", reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data.in_({"text_group_main", "text_group_payment", "text_group_other"}))
async def text_group_handler(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    group = callback.data.replace("text_group_", "")
    code = lang(callback.from_user.id)
    items = TEXT_GROUPS.get(group, [])
    b = InlineKeyboardBuilder()
    bucket = texts.get(code, {}) if isinstance(texts, dict) else {}
    for key, label in items:
        preview = str(bucket.get(key, "")) if isinstance(bucket, dict) else ""
        preview = preview.replace("\n", " ")
        if len(preview) > 42:
            preview = preview[:39] + "..."
        b.row(types.InlineKeyboardButton(text=f"✏️ {label}", callback_data=f"text_edit_{code}_{key}"))
        b.row(types.InlineKeyboardButton(text=f"  └ {preview}", callback_data=f"text_edit_{code}_{key}"))
    b.row(p_btn("Textlar", "admin_texts", "back"))
    language_name = "O'zbekcha" if code == "uz" else "Русский"
    await callback.message.edit_text(
        f"<b>📝 {language_name} textlari</b>\n\nO'zgartirmoqchi bo'lgan textni tanlang:",
        reply_markup=b.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("text_edit_"))
async def text_edit_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    raw = callback.data.replace("text_edit_", "", 1)
    if "_" not in raw:
        return
    code, key = raw.split("_", 1)
    if code not in ("uz", "ru") or key not in texts.get(code, {}):
        await callback.answer("Text topilmadi!", show_alert=True)
        return
    await state.update_data(text_key=key, text_lang=code)
    current = texts[code][key]
    lang_name = "O'zbekcha" if code == "uz" else "Русский"
    text_content = (
        "<b>📝 Textni tahrirlash</b>\n\n"
        f"Til: <b>{lang_name}</b>\n"
        f"Kalit: <code>{key}</code>\n\n"
        "Hozirgi matn:\n"
        f"<blockquote>{current}</blockquote>\n\n"
        "Yangi textni yuboring:"
    )
    await callback.message.edit_text(text_content, reply_markup=back_main_keyboard(ADMIN_ID))
    await state.set_state(AdminState.waiting_for_text)
    await callback.answer()


@dp.message(AdminState.waiting_for_text)
async def process_new_text(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    value = (message.text or message.caption or "").strip()
    if not value:
        await message.answer("⚠️ Bo'sh text saqlab bo'lmaydi.")
        return
    data = await state.get_data()
    key, code = data.get("text_key"), data.get("text_lang")
    if code not in ("uz", "ru") or key not in texts.get(code, {}):
        await state.clear()
        await message.answer("❌ Text topilmadi.", reply_markup=get_admin_panel_keyboard())
        return
    texts[code][key] = value
    save_data()
    await state.clear()
    await safe_delete(message)
    await message.answer("✅ Text muvaffaqiyatli saqlandi.", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_prices")
async def admin_prices(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text(
        "<b>Narxlarni boshqarish</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=price_group_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("price_group_"))
async def price_group(callback):
    if callback.from_user.id != ADMIN_ID:
        return
    group = callback.data.replace("price_group_", "")
    builder = InlineKeyboardBuilder()

    if group == "stars":
        for key, item in STARS_PRICES.items():
            builder.row(
                p_btn(f"{item['count']} Stars — {money(item['price'])} so'm", f"price_edit_{key}", "stars")
            )
        title = "Stars narxlari"
    elif group == "gifts":
        for key, item in GIFT_PRICES.items():
            builder.row(
                p_btn(item["name"], f"price_edit_{key}", key)
            )
        title = "Gift narxlari"
    elif group == "premium":
        for key, item in PREMIUM_PRICES.items():
            builder.row(
                p_btn(item["name"], f"price_edit_{key}", key)
            )
        title = "Premium narxlari"
    else:
        sell_names = {
            "sell_gift_bear": "Bear", "sell_gift_heart": "Heart", "sell_gift_box": "Box", "sell_gift_rose": "Rose",
            "sell_gift_rocket": "Rocket", "sell_gift_cake": "Cake", "sell_gift_gem": "Gem", "sell_gift_ring": "Ring"
        }
        for key, name in sell_names.items():
            builder.row(
                p_btn(f"{name} — {money(prices['sell_gifts'][key])} so'm", f"price_edit_{key}", key)
            )
        title = "Gift sotish narxlari"

    builder.row(p_btn("Narxlar", "admin_prices", "back"))
    await callback.message.edit_text(f"<b>{title}</b>\n\nO'zgartirmoqchi bo'lgan narxni tanlang:", reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "price_edit_custom_star")
async def edit_custom_star(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.update_data(price_group="custom_star", price_key="custom_star")
    await callback.message.edit_text(
        f"<b>1 Stars narxi</b>\n\nHozirgi narx: <b>{money(prices['custom_star'])} so'm</b>\n\nYangi narxni faqat raqam bilan yozing:",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(AdminState.waiting_for_price)
    await callback.answer()


def find_price_location(key):
    if key.startswith("stars_"):
        return "stars", key.replace("stars_", "")
    for group in ("gifts", "premium", "sell_gifts"):
        if key in prices.get(group, {}):
            return group, key
    return None, None


@dp.callback_query(F.data.startswith("price_edit_"))
async def edit_price(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.replace("price_edit_", "")
    group, real_key = find_price_location(key)
    if not group:
        await callback.answer("Narx topilmadi!", show_alert=True)
        return
    current = prices[group][real_key]
    await state.update_data(price_group=group, price_key=real_key)
    await callback.message.edit_text(
        f"<b>Narxni o'zgartirish</b>\n\nHozirgi narx: <b>{money(current)} so'm</b>\n\nYangi narxni faqat raqam bilan yozing:",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(AdminState.waiting_for_price)
    await callback.answer()


@dp.message(AdminState.waiting_for_price)
async def process_new_price(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqam kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    amount = int(message.text)
    if amount <= 0:
        msg = await message.answer("⚠️ Narx 0 dan katta bo'lishi kerak!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    data = await state.get_data()
    group = data.get("price_group")
    key = data.get("price_key")

    if group == "custom_star":
        prices["custom_star"] = amount
    else:
        prices[group][key] = amount

    save_data()
    refresh_products()
    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ Narx yangilandi!\n\nYangi narx: <b>{money(amount)} so'm</b>", reply_markup=price_group_keyboard())


@dp.callback_query(F.data == "admin_referral_reward")
async def admin_referral_reward_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    current = float(prices.get("referral_reward", 1.5))
    await callback.message.edit_text(
        f"<b>Referal Stars mukofoti</b>\n\nHozirgi mukofot: <b>+{format_stars(current)} Stars</b>\n\nYangi mukofotni kiriting:\nMasalan: <code>2</code> yoki <code>1.5</code>",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(AdminState.waiting_for_referral_reward)
    await callback.answer()


@dp.message(AdminState.waiting_for_referral_reward)
async def process_referral_reward(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    raw = (message.text or "").replace(",", ".").strip()
    try:
        value = float(raw)
    except Exception:
        msg = await message.answer("⚠️ Masalan: <code>1.5</code> yoki <code>2</code>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    if value <= 0:
        msg = await message.answer("⚠️ Mukofot 0 dan katta bo'lishi kerak!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    prices["referral_reward"] = round(value, 2)
    save_data()
    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ Referal mukofoti <b>+{format_stars(value)} Stars</b> qilib saqlandi.", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_user_message")
async def admin_user_message_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("<b>Foydalanuvchiga xabar</b>\n\nTelegram ID raqamini yuboring:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_message_user_id)
    await callback.answer()


@dp.message(AdminState.waiting_for_message_user_id)
async def process_user_message_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat Telegram ID raqamini yuboring.")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    target_id = int(message.text)
    await safe_delete(message)
    await state.update_data(target_user_id=target_id)
    await message.answer(
        f"<b>ID:</b> <code>{target_id}</code>\n\nEndi foydalanuvchiga yubormoqchi bo'lgan xabarni yuboring.",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(AdminState.waiting_for_user_message)


@dp.message(AdminState.waiting_for_user_message)
async def process_user_message(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    target_id = data.get("target_user_id")

    if not target_id:
        await state.clear()
        await message.answer("❌ Foydalanuvchi ID topilmadi.", reply_markup=get_admin_panel_keyboard())
        return

    try:
        await message.copy_to(chat_id=target_id)
        await state.clear()
        await message.answer(f"✅ Xabar <code>{target_id}</code> ga yuborildi.", reply_markup=get_admin_panel_keyboard())
        await safe_delete(message)
    except Exception:
        await state.clear()
        await message.answer("❌ Xabar yuborilmadi.", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_delete_message")
async def admin_delete_message_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("<b>Bot xabarini o'chirish</b>\n\nTelegram ID raqamini yuboring:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_delete_user_id)
    await callback.answer()


@dp.message(AdminState.waiting_for_delete_user_id)
async def process_delete_user_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat Telegram ID raqamini yuboring.")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    target_id = int(message.text)
    await safe_delete(message)
    await state.update_data(delete_user_id=target_id)
    await message.answer(f"<b>Foydalanuvchi:</b> <code>{target_id}</code>\n\nEndi bot xabarining <b>message ID</b> sini yuboring:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_delete_message_id)


@dp.message(AdminState.waiting_for_delete_message_id)
async def process_delete_message_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat message ID raqamini yuboring.")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    data = await state.get_data()
    target_id = data.get("delete_user_id")
    message_id = int(message.text)

    try:
        await bot.delete_message(chat_id=target_id, message_id=message_id)
        await state.clear()
        await message.answer(f"✅ Bot xabari o'chirildi.\n\nID: <code>{target_id}</code> | Message ID: <code>{message_id}</code>", reply_markup=get_admin_panel_keyboard())
        await safe_delete(message)
    except Exception:
        await state.clear()
        await message.answer("❌ Xabarni o'chirib bo'lmadi.", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_check_bal")
async def admin_check_bal_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Foydalanuvchi balansini tekshirish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=builder.as_markup())
    await state.set_state(AdminState.waiting_for_user_id_check)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_check)
async def process_admin_check_user_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqamli Telegram ID kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    target_id = int(message.text)
    await safe_delete(message)
    await state.clear()

    text = (
        f"<blockquote>{custom_tag('balance')}<b>Foydalanuvchi Ma'lumotlari:</b>\n\n"
        f"ID: <code>{target_id}</code>\n"
        f"Pul balansi: <b>{money(get_balance(target_id))} so'm</b>\n"
        f"Referal Stars: <b>{format_stars(get_stars_balance(target_id))} Stars</b>\n"
        f"Referallari: <b>{user_referrals.get(target_id, 0)} ta</b></blockquote>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        p_btn("Balans Qo'shish", f"admin_quick_add_{target_id}", "deposit"),
        p_btn("Balans Ayirish", f"admin_quick_sub_{target_id}", "sell")
    )
    builder.row(p_btn("Admin Panel", "admin_panel", "back"))
    await message.answer(text, reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("admin_quick_add_"))
async def admin_quick_add_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    target_id = int(callback.data.replace("admin_quick_add_", ""))
    await state.update_data(target_user_id=target_id)
    await callback.message.edit_text(f"<b>ID: {target_id}</b>\nQancha so'm qo'shmoqchisiz?", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_amount_add)
    await callback.answer()


@dp.callback_query(F.data.startswith("admin_quick_sub_"))
async def admin_quick_sub_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    target_id = int(callback.data.replace("admin_quick_sub_", ""))
    await state.update_data(target_user_id=target_id)
    await callback.message.edit_text(f"<b>ID: {target_id}</b>\nQancha so'm ayirmoqchisiz?", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_amount_sub)
    await callback.answer()


@dp.callback_query(F.data == "admin_add_bal")
async def admin_add_bal_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("<b>Balans qo'shish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_user_id_add)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_add)
async def process_admin_add_user_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqamli Telegram ID kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return
    target_id = int(message.text)
    await safe_delete(message)
    await state.update_data(target_user_id=target_id)
    await message.answer(f"<b>ID: {target_id}</b>\nQancha so'm qo'shmoqchisiz?", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_amount_add)


@dp.message(AdminState.waiting_for_amount_add)
async def process_admin_add_amount(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqam kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return
    amount = int(message.text)
    data = await state.get_data()
    target_id = data.get("target_user_id")
    update_balance(target_id, amount)
    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ <b>ID: {target_id}</b> ga <b>{money(amount)} so'm</b> qo'shildi!", reply_markup=get_admin_panel_keyboard())
    try:
        await bot.send_message(chat_id=target_id, text=f"{custom_tag('deposit')}Hisobingizga <b>{money(amount)} so'm</b> qo'shildi!")
    except Exception:
        pass


@dp.callback_query(F.data == "admin_sub_bal")
async def admin_sub_bal_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("<b>Balans ayirish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_user_id_sub)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_sub)
async def process_admin_sub_user_id(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqamli Telegram ID kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return
    target_id = int(message.text)
    await safe_delete(message)
    await state.update_data(target_user_id=target_id)
    await message.answer(f"<b>ID: {target_id}</b>\nQancha so'm ayirmoqchisiz?", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_amount_sub)


@dp.message(AdminState.waiting_for_amount_sub)
async def process_admin_sub_amount(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text or not message.text.isdigit():
        msg = await message.answer("⚠️ Faqat raqam kiriting!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return
    amount = int(message.text)
    data = await state.get_data()
    target_id = data.get("target_user_id")
    update_balance(target_id, -amount)
    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ <b>ID: {target_id}</b> dan <b>{money(amount)} so'm</b> ayirildi!", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("<b>Xabar yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring:", reply_markup=back_main_keyboard())
    await state.set_state(AdminState.waiting_for_broadcast)
    await callback.answer()


@dp.message(AdminState.waiting_for_broadcast)
async def process_admin_broadcast(message, state):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    success, failed = 0, 0
    status = await message.answer("⏳ Xabar yuborilmoqda...")

    for uid in list(registered_users):
        try:
            await message.copy_to(chat_id=uid)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await safe_delete(message)
    await status.edit_text(f"<b>Xabar yuborish yakunlandi!</b>\n\n✅ Yuborildi: <b>{success} ta</b>\n❌ Muvaffaqiyatsiz: <b>{failed} ta</b>", reply_markup=get_admin_panel_keyboard())


@dp.message(CommandStart())
async def start_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_languages.setdefault(str(user_id), "uz")
    user_join_dates.setdefault(str(user_id), datetime.now().strftime("%d.%m.%Y"))
    save_data()

    await safe_delete(message)
    await delete_previous_menu(user_id)

    args = command.args
    is_new_user = (user_id not in registered_users)

    if is_new_user:
        registered_users.add(user_id)
        if args and args.isdigit():
            referrer_id = int(args)
            if referrer_id != user_id and referrer_id in registered_users and str(user_id) not in referral_processed:
                referral_pending[str(user_id)] = referrer_id
                save_data()
                contact_kb = ReplyKeyboardBuilder()
                contact_kb.row(types.KeyboardButton(text=tr(user_id, "share_contact"), request_contact=True))
                contact_kb.row(types.KeyboardButton(text=tr(user_id, "refresh")))
                msg = await message.answer(
                    f"<blockquote><b>{tr(user_id,'contact_title')}</b>\n\n{tr(user_id,'contact_text')}</blockquote>",
                    reply_markup=contact_kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
                )
                last_menu_messages[user_id] = msg.message_id
                await state.set_state(ContactState.waiting_for_contact)
                return
        save_data()

    if user_id not in user_balances:
        user_balances[user_id] = 0
        save_data()

    unsub = await check_all_subs(user_id)
    if unsub:
        sub_text = (
            "<blockquote><b>Star Market Uz botdan foydalanish uchun yangiliklar kanaliga obuna bo'ling.</b>\n\n"
            "Kanalga obuna bo'lgach, <b>Obunani tekshirish</b> tugmasini bosing.</blockquote>"
        )
        msg = await message.answer(sub_text, reply_markup=get_sub_keyboard(unsub))
        last_menu_messages[user_id] = msg.message_id
        return

    msg = await message.answer(
        main_menu_text(user_id),
        reply_markup=get_main_inline_menu(user_id)
    )
    last_menu_messages[user_id] = msg.message_id


@dp.message(ContactState.waiting_for_contact, F.contact)
async def referral_contact_handler(message, state):
    phone = message.contact.phone_number if message.contact else ""
    uid = message.from_user.id
    if message.contact and message.contact.user_id and message.contact.user_id != uid:
        await message.answer("❌ O'zingizning telefon raqamingizni yuboring.")
        return
    if not phone_allowed(phone):
        await message.answer(tr(uid, "bad_phone"))
        return
    verified_phones[str(uid)] = phone
    referrer_id = referral_pending.get(str(uid))
    if referrer_id and str(uid) not in referral_processed:
        add_star_referral(referrer_id)
        referral_processed[str(uid)] = True
        referral_pending.pop(str(uid), None)
        reward = float(prices.get("referral_reward", 1.5))
        try:
            await bot.send_message(chat_id=referrer_id, text=f"<blockquote>{custom_tag('referral')}<b>Yangi referal tasdiqlandi!</b>\n\nSizga <b>+{format_stars(reward)} Stars</b> berildi.</blockquote>")
        except Exception:
            pass
    save_data()
    await state.clear()
    await delete_previous_menu(uid)
    await message.answer(tr(uid, "phone_ok"), reply_markup=get_bottom_reply_keyboard(uid))
    
    unsub = await check_all_subs(uid)
    if unsub:
        sub_text = "<blockquote><b>Botdan foydalanish uchun yangiliklar kanaliga obuna bo'ling.</b>\n\nObuna bo'lgach, tekshirish tugmasini bosing.</blockquote>"
        msg = await message.answer(sub_text, reply_markup=get_sub_keyboard(unsub))
    else:
        msg = await message.answer(main_menu_text(uid), reply_markup=get_main_inline_menu(uid))
    last_menu_messages[uid] = msg.message_id


@dp.message(F.text.in_({"Yangilash", "Обновить", "🔄 Yangilash", "🔄 Обновить"}))
async def bottom_refresh_handler(message, state):
    await state.clear()
    user_id = message.from_user.id
    await safe_delete(message)
    await delete_previous_menu(user_id)

    unsub = await check_all_subs(user_id)
    if unsub:
        msg = await message.answer(
            "<blockquote><b>Avval @rymbyvv_otziv kanaliga obuna bo'ling.</b>\n\nObuna bo'lgach, tekshirish tugmasini bosing.</blockquote>",
            reply_markup=get_sub_keyboard(unsub)
        )
        last_menu_messages[user_id] = msg.message_id
        return

    msg = await message.answer(main_menu_text(user_id), reply_markup=get_main_inline_menu(user_id))
    last_menu_messages[user_id] = msg.message_id


@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback):
    user_id = callback.from_user.id
    unsub = await check_all_subs(user_id)
    if not unsub:
        await callback.message.edit_text(
            main_menu_text(user_id),
            reply_markup=get_main_inline_menu(user_id)
        )
        last_menu_messages[user_id] = callback.message.message_id
        await callback.answer("✅ Obuna tasdiqlandi!")
    else:
        await callback.answer("❌ @rymbyvv_otziv kanaliga hali obuna bo'lmagansiz!", show_alert=True)


@dp.callback_query(F.data == "back_main")
async def back_to_main(callback, state):
    await state.clear()
    user_id = callback.from_user.id
    unsub = await check_all_subs(user_id)
    if unsub:
        await callback.message.edit_text(
            "<blockquote><b>Botdan foydalanish uchun @rymbyvv_otziv kanaliga obuna bo'ling.</b></blockquote>",
            reply_markup=get_sub_keyboard(unsub)
        )
    else:
        await callback.message.edit_text(
            main_menu_text(user_id),
            reply_markup=get_main_inline_menu(user_id)
        )
    await callback.answer()


@dp.callback_query(F.data == "cancel")
async def cancel_action(callback, state):
    await state.clear()
    await cancel_user_payment_if_any(callback.from_user.id)
    await callback.message.edit_text(
        main_menu_text(callback.from_user.id),
        reply_markup=get_main_inline_menu(callback.from_user.id)
    )
    await callback.answer("Bekor qilindi.")


@dp.callback_query(F.data == "settings")
async def settings_handler(callback):
    uid = callback.from_user.id
    user = callback.from_user
    joined = user_join_dates.get(str(uid), "Noma'lum" if lang(uid) == "uz" else "Неизвестно")
    uname = f"@{user.username}" if user.username else ("Mavjud emas" if lang(uid) == "uz" else "Нет")

    text = (
        f"<blockquote>{custom_tag('settings')}<b>{tr(uid, 'settings')}</b>\n\n"
        f"Ism: <b>{user.full_name}</b>\n"
        f"ID: <code>{uid}</code>\n"
        f"Username: {uname}\n"
        f"A'zo bo'lingan: {joined}\n"
        f"Til: {'O`zbekcha' if lang(uid) == 'uz' else 'Русский'}\n\n"
        f"{tr(uid, 'choose_lang')}</blockquote>"
    )

    b = InlineKeyboardBuilder()
    b.row(
        p_btn(tr(uid, "russian"), "set_lang_ru", "lang_ru"),
        p_btn(tr(uid, "uzbek"), "set_lang_uz", "lang_uz")
    )
    b.row(p_btn(tr(uid, "back"), "back_main", "back"))
    await callback.message.edit_text(text, reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data.in_({"set_lang_uz", "set_lang_ru"}))
async def set_language_handler(callback):
    uid = callback.from_user.id
    user_languages[str(uid)] = "uz" if callback.data.endswith("uz") else "ru"
    save_data()
    await callback.message.edit_text(
        main_menu_text(uid),
        reply_markup=get_main_inline_menu(uid)
    )
    await callback.answer("✅")


@dp.callback_query(F.data == "top_rating")
async def top_rating_handler(callback):
    uid = callback.from_user.id
    b = InlineKeyboardBuilder()
    b.row(
        p_btn(tr(uid, 'today'), "top_today", "top_today"),
        p_btn(tr(uid, 'week'), "top_week", "top_week")
    )
    b.row(p_btn(tr(uid, 'month'), "top_month", "top_month"))
    b.row(p_btn(tr(uid, "back"), "back_main", "back"))
    await callback.message.edit_text(build_top_text(uid, "today"), reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data.in_({"top_today", "top_week", "top_month"}))
async def top_period_handler(callback):
    uid = callback.from_user.id
    period = callback.data.replace("top_", "")
    b = InlineKeyboardBuilder()
    b.row(
        p_btn(tr(uid, 'today'), "top_today", "top_today"),
        p_btn(tr(uid, 'week'), "top_week", "top_week")
    )
    b.row(p_btn(tr(uid, 'month'), "top_month", "top_month"))
    b.row(p_btn(tr(uid, "back"), "settings", "back"))
    await callback.message.edit_text(build_top_text(uid, period), reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "my_balance")
async def show_balance(callback):
    bal = get_balance(callback.from_user.id)
    text = (
        f"<blockquote>{custom_tag('balance')}<b>Sizning hisobingiz</b>\n\n"
        f"Pul balansi: <b>{money(bal)} so'm</b></blockquote>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Orqaga", "back_main", "back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "referral_system")
async def referral_system_handler(callback):
    user_id = callback.from_user.id
    stars = get_stars_balance(user_id)
    refs = user_referrals.get(user_id, 0)
    reward = float(prices.get("referral_reward", 1.5))
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    text = (
        f"<blockquote>{custom_tag('referral')}<b>{tr(user_id,'referral_title')}</b>\n\n"
        f"<b>Referal havolangiz:</b>\n<code>{ref_link}</code>\n\n"
        f"Taklif qilingan do'stlar soni: <b>{refs} ta</b>\n"
        f"Referal Stars: <b>{format_stars(stars)} Stars</b>\n\n"
        f"Har bir yangi taklif uchun <b>+{format_stars(reward)} Stars</b> beriladi.\n"
        "Minimum yechish: <b>15 Stars</b></blockquote>"
    )

    builder = InlineKeyboardBuilder()
    if stars >= 15:
        builder.row(p_btn(tr(user_id, "withdraw"), "withdraw_stars", "stars"))
    builder.row(p_btn("Orqaga", "back_main", "back"))

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        link_preview_options=types.LinkPreviewOptions(is_disabled=True)
    )
    await callback.answer()


@dp.callback_query(F.data == "withdraw_stars")
async def withdraw_stars_start(callback, state):
    stars = get_stars_balance(callback.from_user.id)
    if stars < 15:
        await callback.answer("❌ Minimal yechib olish 15 Stars!", show_alert=True)
        return

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Stars yechib olish</b>\n\n"
        f"Sizda: <b>{format_stars(stars)} Stars</b> bor.\n\n"
        "Stars o'tkazilishi kerak bo'lgan Telegram username yoki ID raqamini yozing:</blockquote>",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(WithdrawStarsState.waiting_for_username)
    await callback.answer()


@dp.message(WithdrawStarsState.waiting_for_username)
async def process_withdraw_stars(message, state):
    user_id = message.from_user.id
    target_info = (message.text or "").strip()
    stars = get_stars_balance(user_id)

    if stars < 15:
        await safe_delete(message)
        await state.clear()
        await message.answer("<blockquote>❌ Minimal yechib olish 15 Stars!</blockquote>", reply_markup=back_main_keyboard())
        return

    user_stars_balances[user_id] = round(stars - 15, 2)
    save_data()

    await safe_delete(message)
    await state.clear()
    await delete_previous_menu(user_id)

    msg = await message.answer(
        f"<blockquote>{custom_tag('stars')}<b>So'rov qabul qilindi!</b>\n\n15 Stars <b>{target_info}</b> hisobiga tez orada o'tkazib beriladi.</blockquote>",
        reply_markup=back_main_keyboard()
    )
    last_menu_messages[user_id] = msg.message_id

    admin_text = (
        f"<blockquote>{custom_tag('stars')}<b>Stars Yechib Olish So'rovi!</b>\n\n"
        f"Foydalanuvchi: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"ID: <code>{user_id}</code>\n"
        "Stars miqdori: <b>15 Stars</b>\n"
        f"Qabul qiluvchi: <code>{target_info}</code></blockquote>"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text)


async def expire_payment(user_id, payment_id):
    try:
        await asyncio.sleep(300)
        payment = pending_payments.get(payment_id)
        if not payment or payment.get("user_id") != user_id or payment.get("status") != "pending":
            return

        payment["status"] = "expired"
        pending_payments.pop(payment_id, None)
        payment_expiry_tasks.pop(payment_id, None)

        try:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=payment["message_id"],
                text="<blockquote><b>To'lov vaqti tugadi!</b>\n\n5 daqiqa ichida chek yuborilmadi.</blockquote>",
                reply_markup=back_main_keyboard()
            )
        except Exception:
            pass
    except asyncio.CancelledError:
        pass


async def cancel_user_payment_if_any(user_id):
    for payment_id, payment in list(pending_payments.items()):
        if payment.get("user_id") == user_id and payment.get("status") in ["pending", "waiting_admin"]:
            payment["status"] = "cancelled"
            pending_payments.pop(payment_id, None)
            task = payment_expiry_tasks.pop(payment_id, None)
            if task:
                task.cancel()


@dp.callback_query(F.data == "deposit")
async def deposit_start(callback, state):
    deposit_title = editable_text("deposit_title", "Hisob to'ldirish", callback.from_user.id)
    deposit_prompt = editable_text("deposit_prompt", "Hisobingizni qanchaga to'ldirmoqchisiz?", callback.from_user.id)
    deposit_minmax = editable_text("deposit_minmax", "Minimum: <b>1.000 so'm</b>\nMaksimum: <b>22.500 so'm</b>", callback.from_user.id)
    deposit_input = editable_text("deposit_input", "Miqdorni yozing:", callback.from_user.id)
    await callback.message.edit_text(
        f"<blockquote>{custom_tag('deposit')}<b>{deposit_title}</b>\n\n{deposit_prompt}\n\n{deposit_minmax}\n\n{deposit_input}</blockquote>",
        reply_markup=back_main_keyboard(callback.from_user.id)
    )
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()


@dp.message(DepositState.waiting_for_amount)
async def process_deposit_amount(message, state):
    user_id = message.from_user.id

    if not message.text or not message.text.isdigit():
        msg = await message.answer("<blockquote>⚠️ Iltimos, faqat raqam kiriting!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    amount = int(message.text)
    if amount < 1000 or amount > 22500:
        msg = await message.answer(
            "<blockquote>❌ Miqdor 1.000 so'mdan kam yoki 22.500 so'mdan ko'p bo'lmasligi kerak!</blockquote>"
        )
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    await cancel_user_payment_if_any(user_id)

    payment_id = f"{user_id}_{int(datetime.now().timestamp() * 1000)}"

    payment_card_label = editable_text("payment_card_label", "Karta:", user_id)
    payment_owner_label = editable_text("payment_owner_label", "Ega:", user_id)
    payment_transfer = editable_text("payment_transfer", "Kartaga <b>{amount} so'm</b> o'tkazing.", user_id).format(amount=money(amount))
    payment_done_instruction = editable_text("payment_done_instruction", "To'lovni amalga oshirgach, <b>To'lovni amalga oshirdim</b> tugmasini bosing.", user_id)
    payment_timer = editable_text("payment_timer", "Bu oyna <b>5 daqiqa</b> amal qiladi.", user_id)
    payment_keep_receipt = editable_text("payment_keep_receipt", "Chekni saqlab qo'ying.", user_id)

    card_text = (
        f"<blockquote>{custom_tag('deposit')}<b>{payment_card_label}</b> <code>{PAYMENT_CARD}</code>\n"
        f"<b>{payment_owner_label}</b> {PAYMENT_CARD_OWNER}\n\n"
        f"{payment_transfer}\n\n"
        f"{payment_done_instruction}\n\n"
        f"{payment_timer}\n\n"
        f"{payment_keep_receipt}</blockquote>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(p_btn(editable_text("payment_done_button", "To'lovni amalga oshirdim", user_id), f"send_pay_{payment_id}", "payment_done"))
    builder.row(p_btn(editable_text("payment_cancel_button", "Bekor qilish", user_id), "cancel", "cancel"))

    await delete_previous_menu(user_id)
    msg = await message.answer(card_text, reply_markup=builder.as_markup())
    last_menu_messages[user_id] = msg.message_id

    pending_payments[payment_id] = {
        "user_id": user_id,
        "amount": amount,
        "message_id": msg.message_id,
        "status": "pending"
    }

    payment_expiry_tasks[payment_id] = asyncio.create_task(
        expire_payment(user_id, payment_id)
    )
    await state.clear()


@dp.callback_query(F.data.startswith("send_pay_"))
async def send_payment_to_admin(callback, state):
    payment_id = callback.data.replace("send_pay_", "")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("user_id") != callback.from_user.id or payment.get("status") != "pending":
        await callback.answer("⏰ Bu to'lov oynasining muddati tugagan.", show_alert=True)
        return

    payment["status"] = "waiting_receipt"
    await state.update_data(payment_id=payment_id)

    receipt_text = editable_text(
        "receipt_request",
        "<b>To'lov chekini yuboring.</b>\n\nIltimos, to'lov qilganingizni tasdiqlovchi <b>rasm yoki screenshot</b>ni shu yerga yuboring.\n\nChekni 5 daqiqa ichida yuboring.",
        callback.from_user.id
    )
    await callback.message.edit_text(
        f"<blockquote>{custom_tag('deposit')}{receipt_text}</blockquote>",
        reply_markup=back_main_keyboard(callback.from_user.id)
    )
    await state.set_state(DepositState.waiting_for_receipt)
    await callback.answer()


@dp.message(DepositState.waiting_for_receipt)
async def process_deposit_receipt(message, state):
    data = await state.get_data()
    payment_id = data.get("payment_id")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("user_id") != message.from_user.id or payment.get("status") != "waiting_receipt":
        await state.clear()
        await message.answer(
            "<blockquote><b>To'lov vaqti tugagan.</b>\n\nYangi to'lov oynasini ochib, qaytadan urinib ko'ring.</blockquote>",
            reply_markup=back_main_keyboard()
        )
        return

    if not message.photo:
        msg = await message.answer(
            "<blockquote>⚠️ Iltimos, to'lov chekini <b>rasm yoki screenshot</b> ko'rinishida yuboring.</blockquote>"
        )
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    payment["status"] = "waiting_admin"
    task = payment_expiry_tasks.pop(payment_id, None)
    if task:
        task.cancel()

    amount = payment["amount"]
    user_id = message.from_user.id
    username = message.from_user.username or "Mavjud emas"

    try:
        await bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception:
        pass

    admin_builder = InlineKeyboardBuilder()
    admin_builder.row(
        p_btn("Tasdiqlash", f"approve_pay_{payment_id}", "check_btn"),
        p_btn("Rad etish", f"reject_pay_{payment_id}", "cancel")
    )

    admin_text = (
        f"<blockquote>{custom_tag('deposit')}<b>Yangi to'lov + chek!</b>\n\n"
        f"Foydalanuvchi: {message.from_user.full_name}\n"
        f"Username: @{username}\n"
        f"ID: <code>{user_id}</code>\n"
        f"Miqdor: <b>{money(amount)} so'm</b>\n\n"
        "Chek yuqoridagi xabarda.</blockquote>"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=admin_builder.as_markup()
        )
    except Exception:
        payment["status"] = "waiting_receipt"
        msg = await message.answer("<blockquote>⚠️ Chekni adminga yuborishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.</blockquote>")
        await asyncio.sleep(3)
        await safe_delete(msg)
        return

    await state.clear()
    accepted_text = editable_text(
        "receipt_accepted",
        "<b>Chek qabul qilindi!</b>\n\nTo'lovingiz tekshirilmoqda.\n5 daqiqa ichida balansingizga qo'shilmasa,\nadminga murojaat qiling.",
        message.from_user.id
    )
    await message.answer(
        f"<blockquote>{custom_tag('deposit')}{accepted_text}</blockquote>",
        reply_markup=back_main_keyboard(message.from_user.id)
    )


@dp.callback_query(F.data.startswith("approve_pay_"))
async def approve_payment(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Bu tugma faqat admin uchun!", show_alert=True)
        return

    payment_id = callback.data.replace("approve_pay_", "")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("status") != "waiting_admin":
        await callback.answer("❌ To'lov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    user_id = payment["user_id"]
    amount = payment["amount"]
    payment["status"] = "approved"
    pending_payments.pop(payment_id, None)

    update_balance(user_id, amount)

    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ <b>HOLAT:</b> Tasdiqlandi.\nBalansga {money(amount)} so'm qo'shildi."
    )

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"<blockquote>{custom_tag('deposit')}Hisobingizga <b>{money(amount)} so'm</b> qo'shildi!\n\nTo'lovingiz tasdiqlandi.</blockquote>",
            reply_markup=back_main_keyboard(user_id)
        )
    except Exception:
        pass

    await callback.answer("✅ To'lov tasdiqlandi!")


@dp.callback_query(F.data.startswith("reject_pay_"))
async def reject_payment(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Bu tugma faqat admin uchun!", show_alert=True)
        return

    payment_id = callback.data.replace("reject_pay_", "")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("status") != "waiting_admin":
        await callback.answer("❌ To'lov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    user_id = payment["user_id"]
    payment["status"] = "rejected"
    pending_payments.pop(payment_id, None)

    await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>HOLAT:</b> Rad etildi.")

    try:
        await bot.send_message(
            chat_id=user_id,
            text="<blockquote>❌ <b>Hisobni to'ldirish so'rovingiz admin tomonidan rad etildi.</b></blockquote>",
            reply_markup=back_main_keyboard(user_id)
        )
    except Exception:
        pass

    await callback.answer("❌ To'lov rad etildi.")


@dp.callback_query(F.data == "buy_stars")
async def stars_menu(callback):
    builder = InlineKeyboardBuilder()
    for key, data in STARS_PRICES.items():
        builder.add(p_btn(data["name"], f"buyprod_{key}", "stars"))
    builder.adjust(2)
    builder.row(p_btn("Boshqa miqdorda Stars", "custom_stars", "custom_stars"))
    builder.row(p_btn("Orqaga", "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Stars paketini tanlang:</b>\n\nKerakli paketni bosing.</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "custom_stars")
async def custom_stars_start(callback, state):
    one_star_price = prices["custom_star"]
    text = (
        f"<blockquote>{custom_tag('custom_stars')}<b>Boshqa miqdorda Stars olish</b>\n\n"
        f"1 ta Stars narxi: <b>{money(one_star_price)} so'm</b>\n\n"
        "Minimal buyurtma: 50 Stars\n\n"
        "Qancha Stars olmoqchisiz?</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=back_main_keyboard())
    await state.set_state(CustomStarsState.waiting_for_stars_amount)
    await callback.answer()


@dp.message(CustomStarsState.waiting_for_stars_amount)
async def process_custom_stars_amount(message, state):
    user_id = message.from_user.id
    if not message.text or not message.text.isdigit():
        msg = await message.answer("<blockquote>⚠️ Iltimos, faqat raqam kiriting!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    count = int(message.text)
    if count < 50:
        msg = await message.answer("<blockquote>⚠️ <b>Minimal buyurtma — 50 Stars!</b>\n\nKamida 50 Stars kiriting.</blockquote>")
        await asyncio.sleep(3)
        await safe_delete(msg)
        return

    if count > 10000:
        msg = await message.answer("<blockquote>❌ Maksimal miqdor 10.000 Stars.</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    total_price = int(count * prices["custom_star"])

    product = {
        "name": f"{count} Stars - {money(total_price)} so'm",
        "formatted": f"{custom_tag('stars')}<b>{count} Stars</b> - {money(total_price)} so'm",
        "price": total_price,
        "count": count
    }

    await state.update_data(prod_key=f"custom_stars_{count}", product=product)

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("O'zimning profilimga", "target_self", "profile"))
    builder.row(p_btn("Boshqa profilga", "target_other", "target_other"))
    builder.row(p_btn("Orqaga", "buy_stars", "back"))

    if get_balance(user_id) < total_price:
        text = (
            f"<blockquote>{custom_tag('stars')}<b>Stars buyurtmasi</b>\n\n"
            f"Mahsulot: <b>{count} Stars</b>\n"
            f"Narxi: <b>{money(total_price)} so'm</b>\n\n"
            "⚠️ <b>Hisobingizda mablag' yetarli emas.</b>\nAvval hisobingizni to'ldiring.</blockquote>"
        )
        builder = InlineKeyboardBuilder()
        builder.row(p_btn("Hisob to'ldirish", "deposit", "deposit"))
        builder.row(p_btn("Orqaga", "buy_stars", "back"))
        await state.clear()
    else:
        text = (
            f"<blockquote>{custom_tag('stars')}<b>Mahsulot:</b> {product['formatted']}\n"
            f"<b>Narxi:</b> {money(total_price)} so'm\n\n"
            "Qaysi profilga olmoqchisiz?</blockquote>"
        )

    await delete_previous_menu(user_id)
    msg = await message.answer(text, reply_markup=builder.as_markup())
    last_menu_messages[user_id] = msg.message_id


@dp.callback_query(F.data == "buy_gift")
async def gift_menu(callback):
    builder = InlineKeyboardBuilder()
    for key, data in GIFT_PRICES.items():
        builder.add(p_btn(data["name"], f"buyprod_{key}", key))
    builder.adjust(2)
    builder.row(p_btn("Orqaga", "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('gift')}<b>Gift olish</b>\n\nKerakli Giftni tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


SELL_GIFT_INFO = {
    "sell_gift_bear": "Bear", "sell_gift_heart": "Heart", "sell_gift_box": "Box", "sell_gift_rose": "Rose",
    "sell_gift_rocket": "Rocket", "sell_gift_cake": "Cake", "sell_gift_gem": "Gem", "sell_gift_ring": "Ring"
}


@dp.callback_query(F.data == "sell_gift_menu")
async def sell_gift_start(callback):
    builder = InlineKeyboardBuilder()
    for key, name in SELL_GIFT_INFO.items():
        builder.add(
            p_btn(f"{name} — {money(prices['sell_gifts'][key])} so'm", key, key)
        )
    builder.adjust(2)
    builder.row(p_btn("Orqaga", "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('sell')}<b>Qaysi giftni sotmoqchisiz?</b></blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("sell_gift_"))
async def process_gift_choice(call, state):
    key = call.data
    if key not in SELL_GIFT_INFO:
        await call.answer()
        return

    gift_name = SELL_GIFT_INFO[key]
    price = f"{money(prices['sell_gifts'][key])} so'm"
    await state.update_data(gift_name=gift_name, price=price)
    text = (
        f"<blockquote>{custom_tag('sell')}Siz <b>{gift_name}</b> sotishni tanladingiz.\n"
        f"Narxi: <b>{price}</b>\n\n"
        f"Giftni quyidagi profilga yuboring: {ADMIN_USERNAME}\n"
        "So'ngra gift yuborilganligi haqidagi chek (skrinshot)ni shu botga yuboring.</blockquote>"
    )
    await call.message.edit_text(text, reply_markup=back_main_keyboard())
    await state.set_state(GiftProcess.waiting_for_receipt)
    await call.answer()


@dp.message(GiftProcess.waiting_for_receipt)
async def process_receipt(message, state):
    if not message.photo:
        msg = await message.answer("<blockquote>⚠️ Iltimos, chekni rasm yoki screenshot ko'rinishida yuboring.</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await state.update_data(receipt_msg_id=message.message_id)
    await message.answer(
        f"<blockquote>{custom_tag('deposit')}Plastik karta raqamingizni yozing:\n<i>(16 xonali karta raqami)</i></blockquote>",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(GiftProcess.waiting_for_card_details)


@dp.message(GiftProcess.waiting_for_card_details)
async def process_card_details(message, state):
    card_raw = re.sub(r"\D", "", message.text or "")
    if len(card_raw) != 16:
        msg = await message.answer("<blockquote>⚠️ <b>Xatolik!</b>\n\n16 xonali karta raqamini kiriting.</blockquote>")
        await asyncio.sleep(3)
        await safe_delete(msg)
        return

    formatted_card = f"{card_raw[:4]} {card_raw[4:8]} {card_raw[8:12]} {card_raw[12:]}"
    data = await state.get_data()
    await safe_delete(message)
    await message.answer("<blockquote>To'lov amalga oshirilmoqda, sabr qiling...</blockquote>")

    admin_text = (
        f"<blockquote>{custom_tag('sell')}<b>Foydalanuvchi gift sotdi!</b>\n\n"
        f"Foydalanuvchi: <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> (@{message.from_user.username or 'yoq'})\n"
        f"Gift: <b>{data['gift_name']}</b>\n"
        f"Summa: <b>{data['price']}</b>\n"
        f"Karta: <code>{formatted_card}</code></blockquote>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("To'lov amalga oshirildi", f"pay_done_{message.from_user.id}_{data['price']}", "check_btn"))

    try:
        await bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=data["receipt_msg_id"]
        )
    except Exception:
        pass

    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=builder.as_markup())
    await state.clear()


@dp.callback_query(F.data.startswith("pay_done_"))
async def confirm_payment_sell(call):
    parts = call.data.split("_")
    user_id = int(parts[2])

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"<blockquote>{custom_tag('deposit')}Pulingiz muvaffaqiyatli kartangizga tushdi, savdo uchun rahmat!</blockquote>"
        )
        await call.message.edit_text(
            call.message.text + "\n\n<blockquote>✅ <b>To'lov tasdiqlandi va foydalanuvchiga xabar berildi.</b></blockquote>"
        )
    except Exception:
        await call.answer("Xatolik yuz berdi.", show_alert=True)
        return

    await call.answer("✅ To'lov tasdiqlandi!")


@dp.callback_query(F.data == "buy_premium")
async def premium_menu(callback):
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Profilga kirmasdan (Avto)", "prem_auto_menu", "prem_auto"))
    builder.row(p_btn("Profilga kirib (Admin orqali)", "prem_admin_menu", "prem_admin"))
    builder.row(p_btn("Orqaga", "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Premium olish</b>\n\nPremium berish usulini tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "prem_auto_menu")
async def premium_auto_menu(callback):
    builder = InlineKeyboardBuilder()
    for key in ("prem_3", "prem_6", "prem_12"):
        data = PREMIUM_PRICES[key]
        builder.row(p_btn(data["name"], f"buyprod_{key}", key))
    builder.row(p_btn("Orqaga", "buy_premium", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Avtomatik Premium</b>\n\nKerakli muddatni tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "prem_admin_menu")
async def premium_admin_menu(callback):
    data = PREMIUM_PRICES["prem_1"]
    builder = InlineKeyboardBuilder()
    builder.row(p_btn(data["name"], "buyprod_prem_1", "prem_1"))
    builder.row(p_btn("Orqaga", "buy_premium", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Admin orqali Premium</b>\n\nPaketni tanlang.</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("buyprod_"))
async def select_product(callback, state):
    prod_key = callback.data.split("buyprod_", 1)[1]
    product = ALL_PRODUCTS.get(prod_key)

    if not product:
        await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
        return

    user_id = callback.from_user.id
    if get_balance(user_id) < product["price"]:
        builder = InlineKeyboardBuilder()
        builder.row(p_btn("Hisob to'ldirish", "deposit", "deposit"))
        builder.row(p_btn("Orqaga", "back_main", "back"))

        await callback.message.edit_text(
            f"<blockquote>⚠️ <b>Hisobingizda mablag' yetarli emas.</b>\n\n"
            f"<b>Mahsulot:</b> {product['formatted']}\n"
            f"<b>Narxi:</b> {money(product['price'])} so'm\n"
            f"Balansingiz: <b>{money(get_balance(user_id))} so'm</b></blockquote>",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return

    await state.update_data(prod_key=prod_key, product=product)

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("O'zimning profilimga", "target_self", "profile"))
    builder.row(p_btn("Boshqa profilga", "target_other", "target_other"))
    builder.row(p_btn("Orqaga", "back_main", "back"))

    text = (
        f"<blockquote><b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Narxi:</b> {money(product['price'])} so'm\n\n"
        "Qaysi profilga olmoqchisiz?</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "target_self")
async def target_self_handler(callback, state):
    username = callback.from_user.username
    target = f"@{username}" if username else f"ID: {callback.from_user.id}"
    await state.update_data(target=target)
    await confirm_purchase_menu(callback, state)


@dp.callback_query(F.data == "target_other")
async def target_other_handler(callback, state):
    await callback.message.edit_text(
        "<blockquote><b>Boshqa profilga yuborish</b>\n\nFoydalanuvchi username'ini yuboring:\n(Masalan: @username)</blockquote>",
        reply_markup=back_main_keyboard()
    )
    await state.set_state(BuyState.waiting_for_target)
    await callback.answer()


@dp.message(BuyState.waiting_for_target)
async def process_target_username(message, state):
    target = (message.text or "").strip()
    if not target.startswith("@") and not target.isdigit():
        msg = await message.answer("<blockquote>⚠️ To'g'ri username yuboring (Masalan: @username)!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    await state.update_data(target=target)
    await confirm_purchase_menu_msg(message, state)


async def confirm_purchase_menu(callback, state):
    data = await state.get_data()
    product = data.get("product")
    target = data.get("target")

    if not product or not target:
        await callback.answer("❌ Ma'lumot topilmadi.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Xaridni tasdiqlash", "confirm_buy", "confirm_buy"))
    builder.row(p_btn("Bekor qilish", "cancel", "cancel"))

    text = (
        f"<blockquote><b>Xaridni tasdiqlang:</b>\n\n"
        f"<b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Narxi:</b> {money(product['price'])} so'm\n"
        f"<b>Qabul qiluvchi:</b> {target}</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


async def confirm_purchase_menu_msg(message, state):
    data = await state.get_data()
    product = data.get("product")
    target = data.get("target")

    if not product or not target:
        await state.clear()
        await message.answer("❌ Ma'lumot topilmadi.", reply_markup=back_main_keyboard())
        return

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Xaridni tasdiqlash", "confirm_buy", "confirm_buy"))
    builder.row(p_btn("Bekor qilish", "cancel", "cancel"))

    text = (
        f"<blockquote><b>Xaridni tasdiqlang:</b>\n\n"
        f"<b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Narxi:</b> {money(product['price'])} so'm\n"
        f"<b>Qabul qiluvchi:</b> {target}</blockquote>"
    )
    await delete_previous_menu(message.from_user.id)
    msg = await message.answer(text, reply_markup=builder.as_markup())
    last_menu_messages[message.from_user.id] = msg.message_id


@dp.callback_query(F.data == "confirm_buy")
async def execute_purchase(callback, state):
    user_id = callback.from_user.id
    data = await state.get_data()
    product = data.get("product")
    target = data.get("target")

    if not product or not target:
        await callback.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring!", show_alert=True)
        return

    price = int(product["price"])
    if get_balance(user_id) < price:
        await callback.answer("❌ Hisobingizda yetarli mablag' yo'q!", show_alert=True)
        return

    update_balance(user_id, -price)
    await state.clear()

    order_id = f"{user_id}_{int(datetime.now().timestamp() * 1000)}"
    active_orders[order_id] = {
        "user_id": user_id,
        "user_name": callback.from_user.full_name,
        "username": callback.from_user.username or "yoq",
        "product_name": product["name"],
        "product_formatted": product["formatted"],
        "price": price,
        "target": target
    }

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"<b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Qabul qiluvchi:</b> {target}\n\n"
        "Tez orada buyurtmangiz bajariladi. Rahmat!</blockquote>",
        reply_markup=back_main_keyboard()
    )

    admin_builder = InlineKeyboardBuilder()
    admin_builder.row(
        p_btn("Tasdiqlash", f"ord_done_{order_id}", "check_btn"),
        p_btn("Bekor qilish", f"ord_cancel_{order_id}", "cancel")
    )

    admin_text = (
        f"<blockquote><b>Yangi buyurtma!</b>\n\n"
        f"Xaridor: {callback.from_user.full_name} (@{callback.from_user.username or 'yoq'})\n"
        f"ID: <code>{user_id}</code>\n"
        f"Mahsulot: {product['name']}\n"
        f"Narxi: {money(price)} so'm\n"
        f"Qabul qiluvchi: {target}</blockquote>"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_builder.as_markup())
    await callback.answer("✅ Buyurtma qabul qilindi!")


@dp.callback_query(F.data.startswith("ord_done_"))
async def admin_order_done(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = callback.data.replace("ord_done_", "")
    order_info = active_orders.get(order_id)
    await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>HOLAT:</b> Tasdiqlandi va bajarildi.")

    if order_info:
        user_id = order_info["user_id"]
        purchase_history.append({
            "time": datetime.now().isoformat(),
            "user_id": user_id,
            "name": order_info.get("user_name", str(user_id)),
            "price": int(order_info.get("price", 0)),
            "product": order_info.get("product_name", "")
        })
        save_data()

        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"<blockquote><b>Buyurtmangiz muvaffaqiyatli bajarildi!</b>\n\n"
                    f"{order_info['product_formatted']}\n"
                    f"Qabul qiluvchi: <b>{order_info['target']}</b></blockquote>"
                ),
                reply_markup=back_main_keyboard(user_id)
            )
        except Exception:
            pass

        active_orders.pop(order_id, None)

    await callback.answer("✅ Buyurtma tasdiqlandi!")


@dp.callback_query(F.data.startswith("ord_cancel_"))
async def admin_order_cancel(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = callback.data.replace("ord_cancel_", "")
    order_info = active_orders.get(order_id)
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>HOLAT:</b> Bekor qilindi va pul qaytarildi.")

    if order_info:
        user_id = order_info["user_id"]
        price = order_info["price"]
        update_balance(user_id, price)

        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"<blockquote>❌ Buyurtmangiz bekor qilindi. Hisobingizga <b>{money(price)} so'm</b> qaytarildi.</blockquote>",
                reply_markup=back_main_keyboard(user_id)
            )
        except Exception:
            pass

        active_orders.pop(order_id, None)

    await callback.answer("Bekor qilindi va pul qaytarildi!")


async def dummy_handler(request):
    return web.Response(text="Bot ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", dummy_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

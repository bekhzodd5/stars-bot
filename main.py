import asyncio
import json
import logging
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta

import aiohttp  # pyrefly: ignore [missing-import]
from aiohttp import web  # pyrefly: ignore [missing-import]
from aiogram import Bot, Dispatcher, F, types  # pyrefly: ignore [missing-import]
from aiogram.client.default import DefaultBotProperties  # pyrefly: ignore [missing-import]
from aiogram.enums import ParseMode  # pyrefly: ignore [missing-import]
from aiogram.filters import CommandObject, CommandStart  # pyrefly: ignore [missing-import]
from aiogram.fsm.context import FSMContext  # pyrefly: ignore [missing-import]
from aiogram.fsm.state import State, StatesGroup  # pyrefly: ignore [missing-import]
from aiogram.fsm.storage.memory import MemoryStorage  # pyrefly: ignore [missing-import]
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder  # pyrefly: ignore [missing-import]


BOT_TOKEN = os.getenv("BOT_TOKEN", "8982437206:AAEdeSgZluIOS7SnDXSfFGqT8MuNlAglJz0")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. Serverda BOT_TOKEN environment variable o‘rnating."
    )

ADMIN_ID = 7414653407
ADMIN_USERNAME = "@rymbyvv"
SUB_CHANNELS = ["@rymbyvv_otziv"]
DATA_FILE = "bot_database.json"

PAYMENT_CARD = os.getenv("PAYMENT_CARD") or "9860 3566 3465 1745"
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER") or "Elvira.k"

# ==============================================================================
# 🌟 TELEGRAM BOT - PREMIUM CUSTOM EMOJI ID-LARI (ANIQ QATORLAR):
# O'zingizning Custom Emoji ID raqamlaringizni quyidagi qatorlarga qo'ying:
# ==============================================================================
DEFAULT_MENU_EMOJIS = {
    # 📌 ASOSIY MENYU TUGMALARI (Tugmalar oldidagi emojilar):
    "deposit": "4972482444025398275",     # Hisob to'ldirish tugmasi
    "stars": "5269623953898357794",       # Stars olish tugmasi
    "gift": "5458488840022933066",        # Gift olish tugmasi
    "premium": "5461082978794880873",     # Premium olish tugmasi
    "balance": "4965219701572503640",     # Hisobim tugmasi
    "sell": "5460641176983976678",        # Gift sotish tugmasi
    "referral": "5460997461701050139",    # Referal tizimi tugmasi
    "top": "5409008750893734809",         # Top reyting tugmasi
    "settings": "4967490064234840998",    # Sozlamalar tugmasi
    "admin": "5864197326318342099",       # Admin (Aloqa) tugmasi

    # 📌 ASOSIY MENYU XABARI MATNIDAGI EMOJILAR (Xabar ichida):
    "main_title": "5008248651038852115",  # "Asosiy menyu" sarlavhasi yonidagi emoji
    "main_trust": "5460947592835778324",  # "Biz bilan ishonchli savdo..." yonidagi emoji
    "main_channel": "5461137215641895106",# "Kanalimizni kuzatib boring..." yonidagi emoji
    "main_hint": "5271998448042785916",   # "Kerakli xizmatni tanlang..." yonidagi emoji

    # 📌 QO'SHIMCHA TUGMALAR:
    "back": "5271599436991052462",        # Orqaga tugmasi emojisi
    "cancel": "5316660455744223443",      # Bekor qilish tugmasi emojisi
    "check_btn": "5316827280863934685",   # To'lovni tekshirish tugmasi emojisi
    "sent_btn": "5316827280863934685",    # Sovg'a yubordim / Tashladim tugmasi emojisi

    # 🎁 SOVG'ALARNING ALOHIDA PREMIUM EMOJI ID-LARI:
    "gift_15_1": "5823511762548301106",   # Ayiqcha (Teddy Bear)
    "gift_15_2": "5823504508348537997",   # Yurakcha (Heart)
    "gift_25_1": "5823675916198354199",   # Qizil Atirgul (Rose)
    "gift_25_2": "5825844101588720291",   # Syurpriz quti (Gift Box)
    "gift_50_1": "5823675916198354199",   # Lola guldastasi (Tulips)
    "gift_50_2": "5825442788434517646",   # Kosmik Raketa (Rocket)
    "gift_50_3": "5825603677909424544",   # Tug'ilgan kun torti (Cake)
    "gift_50_4": "5823279086990006647",   # Shampan vinosi (Champagne)
    "gift_100_1": "5823653586663382347",  # Oltin Kubok (Trophy)
    "gift_100_2": "5823337017508895058",  # Moviy Olmos (Diamond)
    "gift_100_3": "5823622048718527510",  # Brilliant Uzuk (Ring)

    # 💰 GIFT SOTISH ALOHIDA PREMIUM EMOJI ID-LARI:
    "sell_gift_ayiqcha": "5823511762548301106",
    "sell_gift_yurak": "5823504508348537997",
    "sell_gift_atirgul": "5823675916198354199",
    "sell_gift_quti": "5825844101588720291",
    "sell_gift_lola": "5823675916198354199",
    "sell_gift_raketa": "5825442788434517646",
    "sell_gift_tort": "5825603677909424544",
    "sell_gift_shampan": "5823279086990006647",
    "sell_gift_kubok": "5823653586663382347",
    "sell_gift_olmos": "5823337017508895058",
    "sell_gift_yuzuk": "5823622048718527510",
}

# ==============================================================================
# PAYHAMYON TO'LOV TIZIMI (PAYMENT GATEWAY) SOZLAMALARI
# ==============================================================================
DEFAULT_SHOP_ID = int(os.getenv("PAYHAMYON_SHOP_ID", "121"))
DEFAULT_SHOP_KEY = os.getenv("PAYHAMYON_SHOP_KEY", "Gqjap69EFBHO15IBuWl8xAig6QpGunx")
DEFAULT_BASE_URL = os.getenv("PAYHAMYON_BASE_URL", "https://user91.hostx.uz").rstrip("/")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())


def get_payhamyon_config():
    """Hozirgi PayHamyon kassa sozlamalarini olish (baza yoki standart)"""
    cfg = db.get("payhamyon", {}) if "db" in globals() and isinstance(db, dict) else {}
    shop_id = cfg.get("shop_id", DEFAULT_SHOP_ID)
    shop_key = cfg.get("shop_key", DEFAULT_SHOP_KEY)
    base_url = cfg.get("base_url", DEFAULT_BASE_URL)
    try:
        shop_id = int(shop_id)
    except Exception:
        shop_id = DEFAULT_SHOP_ID
    return shop_id, str(shop_key).strip(), str(base_url).strip().rstrip("/")


def send_request(url, payload):
    """HTTP POST so'rov jo'natuvchi yordamchi funksiya (sinxron)"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode("utf-8"))
        except Exception:
            return {"success": False, "error": f"http_error_{exc.code}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_shop_info(shop_id=None, shop_key=None, base_url=None):
    """Kassa ma'lumotlari, faollik holati va to'lov limitlarini olish (sinxron)"""
    cfg_id, cfg_key, cfg_url = get_payhamyon_config()
    s_id = shop_id if shop_id is not None else cfg_id
    s_key = shop_key if shop_key is not None else cfg_key
    b_url = (base_url if base_url is not None else cfg_url).rstrip("/")
    return send_request(f"{b_url}/api/shop/info", {
        "shop_id": int(s_id),
        "shop_key": str(s_key).strip(),
    })


def create_payment(amount, callback_url=None, shop_id=None, shop_key=None, base_url=None):
    """Yangi to'lov hisobi (chek) yaratish (sinxron)"""
    cfg_id, cfg_key, cfg_url = get_payhamyon_config()
    s_id = shop_id if shop_id is not None else cfg_id
    s_key = shop_key if shop_key is not None else cfg_key
    b_url = (base_url if base_url is not None else cfg_url).rstrip("/")
    payload = {
        "shop_id": int(s_id),
        "shop_key": str(s_key).strip(),
        "amount": int(amount),
    }
    if callback_url:
        payload["callback_url"] = str(callback_url).strip()
    return send_request(f"{b_url}/api/payment/create", payload)


def check_payment(token, shop_id=None, shop_key=None, base_url=None):
    """To'lov holatini tekshirish (sinxron)"""
    cfg_id, cfg_key, cfg_url = get_payhamyon_config()
    s_id = shop_id if shop_id is not None else cfg_id
    s_key = shop_key if shop_key is not None else cfg_key
    b_url = (base_url if base_url is not None else cfg_url).rstrip("/")
    return send_request(f"{b_url}/api/payment/check", {
        "shop_id": int(s_id),
        "shop_key": str(s_key).strip(),
        "token": str(token).strip(),
    })


def cancel_payment(token, shop_id=None, shop_key=None, base_url=None):
    """To'lovni bekor qilish (sinxron)"""
    cfg_id, cfg_key, cfg_url = get_payhamyon_config()
    s_id = shop_id if shop_id is not None else cfg_id
    s_key = shop_key if shop_key is not None else cfg_key
    b_url = (base_url if base_url is not None else cfg_url).rstrip("/")
    return send_request(f"{b_url}/api/payment/cancel", {
        "shop_id": int(s_id),
        "shop_key": str(s_key).strip(),
        "token": str(token).strip(),
    })


# Asinxron HTTP so'rovlar (aiogram event-loop ni bloklamaydi)
async def async_payhamyon_request(endpoint, payload):
    shop_id, shop_key, base_url = get_payhamyon_config()
    full_payload = {
        "shop_id": int(shop_id),
        "shop_key": str(shop_key).strip(),
    }
    full_payload.update(payload)
    url = f"{base_url}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=full_payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                text = await resp.text()
                try:
                    return json.loads(text)
                except Exception:
                    return {"success": False, "error": f"Invalid server response (HTTP {resp.status})"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


async def async_get_shop_info():
    return await async_payhamyon_request("/api/shop/info", {})


async def async_create_payment(amount, callback_url=None):
    payload = {"amount": int(amount)}
    if callback_url:
        payload["callback_url"] = str(callback_url).strip()
    return await async_payhamyon_request("/api/payment/create", payload)


async def async_check_payment(token):
    return await async_payhamyon_request("/api/payment/check", {"token": str(token).strip()})


async def async_cancel_payment(token):
    return await async_payhamyon_request("/api/payment/cancel", {"token": str(token).strip()})


# ==============================================================================
# BAZA VA STANDART QIYMATLAR
# ==============================================================================
def default_prices():
    return {
        "stars": {
            "50": 12500,
            "100": 22500,
            "150": 38000,
            "200": 40000,
            "250": 55000,
            "300": 65000,
            "350": 75000,
            "400": 85000,
            "500": 95000,
            "750": 142500,
            "1000": 190000,
        },
        "gifts": {
            "gift_15_1": 3500,
            "gift_15_2": 3500,
            "gift_25_1": 6500,
            "gift_25_2": 6500,
            "gift_50_1": 10500,
            "gift_50_2": 10500,
            "gift_50_3": 10500,
            "gift_50_4": 10500,
            "gift_100_1": 20000,
            "gift_100_2": 20000,
            "gift_100_3": 20000,
            "gift_13_1": 3500,
            "gift_13_2": 3500,
            "gift_21_1": 6500,
            "gift_21_2": 6500,
            "gift_43_1": 10500,
            "gift_43_2": 10500,
            "gift_85_1": 20000,
            "gift_85_2": 20000
        },
        "premium": {
            "prem_1": 45000,
            "prem_3": 155000,
            "prem_6": 210000,
            "prem_12": 285000,
            "prem_12_gift": 385000
        },
        "sell_gifts": {
            "sell_gift_ayiqcha": 1500,
            "sell_gift_yurak": 1500,
            "sell_gift_atirgul": 2500,
            "sell_gift_quti": 2500,
            "sell_gift_lola": 4500,
            "sell_gift_raketa": 4500,
            "sell_gift_tort": 4500,
            "sell_gift_shampan": 4500,
            "sell_gift_kubok": 9000,
            "sell_gift_olmos": 9000,
            "sell_gift_yuzuk": 9000,
            "sell_gift_bear": 1500,
            "sell_gift_heart": 1500,
            "sell_gift_rose": 2500,
            "sell_gift_box": 2500,
            "sell_gift_rocket": 4500,
            "sell_gift_cake": 4500,
            "sell_gift_gem": 9000,
            "sell_gift_ring": 9000
        },
        "custom_star": 225,
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
                "deposit_minmax": "Minimum: <b>1.000 so'm</b>\nMaksimum: <b>100.000 so'm</b>",
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
                "deposit_minmax": "Минимум: <b>1.000 сум</b>\nМаксимум: <b>100.000 сум</b>",
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
                "active_orders": data.get("active_orders", {}),
                "pending_payments": data.get("pending_payments", {}),
                "pending_auto_payments": data.get("pending_auto_payments", {}),
                "sell_orders": data.get("sell_orders", {}),
                "withdraw_requests": data.get("withdraw_requests", {}),
                "payhamyon": data.get("payhamyon", {
                    "shop_id": DEFAULT_SHOP_ID,
                    "shop_key": DEFAULT_SHOP_KEY,
                    "base_url": DEFAULT_BASE_URL
                }),
                "texts": defaults["texts"],
                "prices": defaults
            }
        except Exception as e:
            logging.error(f"Faylni yuklashda xatolik: {e}")

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
        "active_orders": {},
        "pending_payments": {},
        "pending_auto_payments": {},
        "sell_orders": {},
        "withdraw_requests": {},
        "payhamyon": {
            "shop_id": DEFAULT_SHOP_ID,
            "shop_key": DEFAULT_SHOP_KEY,
            "base_url": DEFAULT_BASE_URL
        },
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
for k, v in DEFAULT_MENU_EMOJIS.items():
    if k not in menu_emojis:
        menu_emojis[k] = v
db["menu_emojis"] = menu_emojis
texts = db.get("texts", default_prices()["texts"])
prices = db["prices"]

active_orders = db.get("active_orders", {})
pending_payments = db.get("pending_payments", {})
pending_auto_payments = db.get("pending_auto_payments", {})
sell_orders = db.get("sell_orders", {})
withdraw_requests = db.get("withdraw_requests", {})

last_menu_messages = {}
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

class GiftSellState(StatesGroup):
    waiting_for_card_number = State()

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
    waiting_for_payhamyon_shop_id = State()
    waiting_for_payhamyon_shop_key = State()
    waiting_for_payhamyon_base_url = State()


def save_data():
    """Xavfsiz atomik tarzda ma'lumotlarni saqlash"""
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
        "active_orders": active_orders,
        "pending_payments": pending_payments,
        "pending_auto_payments": pending_auto_payments,
        "sell_orders": sell_orders,
        "withdraw_requests": withdraw_requests,
        "payhamyon": db.get("payhamyon", {
            "shop_id": DEFAULT_SHOP_ID,
            "shop_key": DEFAULT_SHOP_KEY,
            "base_url": DEFAULT_BASE_URL
        }),
        "texts": texts,
        "prices": prices
    }
    try:
        tmp_file = f"{DATA_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_file, DATA_FILE)
    except Exception as e:
        logging.error(f"Saqlashda xatolik: {e}")


def money(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)

def format_stars(value):
    try:
        return f"{float(value):g}"
    except Exception:
        return str(value)

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
        "balance_text": "Sizning hisobingiz", "current_balance": "Pul balansi:",
        "auto_pay": "⚡️ Avto to'lov (PayHamyon)", "manual_pay": "💳 Qo'lda to'lov (Chek orqali)",
        "check_pay": "🔄 To'lovni tekshirish", "cancel_pay": "❌ Bekor qilish",
        "choose_pay_method": "To'lov usulini tanlang:"
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
        "balance_text": "Ваш счёт", "current_balance": "Баланс:",
        "auto_pay": "⚡️ Авто-оплата (PayHamyon)", "manual_pay": "💳 Ручная оплата (Через чек)",
        "check_pay": "🔄 Проверить оплату", "cancel_pay": "❌ Отменить",
        "choose_pay_method": "Выберите способ оплаты:"
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
    eid = menu_emojis.get(key) or DEFAULT_MENU_EMOJIS.get(key)
    return f'<tg-emoji emoji-id="{eid}">✨</tg-emoji> ' if eid else ''

def p_btn(text, cb, key):
    eid = menu_emojis.get(key) or DEFAULT_MENU_EMOJIS.get(key)
    if not eid and str(key).startswith("gift_"):
        eid = menu_emojis.get("gift") or DEFAULT_MENU_EMOJIS.get("gift")
    if not eid and str(key).startswith("sell_gift_"):
        eid = menu_emojis.get("sell") or DEFAULT_MENU_EMOJIS.get("sell")
    return types.InlineKeyboardButton(text=text, callback_data=cb, icon_custom_emoji_id=eid if eid else None)

def p_url_btn(text, url, key):
    eid = menu_emojis.get(key) or DEFAULT_MENU_EMOJIS.get(key)
    return types.InlineKeyboardButton(text=text, url=url, icon_custom_emoji_id=eid if eid else None)

def phone_allowed(phone):
    digits = re.sub(r"\D", "", phone or "")
    return digits.startswith("998") or digits.startswith("7")

def top_period_start(period):
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
    uid_str = str(user_id)
    bal = user_balances.get(uid_str)
    if bal is None and isinstance(user_id, int):
        bal = user_balances.get(user_id)
    if bal is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "data", "database.json")
        if not os.path.exists(db_path):
            db_path = os.path.join("data", "database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    web_db = json.load(f)
                u = web_db.get("users", {}).get(uid_str)
                if u and "balance" in u:
                    bal = u["balance"]
                    user_balances[uid_str] = bal
                    save_data()
            except Exception:
                pass
    return bal if bal is not None else 0

def update_balance(user_id, amount):
    uid_str = str(user_id)
    new_bal = get_balance(user_id) + amount
    user_balances[uid_str] = new_bal
    save_data()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "database.json")
    if not os.path.exists(db_path):
        db_path = os.path.join("data", "database.json")
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                web_db = json.load(f)
            if "users" not in web_db:
                web_db["users"] = {}
            if uid_str in web_db["users"]:
                web_db["users"][uid_str]["balance"] = new_bal
            else:
                web_db["users"][uid_str] = {
                    "id": uid_str,
                    "first_name": "Foydalanuvchi",
                    "username": "",
                    "balance": new_bal,
                    "created_at": datetime.now().isoformat()
                }
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(web_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error syncing balance to web_db: {e}")

def get_stars_balance(user_id):
    return user_stars_balances.get(user_id, 0.0)

def add_star_referral(user_id):
    reward = float(prices.get("referral_reward", 1.5))
    user_stars_balances[user_id] = round(get_stars_balance(user_id) + reward, 2)
    user_referrals[user_id] = user_referrals.get(user_id, 0) + 1
    save_data()


def build_products():
    stars = {}
    star_items = [
        (50, 12500),
        (100, 22500),
        (150, 38000),
        (200, 40000),
        (250, 55000),
        (300, 65000),
        (350, 75000),
        (400, 85000),
        (500, 95000),
        (750, 142500),
        (1000, 190000)
    ]
    configured_stars = {}
    if "stars" in prices and isinstance(prices["stars"], dict):
        for k, v in prices["stars"].items():
            if str(k).isdigit():
                try:
                    configured_stars[int(k)] = int(v)
                except Exception:
                    pass

    if not configured_stars:
        configured_stars = {count: default_p for count, default_p in star_items}

    for s in sorted(configured_stars.keys()):
        p = configured_stars[s]
        stars[f"stars_{s}"] = {
            "name": f"{s} Stars - {money(p)} so'm",
            "formatted": f"{custom_tag('stars')}<b>{s} Stars</b> - {money(p)} so'm",
            "price": int(p),
            "count": s
        }

    gifts_info = {
        "gift_15_1": (15, "Ayiqcha"),
        "gift_15_2": (15, "Yurakcha"),
        "gift_25_1": (25, "Qizil Atirgul"),
        "gift_25_2": (25, "Syurpriz quti"),
        "gift_50_1": (50, "Lola guldastasi"),
        "gift_50_2": (50, "Kosmik Raketa"),
        "gift_50_3": (50, "Tug'ilgan kun torti"),
        "gift_50_4": (50, "Shampan"),
        "gift_100_1": (100, "Oltin Kubok"),
        "gift_100_2": (100, "Moviy Olmos"),
        "gift_100_3": (100, "Brilliant Uzuk")
    }

    gifts = {}
    for key, (count, name) in gifts_info.items():
        p = prices["gifts"].get(key, 0)
        gifts[key] = {
            "name": f"{name} - {money(p)} so'm",
            "formatted": f"{custom_tag(key)}<b>{name}</b> ({count} ⭐) - {money(p)} so'm",
            "price": int(p),
            "title": name,
            "stars_count": count
        }

    premium_names = {
        "prem_1": "1 Oylik Premium",
        "prem_3": "3 Oylik Premium",
        "prem_6": "6 Oylik Premium",
        "prem_12": "1 Yillik Premium (Akkauntga kirib)",
        "prem_12_gift": "1 Yillik Premium (Sovg'a tariqasida)"
    }

    premium = {}
    for key, title in premium_names.items():
        p = prices["premium"].get(key, 0)
        premium[key] = {
            "name": f"{title} - {money(p)} so'm",
            "formatted": f"{custom_tag(key)}<b>{title}</b> - {money(p)} so'm",
            "price": int(p),
            "title": title
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
            err_msg = str(e).lower()
            if "member list is inaccessible" in err_msg or "chat not found" in err_msg or "bot was kicked" in err_msg:
                logging.warning(f"Bot {channel} kanalida admin emas! Obunani tekshirish uchun botni kanalda admin qiling.")
                continue
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
        p_btn("⚙️ Admin Panel", "admin_panel", "back")
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
        builder.row(p_btn("⚡️ Admin Panel", "admin_panel", "settings"))
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
    builder.row(p_btn("⚡️ PayHamyon Kassa", "admin_payhamyon", "deposit"))
    builder.row(p_btn("Narxlarni boshqarish", "admin_prices", "custom_stars"))
    builder.row(p_btn("Premium Emoji boshqarish", "admin_emojis", "premium"))
    builder.row(p_btn("Textlarni o'zgartirish", "admin_texts", "settings"))
    builder.row(
        p_btn("Referal mukofoti", "admin_referral_reward", "referral"),
        p_btn("Foydalanuvchiga xabar", "admin_user_message", "admin")
    )
    builder.row(p_btn("Bot xabarini o'chirish", "admin_delete_message", "cancel"))
    builder.row(p_btn("Xabar Yuborish (Broadcast)", "admin_broadcast", "channel_btn"))
    builder.row(p_btn("Bosh Menyu", "back_main", "back"))
    return builder.as_markup()


# ==============================================================================
# ADMIN PANEL: ASOSIY & SOZLAMALAR
# ==============================================================================
@dp.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: types.CallbackQuery, state: FSMContext):
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
async def admin_stats_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    total_money = sum(user_balances.values())
    total_stars = sum(user_stars_balances.values())
    text = (
        f"<blockquote>{custom_tag('top')}<b>Bot Statistikasi:</b>\n\n"
        f"Barcha foydalanuvchilar: <b>{len(registered_users)} ta</b>\n"
        f"Umumiy balans: <b>{money(total_money)} so'm</b>\n"
        f"Umumiy referal Stars: <b>{format_stars(total_stars)} Stars</b>\n"
        f"Faol buyurtmalar: <b>{len(active_orders)} ta</b>\n"
        f"Kutilayotgan to'lovlar: <b>{len(pending_payments) + len(pending_auto_payments)} ta</b></blockquote>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Admin Panel", "admin_panel", "back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


# ==============================================================================
# ADMIN PANEL: PAYHAMYON KASSA BOSHQARUVI
# ==============================================================================
@dp.callback_query(F.data == "admin_payhamyon")
async def admin_payhamyon_menu(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    s_id, s_key, b_url = get_payhamyon_config()
    masked_key = (s_key[:4] + "..." + s_key[-4:]) if len(s_key) > 8 else s_key
    text = (
        f"<blockquote>{custom_tag('deposit')}<b>⚡️ PayHamyon Avto To'lov Sozlamalari</b>\n\n"
        f"🏪 <b>Shop ID:</b> <code>{s_id}</code>\n"
        f"🔑 <b>Shop Key:</b> <code>{masked_key}</code>\n"
        f"🌐 <b>Base URL:</b> <code>{b_url}</code>\n\n"
        "Kassa holatini tekshirish yoki parametrlarni o'zgartirish uchun tugmalardan foydalaning.</blockquote>"
    )
    b = InlineKeyboardBuilder()
    b.row(p_btn("🔄 Kassa holatini tekshirish", "admin_payhamyon_check", "check_btn"))
    b.row(p_btn("✏️ Shop ID ni o'zgartirish", "admin_payhamyon_edit_shop_id", "settings"))
    b.row(p_btn("✏️ Shop Key ni o'zgartirish", "admin_payhamyon_edit_shop_key", "settings"))
    b.row(p_btn("✏️ Base URL ni o'zgartirish", "admin_payhamyon_edit_base_url", "settings"))
    b.row(p_btn("Admin Panel", "admin_panel", "back"))

    await callback.message.edit_text(text, reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "admin_payhamyon_check")
async def admin_payhamyon_check_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer("⏳ Kassa tekshirilmoqda...")
    info = await async_get_shop_info()
    s_id, s_key, b_url = get_payhamyon_config()

    if info.get("success"):
        shop_data = info.get("data") or info
        title = shop_data.get("name") or shop_data.get("shop_name") or f"Kassa #{s_id}"
        balance = shop_data.get("balance", "Noma'lum")
        status = shop_data.get("status", "Faol")
        min_amount = shop_data.get("min_amount", 1000)
        max_amount = shop_data.get("max_amount", "Cheklovsiz")

        res_text = (
            f"<blockquote>✅ <b>PayHamyon Kassa Faol!</b>\n\n"
            f"Kassa: <b>{title}</b>\n"
            f"Holat: <b>{status}</b>\n"
            f"Kassa balansi: <b>{money(balance) if str(balance).isdigit() else balance}</b>\n"
            f"Minimal to'lov: <b>{money(min_amount) if str(min_amount).isdigit() else min_amount} so'm</b>\n"
            f"Maksimal to'lov: <b>{money(max_amount) if str(max_amount).isdigit() else max_amount} so'm</b></blockquote>"
        )
    else:
        err = info.get("error", "Noma'lum xatolik")
        res_text = (
            f"<blockquote>❌ <b>Kassa bilan bog'lanishda xatolik!</b>\n\n"
            f"Shop ID: <code>{s_id}</code>\n"
            f"Base URL: <code>{b_url}</code>\n"
            f"Xatolik: <code>{err}</code>\n\n"
            "Shop Key yoki Shop ID to'g'ri kiritilganligini tekshiring.</blockquote>"
        )

    b = InlineKeyboardBuilder()
    b.row(p_btn("Ortga", "admin_payhamyon", "back"))
    await callback.message.edit_text(res_text, reply_markup=b.as_markup())


@dp.callback_query(F.data == "admin_payhamyon_edit_shop_id")
async def admin_payhamyon_edit_shop_id_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    s_id, _, _ = get_payhamyon_config()
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_payhamyon", "cancel"))
    await callback.message.edit_text(
        f"<b>Shop ID ni o'zgartirish</b>\n\nHozirgi Shop ID: <code>{s_id}</code>\n\nYangi raqamli Shop ID ni yuboring:",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_payhamyon_shop_id)
    await callback.answer()


@dp.message(AdminState.waiting_for_payhamyon_shop_id)
async def process_payhamyon_shop_id(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = (message.text or "").strip()
    if not text.isdigit():
        msg = await message.answer("⚠️ Iltimos, faqat raqam kiriting (masalan: 1)!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    new_id = int(text)
    if "payhamyon" not in db or not isinstance(db["payhamyon"], dict):
        db["payhamyon"] = {}
    db["payhamyon"]["shop_id"] = new_id
    save_data()

    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ PayHamyon Shop ID muvaffaqiyatli saqlandi: <code>{new_id}</code>", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_payhamyon_edit_shop_key")
async def admin_payhamyon_edit_shop_key_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_payhamyon", "cancel"))
    await callback.message.edit_text(
        "<b>Shop Key ni o'zgartirish</b>\n\nYangi Shop Key ni yuboring:\n<i>(PayHamyon kabinetingizdagi maxfiy kalit)</i>",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_payhamyon_shop_key)
    await callback.answer()


@dp.message(AdminState.waiting_for_payhamyon_shop_key)
async def process_payhamyon_shop_key(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = (message.text or "").strip()
    if len(text) < 5:
        msg = await message.answer("⚠️ Shop Key juda qisqa!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    if "payhamyon" not in db or not isinstance(db["payhamyon"], dict):
        db["payhamyon"] = {}
    db["payhamyon"]["shop_key"] = text
    save_data()

    await safe_delete(message)
    await state.clear()
    await message.answer("✅ PayHamyon Shop Key muvaffaqiyatli saqlandi!", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_payhamyon_edit_base_url")
async def admin_payhamyon_edit_base_url_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    _, _, b_url = get_payhamyon_config()
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_payhamyon", "cancel"))
    await callback.message.edit_text(
        f"<b>Base URL ni o'zgartirish</b>\n\nHozirgi URL: <code>{b_url}</code>\n\nYangi API URL ni yuboring (masalan: <code>https://user91.hostx.uz</code>):",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_payhamyon_base_url)
    await callback.answer()


@dp.message(AdminState.waiting_for_payhamyon_base_url)
async def process_payhamyon_base_url(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = (message.text or "").strip().rstrip("/")
    if not text.startswith("http"):
        msg = await message.answer("⚠️ URL http:// yoki https:// bilan boshlanishi kerak!")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    if "payhamyon" not in db or not isinstance(db["payhamyon"], dict):
        db["payhamyon"] = {}
    db["payhamyon"]["base_url"] = text
    save_data()

    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ PayHamyon Base URL saqlandi: <code>{text}</code>", reply_markup=get_admin_panel_keyboard())


# ==============================================================================
# ADMIN PANEL: PREMIUM EMOJILAR BOSHQARUVI
# ==============================================================================
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
        ("prem_12", "Premium (1 yil - Kirib)"),
        ("prem_12_gift", "Premium (1 yil - Sovg'a)"),
    ],
    "cat_gifts": [
        ("gift_15_1", "Gift: 🧸 Ayiqcha (15 ⭐)"),
        ("gift_15_2", "Gift: 💖 Yurakcha (15 ⭐)"),
        ("gift_25_1", "Gift: 🌹 Qizil Atirgul (25 ⭐)"),
        ("gift_25_2", "Gift: 🎁 Syurpriz quti (25 ⭐)"),
        ("gift_50_1", "Gift: 💐 Lola guldastasi (50 ⭐)"),
        ("gift_50_2", "Gift: 🚀 Kosmik Raketa (50 ⭐)"),
        ("gift_50_3", "Gift: 🎂 Tug'ilgan kun torti (50 ⭐)"),
        ("gift_50_4", "Gift: 🍾 Shampan (50 ⭐)"),
        ("gift_100_1", "Gift: 🏆 Oltin Kubok (100 ⭐)"),
        ("gift_100_2", "Gift: 💎 Moviy Olmos (100 ⭐)"),
        ("gift_100_3", "Gift: 💍 Brilliant Uzuk (100 ⭐)"),
        ("sell_gift_ayiqcha", "Gift sotish: 🧸 Ayiqcha"),
        ("sell_gift_yurak", "Gift sotish: 💖 Yurakcha"),
        ("sell_gift_atirgul", "Gift sotish: 🌹 Qizil Atirgul"),
        ("sell_gift_quti", "Gift sotish: 🎁 Syurpriz quti"),
        ("sell_gift_lola", "Gift sotish: 💐 Lola"),
        ("sell_gift_raketa", "Gift sotish: 🚀 Raketa"),
        ("sell_gift_tort", "Gift sotish: 🎂 Tort"),
        ("sell_gift_shampan", "Gift sotish: 🍾 Shampan"),
        ("sell_gift_kubok", "Gift sotish: 🏆 Oltin Kubok"),
        ("sell_gift_olmos", "Gift sotish: 💎 Moviy Olmos"),
        ("sell_gift_yuzuk", "Gift sotish: 💍 Brilliant Uzuk"),
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
async def admin_emojis_categories(callback: types.CallbackQuery, state: FSMContext):
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
async def admin_emojis_list(callback: types.CallbackQuery, state: FSMContext):
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
async def emoji_edit_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.replace("emoji_edit_", "")
    await state.update_data(emoji_key=key)
    curr_id = menu_emojis.get(key, "Mavjud emas")
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_emojis", "cancel"))
    await callback.message.edit_text(
        f"<b>🎨 Tugma:</b> <code>{key}</code>\n\n"
        f"Hozirgi Premium Emoji ID: <code>{curr_id}</code>\n\n"
        "Yangi custom emoji ID ni yuboring.\n"
        "O'chirib tashlash uchun <code>0</code> yuboring.",
        reply_markup=b.as_markup()
    )
    await state.set_state(EmojiState.waiting_for_id)
    await callback.answer()


@dp.message(EmojiState.waiting_for_id)
async def emoji_edit_save(message: types.Message, state: FSMContext):
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


# ==============================================================================
# ADMIN PANEL: TEXTLARNI BOSHQARISH
# ==============================================================================
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
async def admin_texts_handler(callback: types.CallbackQuery, state: FSMContext):
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
async def text_group_handler(callback: types.CallbackQuery, state: FSMContext):
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
async def text_edit_start(callback: types.CallbackQuery, state: FSMContext):
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
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_texts", "cancel"))
    await callback.message.edit_text(text_content, reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_text)
    await callback.answer()


@dp.message(AdminState.waiting_for_text)
async def process_new_text(message: types.Message, state: FSMContext):
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


# ==============================================================================
# ADMIN PANEL: NARXLARNI BOSHQARISH
# ==============================================================================
@dp.callback_query(F.data == "admin_prices")
async def admin_prices(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text(
        "<b>Narxlarni boshqarish</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=price_group_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("price_group_"))
async def price_group(callback: types.CallbackQuery):
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
        active_sell_keys = [
            "sell_gift_ayiqcha", "sell_gift_yurak",
            "sell_gift_atirgul", "sell_gift_quti",
            "sell_gift_lola", "sell_gift_raketa",
            "sell_gift_tort", "sell_gift_shampan",
            "sell_gift_kubok", "sell_gift_olmos", "sell_gift_yuzuk"
        ]
        for key in active_sell_keys:
            name = SELL_GIFT_INFO.get(key, key)
            builder.row(
                p_btn(f"{name} — {money(prices['sell_gifts'].get(key, 0))} so'm", f"price_edit_{key}", key)
            )
        title = "Gift sotish narxlari"

    builder.row(p_btn("Narxlar", "admin_prices", "back"))
    await callback.message.edit_text(f"<b>{title}</b>\n\nO'zgartirmoqchi bo'lgan narxni tanlang:", reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "price_edit_custom_star")
async def edit_custom_star(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.update_data(price_group="custom_star", price_key="custom_star")
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_prices", "cancel"))
    await callback.message.edit_text(
        f"<b>1 Stars narxi</b>\n\nHozirgi narx: <b>{money(prices['custom_star'])} so'm</b>\n\nYangi narxni faqat raqam bilan yozing:",
        reply_markup=b.as_markup()
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
async def edit_price(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.replace("price_edit_", "")
    group, real_key = find_price_location(key)
    if not group:
        await callback.answer("Narx topilmadi!", show_alert=True)
        return
    current = prices[group][real_key]
    await state.update_data(price_group=group, price_key=real_key)
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_prices", "cancel"))
    await callback.message.edit_text(
        f"<b>Narxni o'zgartirish</b>\n\nHozirgi narx: <b>{money(current)} so'm</b>\n\nYangi narxni faqat raqam bilan yozing:",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_price)
    await callback.answer()


@dp.message(AdminState.waiting_for_price)
async def process_new_price(message: types.Message, state: FSMContext):
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
    elif group and key:
        prices[group][key] = amount

    save_data()
    refresh_products()
    await safe_delete(message)
    await state.clear()
    await message.answer(f"✅ Narx yangilandi!\n\nYangi narx: <b>{money(amount)} so'm</b>", reply_markup=price_group_keyboard())


@dp.callback_query(F.data == "admin_referral_reward")
async def admin_referral_reward_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    current = float(prices.get("referral_reward", 1.5))
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text(
        f"<b>Referal Stars mukofoti</b>\n\nHozirgi mukofot: <b>+{format_stars(current)} Stars</b>\n\nYangi mukofotni kiriting:\nMasalan: <code>2</code> yoki <code>1.5</code>",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_referral_reward)
    await callback.answer()


@dp.message(AdminState.waiting_for_referral_reward)
async def process_referral_reward(message: types.Message, state: FSMContext):
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


# ==============================================================================
# ADMIN PANEL: FOYDALANUVCHILAR VA BALANS BOSHQARUVI
# ==============================================================================
@dp.callback_query(F.data == "admin_user_message")
async def admin_user_message_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Foydalanuvchiga xabar</b>\n\nTelegram ID raqamini yuboring:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_message_user_id)
    await callback.answer()


@dp.message(AdminState.waiting_for_message_user_id)
async def process_user_message_id(message: types.Message, state: FSMContext):
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
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await message.answer(
        f"<b>ID:</b> <code>{target_id}</code>\n\nEndi foydalanuvchiga yubormoqchi bo'lgan xabarni yuboring.",
        reply_markup=b.as_markup()
    )
    await state.set_state(AdminState.waiting_for_user_message)


@dp.message(AdminState.waiting_for_user_message)
async def process_user_message(message: types.Message, state: FSMContext):
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
    except Exception as e:
        await state.clear()
        await message.answer(f"❌ Xabar yuborilmadi: {e}", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_delete_message")
async def admin_delete_message_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Bot xabarini o'chirish</b>\n\nTelegram ID raqamini yuboring:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_delete_user_id)
    await callback.answer()


@dp.message(AdminState.waiting_for_delete_user_id)
async def process_delete_user_id(message: types.Message, state: FSMContext):
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
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await message.answer(f"<b>Foydalanuvchi:</b> <code>{target_id}</code>\n\nEndi bot xabarining <b>message ID</b> sini yuboring:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_delete_message_id)


@dp.message(AdminState.waiting_for_delete_message_id)
async def process_delete_message_id(message: types.Message, state: FSMContext):
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
    except Exception as e:
        await state.clear()
        await message.answer(f"❌ Xabarni o'chirib bo'lmadi: {e}", reply_markup=get_admin_panel_keyboard())


@dp.callback_query(F.data == "admin_check_bal")
async def admin_check_bal_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Foydalanuvchi balansini tekshirish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=builder.as_markup())
    await state.set_state(AdminState.waiting_for_user_id_check)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_check)
async def process_admin_check_user_id(message: types.Message, state: FSMContext):
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
async def admin_quick_add_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    target_id = int(callback.data.replace("admin_quick_add_", ""))
    await state.update_data(target_user_id=target_id)
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text(f"<b>ID: {target_id}</b>\nQancha so'm qo'shmoqchisiz?", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_amount_add)
    await callback.answer()


@dp.callback_query(F.data.startswith("admin_quick_sub_"))
async def admin_quick_sub_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    target_id = int(callback.data.replace("admin_quick_sub_", ""))
    await state.update_data(target_user_id=target_id)
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text(f"<b>ID: {target_id}</b>\nQancha so'm ayirmoqchisiz?", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_amount_sub)
    await callback.answer()


@dp.callback_query(F.data == "admin_add_bal")
async def admin_add_bal_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Balans qo'shish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_user_id_add)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_add)
async def process_admin_add_user_id(message: types.Message, state: FSMContext):
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
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await message.answer(f"<b>ID: {target_id}</b>\nQancha so'm qo'shmoqchisiz?", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_amount_add)


@dp.message(AdminState.waiting_for_amount_add)
async def process_admin_add_amount(message: types.Message, state: FSMContext):
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
async def admin_sub_bal_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Balans ayirish</b>\n\nFoydalanuvchi ID raqamini kiriting:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_user_id_sub)
    await callback.answer()


@dp.message(AdminState.waiting_for_user_id_sub)
async def process_admin_sub_user_id(message: types.Message, state: FSMContext):
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
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await message.answer(f"<b>ID: {target_id}</b>\nQancha so'm ayirmoqchisiz?", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_amount_sub)


@dp.message(AdminState.waiting_for_amount_sub)
async def process_admin_sub_amount(message: types.Message, state: FSMContext):
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
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    b.row(p_btn("Bekor qilish", "admin_panel", "cancel"))
    await callback.message.edit_text("<b>Xabar yuborish (Broadcast)</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yuboring:", reply_markup=b.as_markup())
    await state.set_state(AdminState.waiting_for_broadcast)
    await callback.answer()


@dp.message(AdminState.waiting_for_broadcast)
async def process_admin_broadcast(message: types.Message, state: FSMContext):
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


# ==============================================================================
# USER HANDLERS: START, TIL VA REFERAL TIZIMI
# ==============================================================================
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
async def referral_contact_handler(message: types.Message, state: FSMContext):
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
async def bottom_refresh_handler(message: types.Message, state: FSMContext):
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
async def check_sub_callback(callback: types.CallbackQuery):
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
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
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
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cancel_user_payment_if_any(callback.from_user.id)
    await callback.message.edit_text(
        main_menu_text(callback.from_user.id),
        reply_markup=get_main_inline_menu(callback.from_user.id)
    )
    await callback.answer("Bekor qilindi.")


@dp.callback_query(F.data == "settings")
async def settings_handler(callback: types.CallbackQuery):
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
async def set_language_handler(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user_languages[str(uid)] = "uz" if callback.data.endswith("uz") else "ru"
    save_data()
    await callback.message.edit_text(
        main_menu_text(uid),
        reply_markup=get_main_inline_menu(uid)
    )
    await callback.answer("✅")


@dp.callback_query(F.data == "top_rating")
async def top_rating_handler(callback: types.CallbackQuery):
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
async def top_period_handler(callback: types.CallbackQuery):
    uid = callback.from_user.id
    period = callback.data.replace("top_", "")
    b = InlineKeyboardBuilder()
    b.row(
        p_btn(tr(uid, 'today'), "top_today", "top_today"),
        p_btn(tr(uid, 'week'), "top_week", "top_week")
    )
    b.row(p_btn(tr(uid, 'month'), "top_month", "top_month"))
    b.row(p_btn(tr(uid, "back"), "top_rating", "back"))
    await callback.message.edit_text(build_top_text(uid, period), reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "my_balance")
async def show_balance(callback: types.CallbackQuery):
    uid = callback.from_user.id
    bal = get_balance(uid)
    stars_bal = get_stars_balance(uid)
    title = tr(uid, "balance_text")
    label = tr(uid, "current_balance")
    text = (
        f"<blockquote>{custom_tag('balance')}<b>{title}</b>\n\n"
        f"{label} <b>{money(bal)} so'm</b>\n"
        f"Referal Stars: <b>{format_stars(stars_bal)} Stars</b></blockquote>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(p_btn(tr(uid, "deposit"), "deposit", "deposit"))
    builder.row(p_btn(tr(uid, "back"), "back_main", "back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "referral_system")
async def referral_system_handler(callback: types.CallbackQuery):
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
    builder.row(p_btn(tr(user_id, "back"), "back_main", "back"))

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        link_preview_options=types.LinkPreviewOptions(is_disabled=True)
    )
    await callback.answer()


@dp.callback_query(F.data == "withdraw_stars")
async def withdraw_stars_start(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    stars = get_stars_balance(uid)
    if stars < 15:
        await callback.answer("❌ Minimal yechib olish 15 Stars!", show_alert=True)
        return

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Stars yechib olish</b>\n\n"
        f"Sizda: <b>{format_stars(stars)} Stars</b> bor.\n\n"
        "Stars o'tkazilishi kerak bo'lgan Telegram username yoki ID raqamini yozing:</blockquote>",
        reply_markup=back_main_keyboard(uid)
    )
    await state.set_state(WithdrawStarsState.waiting_for_username)
    await callback.answer()


@dp.message(WithdrawStarsState.waiting_for_username)
async def process_withdraw_stars(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    target_info = (message.text or "").strip()
    stars = get_stars_balance(user_id)

    if stars < 15:
        await safe_delete(message)
        await state.clear()
        await message.answer("<blockquote>❌ Minimal yechib olish 15 Stars!</blockquote>", reply_markup=back_main_keyboard(user_id))
        return

    user_stars_balances[user_id] = round(stars - 15, 2)
    withdraw_id = f"wd_{user_id}_{int(datetime.now().timestamp() * 1000)}"
    withdraw_requests[withdraw_id] = {
        "user_id": user_id,
        "user_name": message.from_user.full_name,
        "username": message.from_user.username or "yoq",
        "stars": 15,
        "target": target_info,
        "status": "pending"
    }
    save_data()

    await safe_delete(message)
    await state.clear()
    await delete_previous_menu(user_id)

    msg = await message.answer(
        f"<blockquote>{custom_tag('stars')}<b>So'rov qabul qilindi!</b>\n\n15 Stars <b>{target_info}</b> hisobiga tez orada o'tkazib beriladi.</blockquote>",
        reply_markup=back_main_keyboard(user_id)
    )
    last_menu_messages[user_id] = msg.message_id

    admin_builder = InlineKeyboardBuilder()
    admin_builder.row(
        p_btn("Tasdiqlash (Bajarildi)", f"wd_done_{withdraw_id}", "check_btn"),
        p_btn("Rad etish (Qaytarish)", f"wd_cancel_{withdraw_id}", "cancel")
    )

    admin_text = (
        f"<blockquote>{custom_tag('stars')}<b>Stars Yechib Olish So'rovi!</b>\n\n"
        f"Foydalanuvchi: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"ID: <code>{user_id}</code>\n"
        "Stars miqdori: <b>15 Stars</b>\n"
        f"Qabul qiluvchi: <code>{target_info}</code></blockquote>"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_builder.as_markup())


@dp.callback_query(F.data.startswith("wd_done_"))
async def admin_withdraw_done(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return
    wd_id = callback.data.replace("wd_done_", "")
    req = withdraw_requests.get(wd_id)
    if not req or req.get("status") != "pending":
        await callback.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    req["status"] = "done"
    save_data()
    await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>HOLAT:</b> Tasdiqlandi (Stars o'tkazildi).")
    try:
        await bot.send_message(
            chat_id=req["user_id"],
            text=f"<blockquote>✅ <b>15 Stars</b> hisobingizga muvaffaqiyatli o'tkazildi! Qabul qiluvchi: {req['target']}</blockquote>",
            reply_markup=back_main_keyboard(req["user_id"])
        )
    except Exception:
        pass
    await callback.answer("✅ Tasdiqlandi!")


@dp.callback_query(F.data.startswith("wd_cancel_"))
async def admin_withdraw_cancel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return
    wd_id = callback.data.replace("wd_cancel_", "")
    req = withdraw_requests.get(wd_id)
    if not req or req.get("status") != "pending":
        await callback.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    user_id = req["user_id"]
    req["status"] = "cancelled"
    user_stars_balances[user_id] = round(get_stars_balance(user_id) + 15, 2)
    save_data()

    await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>HOLAT:</b> Rad etildi va 15 Stars qaytarildi.")
    try:
        await bot.send_message(
            chat_id=user_id,
            text="<blockquote>❌ Stars yechib olish so'rovingiz rad etildi. <b>15 Stars</b> hisobingizga qaytarildi.</blockquote>",
            reply_markup=back_main_keyboard(user_id)
        )
    except Exception:
        pass
    await callback.answer("Bekor qilindi va Stars qaytarildi.")


# ==============================================================================
# DEPOSIT (HISOB TO'LDIRISH) VA TO'LOV TIZIMI
# ==============================================================================
async def expire_payment(user_id, payment_id):
    try:
        await asyncio.sleep(300)
        payment = pending_payments.get(payment_id)
        if not payment or payment.get("user_id") != user_id or payment.get("status") != "pending":
            return

        payment["status"] = "expired"
        pending_payments.pop(payment_id, None)
        payment_expiry_tasks.pop(payment_id, None)
        save_data()

        try:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=payment["message_id"],
                text="<blockquote><b>To'lov vaqti tugadi!</b>\n\n5 daqiqa ichida chek yuborilmadi.</blockquote>",
                reply_markup=back_main_keyboard(user_id)
            )
        except Exception:
            pass
    except asyncio.CancelledError:
        pass


async def cancel_user_payment_if_any(user_id):
    # Faqat hali to'lanmagan (pending / waiting_receipt) to'lovlarni bekor qilamiz
    # Admin tekshiruviga o'tgan (waiting_admin) to'lovlar bekor qilinmaydi!
    for payment_id, payment in list(pending_payments.items()):
        if payment.get("user_id") == user_id and payment.get("status") in ["pending", "waiting_receipt"]:
            payment["status"] = "cancelled"
            pending_payments.pop(payment_id, None)
            task = payment_expiry_tasks.pop(payment_id, None)
            if task:
                task.cancel()
    save_data()


@dp.callback_query(F.data == "deposit")
async def deposit_start(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    deposit_title = editable_text("deposit_title", "Hisob to'ldirish", uid)
    deposit_prompt = editable_text("deposit_prompt", "Hisobingizni qanchaga to'ldirmoqchisiz?", uid)
    deposit_minmax = editable_text("deposit_minmax", "Minimum: <b>1.000 so'm</b>\nMaksimum: <b>10.000.000 so'm</b>", uid)
    deposit_input = editable_text("deposit_input", "Miqdorni yozing:", uid)
    await callback.message.edit_text(
        f"<blockquote>{custom_tag('deposit')}<b>{deposit_title}</b>\n\n{deposit_prompt}\n\n{deposit_minmax}\n\n{deposit_input}</blockquote>",
        reply_markup=back_main_keyboard(uid)
    )
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()


@dp.message(DepositState.waiting_for_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not message.text or not message.text.isdigit():
        msg = await message.answer("<blockquote>⚠️ Iltimos, faqat raqam kiriting!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    amount = int(message.text)
    if amount < 1000 or amount > 100000:
        msg = await message.answer(
            "<blockquote>❌ Miqdor 1.000 so'mdan kam yoki 100.000 so'mdan ko'p bo'lmasligi kerak!</blockquote>"
        )
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    await state.clear()
    await delete_previous_menu(user_id)

    status_msg = await message.answer("⏳ Avto to'lov cheki yaratilmoqda, kuting...")

    # PayHamyon API orqali avto to'lov hisobi yaratish
    res = await async_create_payment(amount=amount)

    if not res.get("success"):
        err = res.get("error", "Noma'lum xatolik")
        b = InlineKeyboardBuilder()
        b.row(p_btn("Orqaga", "deposit", "back"))

        await status_msg.edit_text(
            f"<blockquote>⚠️ <b>Avto to'lov tizimida vaqtinchalik xatolik yuz berdi.</b>\n"
            f"Xatolik tafsiloti: <code>{err}</code>\n\n"
            "Hisobingizni Qo'lda to'lov (Karta + Chek) orqali to'ldirishingiz mumkin.</blockquote>",
            reply_markup=b.as_markup()
        )
        last_menu_messages[user_id] = status_msg.message_id
        return

    token = res.get("token")
    pay_amount = res.get("pay_amount", amount)
    card = res.get("card", PAYMENT_CARD)

    pending_auto_payments[token] = {
        "user_id": user_id,
        "amount": amount,
        "pay_amount": pay_amount,
        "token": token,
        "card": card,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "message_id": status_msg.message_id
    }
    save_data()

    auto_card_text = (
        f"<blockquote>{custom_tag('deposit')}⚡️ <b>Avto to'lov (PayHamyon)</b>\n\n"
        f"💳 <b>Karta raqami:</b> <code>{card}</code>\n"
        f"👤 <b>Karta egasi:</b> {PAYMENT_CARD_OWNER}\n"
        f"💵 <b>To'lov summasi:</b> <code>{money(pay_amount)}</code> so'm\n"
        f"🧾 <b>To'lov Tokeni:</b> <code>{token}</code>\n\n"
        f"⚠️ <b>MUHIM KO'RSATMA:</b>\n"
        f"1. Yuqoridagi kartaga aynan <b>{money(pay_amount)} so'm</b> o'tkazing.\n"
        f"2. To'lovni amalga oshirgach, pastdagi <b>🔄 To'lovni tekshirish</b> tugmasini bosing.\n"
        f"3. Balansingiz darhol avtomatik tarzda to'ldiriladi!\n\n"
        f"⏱ <i>Ushbu to'lov oynasi 15 daqiqa davomida amal qiladi.</i></blockquote>"
    )

    b = InlineKeyboardBuilder()
    b.row(p_btn("🔄 To'lovni tekshirish", f"check_auto_{token}", "check_btn"))
    b.row(p_btn("❌ Bekor qilish", f"cancel_auto_{token}", "cancel"))

    await status_msg.edit_text(auto_card_text, reply_markup=b.as_markup())
    last_menu_messages[user_id] = status_msg.message_id


# ------------------------------------------------------------------------------
# 1. AVTO TO'LOV (PAYHAMYON GATEWAY)
# ------------------------------------------------------------------------------
@dp.callback_query(F.data.startswith("pay_method_auto_"))
async def start_auto_payment(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    raw_amount = callback.data.replace("pay_method_auto_", "")
    try:
        amount = int(raw_amount)
    except Exception:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
        return

    await callback.message.edit_text("⏳ PayHamyon to'lov cheki yaratilmoqda, kuting...")

    # PayHamyon API orqali hisob yaratish
    res = await async_create_payment(amount=amount)

    if not res.get("success"):
        err = res.get("error", "Noma'lum xatolik")
        b = InlineKeyboardBuilder()
        b.row(p_btn("Orqaga", "deposit", "back"))

        await callback.message.edit_text(
            f"<blockquote>⚠️ <b>Avto to'lov tizimida vaqtinchalik xatolik yuz berdi.</b>\n"
            f"Xatolik tafsiloti: <code>{err}</code>\n\n"
            "Hisobingizni Qo'lda to'lov (Karta + Chek) orqali to'ldirishingiz mumkin.</blockquote>",
            reply_markup=b.as_markup()
        )
        await callback.answer()
        return

    token = res.get("token")
    pay_amount = res.get("pay_amount", amount)
    card = res.get("card", PAYMENT_CARD)

    pending_auto_payments[token] = {
        "user_id": user_id,
        "amount": amount,
        "pay_amount": pay_amount,
        "token": token,
        "card": card,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "message_id": callback.message.message_id
    }
    save_data()

    auto_card_text = (
        f"<blockquote>{custom_tag('deposit')}⚡️ <b>Avto to'lov (PayHamyon)</b>\n\n"
        f"💳 <b>Karta raqami:</b> <code>{card}</code>\n"
        f"💵 <b>To'lov summasi:</b> <code>{money(pay_amount)}</code> so'm\n"
        f"🧾 <b>To'lov Tokeni:</b> <code>{token}</code>\n\n"
        f"⚠️ <b>MUHIM KO'RSATMA:</b>\n"
        f"1. Yuqoridagi kartaga aynan <b>{money(pay_amount)} so'm</b> o'tkazing.\n"
        f"2. To'lovni amalga oshirgach, pastdagi <b>🔄 To'lovni tekshirish</b> tugmasini bosing.\n"
        f"3. Balansingiz darhol avtomatik tarzda to'ldiriladi!\n\n"
        f"⏱ <i>Ushbu to'lov oynasi 15 daqiqa davomida amal qiladi.</i></blockquote>"
    )

    b = InlineKeyboardBuilder()
    b.row(p_btn("🔄 To'lovni tekshirish", f"check_auto_{token}", "check_btn"))
    b.row(p_btn("❌ Bekor qilish", f"cancel_auto_{token}", "cancel"))

    await callback.message.edit_text(auto_card_text, reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("check_auto_"))
async def check_auto_payment_handler(callback: types.CallbackQuery):
    token = callback.data.replace("check_auto_", "")
    payment = pending_auto_payments.get(token)

    if not payment:
        await callback.answer("❌ Bu to'lov topilmadi yoki muddati o'tgan.", show_alert=True)
        return

    if payment.get("status") == "paid":
        await callback.answer("✅ Bu to'lov allaqachon hisobingizga tushirilgan!", show_alert=True)
        return

    user_id = payment["user_id"]
    amount = payment["amount"]

    await callback.answer("⏳ To'lov tekshirilmoqda...")

    # API orqali tekshirish
    res = await async_check_payment(token)

    is_paid = False
    if res.get("success"):
        status_val = str(res.get("status", "")).lower()
        if status_val in ["paid", "completed", "success", "1", 1] or res.get("paid") is True or res.get("is_paid") is True:
            is_paid = True
        elif isinstance(res.get("data"), dict):
            sub_status = str(res["data"].get("status", "")).lower()
            if sub_status in ["paid", "completed", "success", "1", 1] or res["data"].get("paid") is True:
                is_paid = True

    if is_paid:
        # To'lov tasdiqlandi!
        payment["status"] = "paid"
        payment["paid_at"] = datetime.now().isoformat()
        update_balance(user_id, amount)
        save_data()

        success_text = (
            f"<blockquote>{custom_tag('deposit')}✅ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"Hisobingizga <b>+{money(amount)} so'm</b> qo'shildi!\n"
            f"Joriy balansingiz: <b>{money(get_balance(user_id))} so'm</b></blockquote>"
        )
        b = InlineKeyboardBuilder()
        b.row(p_btn("🏠 Asosiy menyu", "back_main", "back"))

        await callback.message.edit_text(success_text, reply_markup=b.as_markup())

        # Adminga avto xabar
        admin_text = (
            f"<blockquote>⚡️ <b>Yangi Avto To'lov (PayHamyon)!</b>\n\n"
            f"Foydalanuvchi: <a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a> (@{callback.from_user.username or 'yoq'})\n"
            f"ID: <code>{user_id}</code>\n"
            f"Summa: <b>{money(amount)} so'm</b>\n"
            f"Token: <code>{token}</code>\n"
            f"Holat: ✅ Avtomatik tasdiqlandi</blockquote>"
        )
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        except Exception:
            pass

    else:
        err = res.get("error", "")
        status_val = res.get("status")
        if status_val in ["canceled", "cancelled", "expired", "failed"]:
            payment["status"] = "cancelled"
            save_data()
            await callback.message.edit_text(
                "<blockquote>❌ <b>To'lov muddati tugagan yoki bekor qilingan.</b></blockquote>",
                reply_markup=back_main_keyboard(user_id)
            )
        else:
            await callback.answer(
                "⏳ To'lov hali tasdiqlanmadi!\n\nIltimos, kartaga to'lovni to'liq o'tkazganingizga ishonch hosil qiling va 10-15 soniyadan so'ng qayta tekshiring.",
                show_alert=True
            )


@dp.callback_query(F.data.startswith("cancel_auto_"))
async def cancel_auto_payment_handler(callback: types.CallbackQuery):
    token = callback.data.replace("cancel_auto_", "")
    payment = pending_auto_payments.get(token)

    if payment:
        payment["status"] = "cancelled"
        save_data()

    try:
        await async_cancel_payment(token)
    except Exception:
        pass

    await callback.message.edit_text(
        main_menu_text(callback.from_user.id),
        reply_markup=get_main_inline_menu(callback.from_user.id)
    )
    await callback.answer("To'lov bekor qilindi.")


# ------------------------------------------------------------------------------
# 2. QO'LDA TO'LOV (KARTA + ADMIN TASDIQLASHI)
# ------------------------------------------------------------------------------
@dp.callback_query(F.data.startswith("pay_method_manual_"))
async def start_manual_payment(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    raw_amount = callback.data.replace("pay_method_manual_", "")
    try:
        amount = int(raw_amount)
    except Exception:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
        return

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

    await callback.message.edit_text(card_text, reply_markup=builder.as_markup())

    pending_payments[payment_id] = {
        "user_id": user_id,
        "amount": amount,
        "message_id": callback.message.message_id,
        "status": "pending"
    }
    save_data()

    payment_expiry_tasks[payment_id] = asyncio.create_task(
        expire_payment(user_id, payment_id)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("send_pay_"))
async def send_payment_to_admin(callback: types.CallbackQuery, state: FSMContext):
    payment_id = callback.data.replace("send_pay_", "")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("user_id") != callback.from_user.id or payment.get("status") != "pending":
        await callback.answer("⏰ Bu to'lov oynasining muddati tugagan.", show_alert=True)
        return

    payment["status"] = "waiting_receipt"
    save_data()
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
async def process_deposit_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get("payment_id")
    payment = pending_payments.get(payment_id)

    if not payment or payment.get("user_id") != message.from_user.id or payment.get("status") != "waiting_receipt":
        await state.clear()
        await message.answer(
            "<blockquote><b>To'lov vaqti tugagan.</b>\n\nYangi to'lov oynasini ochib, qaytadan urinib ko'ring.</blockquote>",
            reply_markup=back_main_keyboard(message.from_user.id)
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
    save_data()
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
        save_data()
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
async def approve_payment(callback: types.CallbackQuery):
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
    save_data()

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
async def reject_payment(callback: types.CallbackQuery):
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
    save_data()

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


# ==============================================================================
# XARIDLAR: STARS, GIFT, PREMIUM
# ==============================================================================
@dp.callback_query(F.data == "buy_stars")
async def stars_menu(callback: types.CallbackQuery):
    uid = callback.from_user.id
    builder = InlineKeyboardBuilder()
    for key, data in STARS_PRICES.items():
        builder.add(p_btn(data["name"], f"buyprod_{key}", "stars"))
    builder.adjust(2)
    builder.row(p_btn("Boshqa miqdorda Stars", "custom_stars", "custom_stars"))
    builder.row(p_btn(tr(uid, "back"), "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Stars paketini tanlang:</b>\n\nKerakli paketni bosing.</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "custom_stars")
async def custom_stars_start(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    one_star_price = prices.get("custom_star", 225)
    text = (
        f"<blockquote>{custom_tag('custom_stars')}<b>Boshqa miqdorda Stars olish</b>\n\n"
        f"1 ta Stars narxi: <b>{money(one_star_price)} so'm</b>\n\n"
        "Minimal buyurtma: 50 Stars\n\n"
        "Qancha Stars olmoqchisiz?</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=back_main_keyboard(uid))
    await state.set_state(CustomStarsState.waiting_for_stars_amount)
    await callback.answer()


@dp.message(CustomStarsState.waiting_for_stars_amount)
async def process_custom_stars_amount(message: types.Message, state: FSMContext):
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
    total_price = int(count * float(prices.get("custom_star", 220)))

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
    builder.row(p_btn(tr(user_id, "back"), "buy_stars", "back"))

    if get_balance(user_id) < total_price:
        text = (
            f"<blockquote>{custom_tag('stars')}<b>Stars buyurtmasi</b>\n\n"
            f"Mahsulot: <b>{count} Stars</b>\n"
            f"Narxi: <b>{money(total_price)} so'm</b>\n\n"
            "⚠️ <b>Hisobingizda mablag' yetarli emas.</b>\nAvval hisobingizni to'ldiring.</blockquote>"
        )
        builder = InlineKeyboardBuilder()
        builder.row(p_btn(tr(user_id, "deposit"), "deposit", "deposit"))
        builder.row(p_btn(tr(user_id, "back"), "buy_stars", "back"))
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
async def gift_menu(callback: types.CallbackQuery):
    uid = callback.from_user.id
    builder = InlineKeyboardBuilder()
    for key, data in GIFT_PRICES.items():
        builder.add(p_btn(data["name"], f"buyprod_{key}", key))
    builder.adjust(2)
    builder.row(p_btn(tr(uid, "back"), "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('gift')}<b>Gift olish</b>\n\nKerakli Giftni tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


SELL_GIFT_INFO = {
    "sell_gift_ayiqcha": "Ayiqcha",
    "sell_gift_yurak": "Yurakcha",
    "sell_gift_atirgul": "Qizil Atirgul",
    "sell_gift_quti": "Syurpriz quti",
    "sell_gift_lola": "Lola guldastasi",
    "sell_gift_raketa": "Kosmik Raketa",
    "sell_gift_tort": "Tug'ilgan kun torti",
    "sell_gift_shampan": "Shampan",
    "sell_gift_kubok": "Oltin Kubok",
    "sell_gift_olmos": "Moviy Olmos",
    "sell_gift_yuzuk": "Brilliant Uzuk",
    "sell_gift_bear": "Ayiqcha",
    "sell_gift_heart": "Yurakcha",
    "sell_gift_box": "Syurpriz quti",
    "sell_gift_rose": "Qizil Atirgul",
    "sell_gift_rocket": "Kosmik Raketa",
    "sell_gift_cake": "Tug'ilgan kun torti",
    "sell_gift_gem": "Moviy Olmos",
    "sell_gift_ring": "Brilliant Uzuk"
}

SELL_GIFT_ALIAS = {
    "sell_gift_bear": "sell_gift_ayiqcha",
    "sell_gift_heart": "sell_gift_yurak",
    "sell_gift_box": "sell_gift_quti",
    "sell_gift_rose": "sell_gift_atirgul",
    "sell_gift_rocket": "sell_gift_raketa",
    "sell_gift_cake": "sell_gift_tort",
    "sell_gift_gem": "sell_gift_olmos",
    "sell_gift_ring": "sell_gift_yuzuk"
}


@dp.callback_query(F.data == "sell_gift_menu")
async def sell_gift_start(callback: types.CallbackQuery):
    uid = callback.from_user.id
    builder = InlineKeyboardBuilder()
    active_keys = [
        "sell_gift_ayiqcha", "sell_gift_yurak",
        "sell_gift_atirgul", "sell_gift_quti",
        "sell_gift_lola", "sell_gift_raketa",
        "sell_gift_tort", "sell_gift_shampan",
        "sell_gift_kubok", "sell_gift_olmos", "sell_gift_yuzuk"
    ]
    for key in active_keys:
        name = SELL_GIFT_INFO.get(key, key)
        p = prices['sell_gifts'].get(key)
        if p is None:
            alias = SELL_GIFT_ALIAS.get(key)
            p = prices['sell_gifts'].get(alias, 0) if alias else 0
        builder.add(
            p_btn(f"{name} — {money(p)} so'm", key, key)
        )
    builder.adjust(2)
    builder.row(p_btn(tr(uid, "back"), "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('sell')}<b>Qaysi giftni sotmoqchisiz?</b></blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("sell_gift_"))
async def process_gift_choice(call: types.CallbackQuery, state: FSMContext):
    key = call.data
    if key not in SELL_GIFT_INFO:
        await call.answer()
        return

    gift_name = SELL_GIFT_INFO[key]
    price_val = prices['sell_gifts'].get(key)
    if price_val is None:
        alias = SELL_GIFT_ALIAS.get(key)
        price_val = prices['sell_gifts'].get(alias, 0) if alias else 0

    price_str = f"{money(price_val)} so'm"
    await state.clear()
    await state.update_data(gift_key=key, gift_name=gift_name, price_str=price_str, price_val=price_val)

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("💳 Plastik kartaga", "sell_payout_card", "deposit"))
    builder.row(p_btn("👛 Bot hisobiga (Balansga)", "sell_payout_balance", "balance"))
    builder.row(p_btn(tr(call.from_user.id, "back"), "sell_gift_menu", "back"))

    text = (
        f"<blockquote>{custom_tag('sell')}Siz <b>{gift_name}</b> sotishni tanladingiz.\n"
        f"Narxi: <b>{price_str}</b>\n\n"
        "Pulingizni qayerga qabul qilib olmoqchisiz?</blockquote>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())
    await call.answer()


@dp.callback_query(F.data == "sell_payout_balance")
async def process_payout_balance(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    gift_name = data.get("gift_name")
    price_str = data.get("price_str")
    await state.set_state(None)
    await state.update_data(payout_type="balance", card=None)

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("✅ Tashladim", "sell_confirm_sent", "sent_btn"))
    builder.row(p_btn(tr(call.from_user.id, "cancel"), "back_main", "cancel"))

    text = (
        f"<blockquote>{custom_tag('sell')}<b>Gift sotish (Bot hisobiga)</b>\n\n"
        f"Gift: <b>{gift_name}</b>\n"
        f"To'lanadigan summa: <b>{price_str}</b>\n"
        "Qabul qilish usuli: <b>Bot hisobiga (Balansga)</b>\n\n"
        f"1. Telegram orqali <b>{ADMIN_USERNAME}</b> profiliga kiring.\n"
        f"2. Sovg'ani (<b>{gift_name}</b>) {ADMIN_USERNAME} ga yuboring.\n"
        "3. Sovg'ani yuborganingizdan so'ng, pastdagi <b>Tashladim</b> tugmasini bosing!</blockquote>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())
    await call.answer()


@dp.callback_query(F.data == "sell_payout_card")
async def process_payout_card(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(payout_type="card")
    builder = InlineKeyboardBuilder()
    builder.row(p_btn(tr(call.from_user.id, "back"), "sell_gift_menu", "back"))

    text = (
        f"<blockquote>{custom_tag('deposit')}<b>Plastik karta raqamingizni yozing:</b>\n\n"
        "<i>(16 xonali karta raqami)</i></blockquote>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(GiftSellState.waiting_for_card_number)
    await call.answer()


@dp.message(GiftSellState.waiting_for_card_number)
async def process_sell_card_number(message: types.Message, state: FSMContext):
    card_raw = re.sub(r"\D", "", message.text or "")
    if len(card_raw) != 16:
        msg = await message.answer("<blockquote>⚠️ <b>Xatolik!</b>\n\nIltimos, to'g'ri 16 xonali karta raqamini kiriting.</blockquote>")
        await asyncio.sleep(2.5)
        await safe_delete(msg)
        return

    formatted_card = f"{card_raw[:4]} {card_raw[4:8]} {card_raw[8:12]} {card_raw[12:]}"
    await state.update_data(card=formatted_card)
    data = await state.get_data()
    gift_name = data.get("gift_name")
    price_str = data.get("price_str")
    await safe_delete(message)

    builder = InlineKeyboardBuilder()
    builder.row(p_btn("✅ Tashladim", "sell_confirm_sent", "sent_btn"))
    builder.row(p_btn(tr(message.from_user.id, "cancel"), "back_main", "cancel"))

    text = (
        f"<blockquote>{custom_tag('sell')}<b>Gift sotish (Plastik kartaga)</b>\n\n"
        f"Gift: <b>{gift_name}</b>\n"
        f"To'lanadigan summa: <b>{price_str}</b>\n"
        f"Kartangiz: <code>{formatted_card}</code>\n\n"
        f"1. Telegram orqali <b>{ADMIN_USERNAME}</b> profiliga kiring.\n"
        f"2. Sovg'ani (<b>{gift_name}</b>) {ADMIN_USERNAME} ga yuboring.\n"
        "3. Sovg'ani yuborganingizdan so'ng, pastdagi <b>Tashladim</b> tugmasini bosing!</blockquote>"
    )
    await delete_previous_menu(message.from_user.id)
    msg = await message.answer(text, reply_markup=builder.as_markup())
    last_menu_messages[message.from_user.id] = msg.message_id


@dp.callback_query(F.data == "sell_confirm_sent")
async def process_sell_confirm_sent(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    gift_name = data.get("gift_name")
    price_str = data.get("price_str")
    price_val = int(data.get("price_val", 0))
    payout_type = data.get("payout_type", "balance")
    card = data.get("card")

    if not gift_name:
        await call.answer("❌ Ma'lumot topilmadi!", show_alert=True)
        return

    user = call.from_user
    sell_id = f"sg_{user.id}_{int(datetime.now().timestamp() * 1000)}"
    sell_orders[sell_id] = {
        "user_id": user.id,
        "user_name": user.full_name,
        "username": user.username or "yoq",
        "gift_name": gift_name,
        "price_val": price_val,
        "price_str": price_str,
        "payout_type": payout_type,
        "card": card,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    save_data()
    await state.clear()

    payout_info = f"<code>{card}</code> kartasiga" if payout_type == "card" else "Bot hisobingizga (Balansga)"

    user_reply = (
        f"<blockquote>✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"Gift: <b>{gift_name}</b>\n"
        f"Summa: <b>{price_str}</b>\n"
        f"Qabul qilish: <b>{payout_info}</b>\n\n"
        f"Admin ({ADMIN_USERNAME}) sovg'a kelganini tekshirib tasdiqlagach, pulingiz o'tkaziladi.\n"
        "Kutishingizni so'raymiz.</blockquote>"
    )
    await call.message.edit_text(user_reply, reply_markup=back_main_keyboard(user.id))
    await call.answer("✅ So'rov adminga yuborildi!")

    payout_display = f"💳 Karta: <code>{card}</code>" if payout_type == "card" else "👛 Bot hisobiga (Balans)"
    admin_text = (
        f"<blockquote>{custom_tag('sell')}🔔 <b>YANGI GIFT SOTISH SO'ROVI!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> <a href='tg://user?id={user.id}'>{user.full_name}</a> (@{user.username or 'yoq'})\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🎁 <b>Gift:</b> <b>{gift_name}</b>\n"
        f"💰 <b>Summa:</b> <b>{price_str}</b>\n"
        f"📥 <b>To'lov usuli:</b> <b>{payout_display}</b>\n\n"
        "<b>Ushbu gift sotish so'rovi tasdiqlansinmi yoki tasdiqlanmasinmi?</b></blockquote>"
    )
    admin_builder = InlineKeyboardBuilder()
    admin_builder.row(
        p_btn("✅ Tasdiqlash", f"admin_sell_approve_{sell_id}", "check_btn"),
        p_btn("❌ Rad etish", f"admin_sell_reject_{sell_id}", "cancel")
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_builder.as_markup())
    except Exception as e:
        logging.error(f"Adminga so'rov yuborishda xatolik: {e}")


@dp.callback_query(F.data.startswith("admin_sell_approve_"))
async def admin_sell_approve(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Faqat admin uchun!", show_alert=True)
        return

    sell_id = call.data.replace("admin_sell_approve_", "")
    order = sell_orders.get(sell_id)
    if not order or order.get("status") != "pending":
        await call.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    order["status"] = "approved"
    save_data()

    uid = order["user_id"]
    gift_name = order.get("gift_name", "Gift")
    price_val = int(order.get("price_val", 0))
    price_str = order.get("price_str", f"{money(price_val)} so'm")
    payout_type = order.get("payout_type", "balance")
    card = order.get("card")

    if payout_type == "balance":
        update_balance(uid, price_val)
        notify_text = (
            f"<blockquote>✅ <b>Gift sotish tasdiqlandi!</b>\n\n"
            f"🎁 <b>{gift_name}</b> qabul qilindi.\n"
            f"💰 <b>{price_str}</b> bot balansingizga qo'shildi!\n\n"
            f"Hozirgi balansingiz: <b>{money(get_balance(uid))} so'm</b></blockquote>"
        )
    else:
        notify_text = (
            f"<blockquote>✅ <b>Gift sotish tasdiqlandi!</b>\n\n"
            f"🎁 <b>{gift_name}</b> qabul qilindi.\n"
            f"💰 <b>{price_str}</b> plastik kartangizga (<code>{card}</code>) o'tkazildi!\n\n"
            "Biz bilan savdo qilganingiz uchun rahmat!</blockquote>"
        )

    try:
        await bot.send_message(chat_id=uid, text=notify_text, reply_markup=back_main_keyboard(uid))
    except Exception as e:
        logging.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")

    await call.message.edit_text(
        call.message.text + "\n\n<blockquote>✅ <b>TASDIQLANDI!</b> Foydalanuvchiga xabar berildi.</blockquote>"
    )
    await call.answer("✅ Muvaffaqiyatli tasdiqlandi!")


@dp.callback_query(F.data.startswith("admin_sell_reject_"))
async def admin_sell_reject(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Faqat admin uchun!", show_alert=True)
        return

    sell_id = call.data.replace("admin_sell_reject_", "")
    order = sell_orders.get(sell_id)
    if not order or order.get("status") != "pending":
        await call.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    order["status"] = "rejected"
    save_data()

    uid = order["user_id"]
    gift_name = order.get("gift_name", "Gift")
    notify_text = (
        f"<blockquote>❌ <b>Gift sotish so'rovingiz rad etildi!</b>\n\n"
        f"🎁 Gift: <b>{gift_name}</b>\n"
        f"Admin sovg'a yuborilganligini tasdiqlamadi.\n\n"
        f"Savollaringiz bo'lsa adminga murojaat qiling: {ADMIN_USERNAME}</blockquote>"
    )
    try:
        await bot.send_message(chat_id=uid, text=notify_text, reply_markup=back_main_keyboard(uid))
    except Exception as e:
        logging.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")

    await call.message.edit_text(
        call.message.text + "\n\n<blockquote>❌ <b>RAD ETILDI!</b> Foydalanuvchiga rad etilgani haqida xabar yuborildi.</blockquote>"
    )
    await call.answer("❌ So'rov rad etildi!")


@dp.callback_query(F.data.startswith("sell_done_"))
async def legacy_sell_done(call: types.CallbackQuery):
    call.data = call.data.replace("sell_done_", "admin_sell_approve_")
    await admin_sell_approve(call)


@dp.callback_query(F.data.startswith("sell_reject_"))
async def legacy_sell_reject(call: types.CallbackQuery):
    call.data = call.data.replace("sell_reject_", "admin_sell_reject_")
    await admin_sell_reject(call)


@dp.callback_query(F.data.startswith("approve_"))
async def handle_webapp_order_approve(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = call.data.replace("approve_", "")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "database.json")
    if not os.path.exists(db_path):
        db_path = os.path.join("data", "database.json")

    if not os.path.exists(db_path):
        await call.answer("❌ database.json topilmadi!", show_alert=True)
        return

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            web_db = json.load(f)
    except Exception as e:
        await call.answer(f"Xatolik: {e}", show_alert=True)
        return

    tx = next((t for t in web_db.get("transactions", []) if t.get("id") == order_id), None)
    if not tx:
        await call.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    if tx.get("status") != "Kutilmoqda":
        await call.answer(f"ℹ️ Bu buyurtma holati allaqachon: {tx.get('status')}", show_alert=True)
        return

    user_id = str(tx.get("user_id"))
    amount = int(tx.get("amount", 0))

    if "users" not in web_db:
        web_db["users"] = {}
    user_obj = web_db["users"].get(user_id)

    current_bal = user_obj.get("balance", 0) if user_obj else get_balance(user_id)
    if current_bal < amount:
        await call.answer("⚠️ Foydalanuvchi balansida mablag' yetarli emas!", show_alert=True)
        return

    new_bal = current_bal - amount
    if user_obj:
        user_obj["balance"] = new_bal
    tx["status"] = "Bajarildi"

    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(web_db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving database.json: {e}")

    # Synchronize balance with bot_database.json
    user_balances[user_id] = new_bal
    save_data()

    # Also notify local server.js if running
    try:
        send_request("http://127.0.0.1:3000/api/orders/approve", {"order_id": order_id})
    except Exception:
        pass

    # Notify customer in Telegram
    if user_id.isdigit():
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text=(
                    f"<blockquote>🎉 <b>Xaridingiz muvaffaqiyatli yetkazildi!</b>\n\n"
                    f"🆔 Buyurtma: <code>#{tx['id']}</code>\n"
                    f"📦 Mahsulot: <b>{tx.get('name', 'Mahsulot')}</b>\n"
                    f"👤 Qabul qiluvchi: <b>{tx.get('recipient', '')}</b>\n"
                    f"💰 Yechilgan summa: <b>{money(amount)} so'm</b>\n"
                    f"💳 Yangi balansingiz: <b>{money(new_bal)} so'm</b>\n\n"
                    f"<i>STARBOZOR xizmatidan foydalanganingiz uchun rahmat!</i></blockquote>"
                )
            )
        except Exception as e:
            logging.error(f"Foydalanuvchiga tasdiq xabari yuborishda xatolik: {e}")

    await call.message.edit_text(
        call.message.text + f"\n\n<blockquote>✅ <b>BUYURTMA TASDIQLANDI VA YUBORILDI</b>\n"
                            f"Yangi foydalanuvchi balansi: <b>{money(new_bal)} so'm</b>\n"
                            f"Holat: <b>Bajarildi ✅</b></blockquote>"
    )
    await call.answer("✅ Buyurtma tasdiqlandi va yetkazildi!", show_alert=True)


@dp.callback_query(F.data.startswith("reject_") | F.data.startswith("cancel_"))
async def handle_webapp_order_reject(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = call.data.replace("reject_", "").replace("cancel_", "")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "database.json")
    if not os.path.exists(db_path):
        db_path = os.path.join("data", "database.json")

    if not os.path.exists(db_path):
        await call.answer("❌ database.json topilmadi!", show_alert=True)
        return

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            web_db = json.load(f)
    except Exception as e:
        await call.answer(f"Xatolik: {e}", show_alert=True)
        return

    tx = next((t for t in web_db.get("transactions", []) if t.get("id") == order_id), None)
    if not tx:
        await call.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    if tx.get("status") != "Kutilmoqda":
        await call.answer(f"Bu buyurtma allaqachon: {tx.get('status')}", show_alert=True)
        return

    tx["status"] = "Bekor qilindi"

    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(web_db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving database.json: {e}")

    try:
        send_request("http://127.0.0.1:3000/api/orders/reject", {"order_id": order_id})
    except Exception:
        pass

    user_id = str(tx.get("user_id"))
    if user_id.isdigit():
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text=(
                    f"<blockquote>❌ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                    f"🆔 Buyurtma: <code>#{tx['id']}</code>\n"
                    f"📦 Mahsulot: <b>{tx.get('name', 'Mahsulot')}</b>\n"
                    f"Mablag' hisobingizdan yechilmadi.\n"
                    f"Savollar bo'lsa adminga murojaat qiling: {ADMIN_USERNAME}</blockquote>"
                )
            )
        except Exception:
            pass

    await call.message.edit_text(
        call.message.text + "\n\n<blockquote>❌ <b>BUYURTMA BEKOR QILINDI!</b> Mablag' yechilmadi.</blockquote>"
    )
    await call.answer("❌ Buyurtma bekor qilindi.", show_alert=True)


@dp.callback_query(F.data == "buy_premium")
async def premium_menu(callback: types.CallbackQuery):
    uid = callback.from_user.id
    builder = InlineKeyboardBuilder()
    builder.row(p_btn("Profilga kirmasdan (Avto)", "prem_auto_menu", "prem_auto"))
    builder.row(p_btn("Profilga kirib (Admin orqali)", "prem_admin_menu", "prem_admin"))
    builder.row(p_btn(tr(uid, "back"), "back_main", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Premium olish</b>\n\nPremium berish usulini tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "prem_auto_menu")
async def premium_auto_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for key in ("prem_3", "prem_6", "prem_12_gift", "prem_12"):
        if key in PREMIUM_PRICES:
            data = PREMIUM_PRICES[key]
            builder.row(p_btn(data["name"], f"buyprod_{key}", key if key in menu_emojis else "premium"))
    builder.row(p_btn("Orqaga", "buy_premium", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Avtomatik Premium</b>\n\nKerakli muddatni tanlang:</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "prem_admin_menu")
async def premium_admin_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for key in ("prem_1", "prem_12"):
        if key in PREMIUM_PRICES:
            data = PREMIUM_PRICES[key]
            builder.row(p_btn(data["name"], f"buyprod_{key}", key if key in menu_emojis else "premium"))
    builder.row(p_btn("Orqaga", "buy_premium", "back"))

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('premium')}<b>Admin orqali Premium</b>\n\nPaketni tanlang.</blockquote>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("buyprod_"))
async def select_product(callback: types.CallbackQuery, state: FSMContext):
    prod_key = callback.data.split("buyprod_", 1)[1]
    product = ALL_PRODUCTS.get(prod_key)

    if not product:
        await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
        return

    user_id = callback.from_user.id
    if get_balance(user_id) < product["price"]:
        builder = InlineKeyboardBuilder()
        builder.row(p_btn(tr(user_id, "deposit"), "deposit", "deposit"))
        builder.row(p_btn(tr(user_id, "back"), "back_main", "back"))

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
    builder.row(p_btn(tr(user_id, "back"), "back_main", "back"))

    text = (
        f"<blockquote><b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Narxi:</b> {money(product['price'])} so'm\n\n"
        "Qaysi profilga olmoqchisiz?</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "target_self")
async def target_self_handler(callback: types.CallbackQuery, state: FSMContext):
    username = callback.from_user.username
    target = f"@{username}" if username else f"ID: {callback.from_user.id}"
    await state.update_data(target=target)
    await confirm_purchase_menu(callback, state)


@dp.callback_query(F.data == "target_other")
async def target_other_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<blockquote><b>Boshqa profilga yuborish</b>\n\nFoydalanuvchi username'ini yuboring:\n(Masalan: @username yoki username)</blockquote>",
        reply_markup=back_main_keyboard(callback.from_user.id)
    )
    await state.set_state(BuyState.waiting_for_target)
    await callback.answer()


@dp.message(BuyState.waiting_for_target)
async def process_target_username(message: types.Message, state: FSMContext):
    target = (message.text or "").strip()
    target = re.sub(r"^https?://t\.me/", "@", target)
    target = re.sub(r"^t\.me/", "@", target)

    if not target.startswith("@") and not target.isdigit():
        target = f"@{target}"

    if len(target) < 3:
        msg = await message.answer("<blockquote>⚠️ To'g'ri username yuboring (Masalan: @username)!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    await state.update_data(target=target)
    await confirm_purchase_menu_msg(message, state)


async def confirm_purchase_menu(callback: types.CallbackQuery, state: FSMContext):
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


async def confirm_purchase_menu_msg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product = data.get("product")
    target = data.get("target")

    if not product or not target:
        await state.clear()
        await message.answer("❌ Ma'lumot topilmadi.", reply_markup=back_main_keyboard(message.from_user.id))
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
async def execute_purchase(callback: types.CallbackQuery, state: FSMContext):
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
    save_data()

    await callback.message.edit_text(
        f"<blockquote>{custom_tag('stars')}<b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"<b>Mahsulot:</b> {product['formatted']}\n"
        f"<b>Qabul qiluvchi:</b> {target}\n\n"
        "Tez orada buyurtmangiz bajariladi. Rahmat!</blockquote>",
        reply_markup=back_main_keyboard(user_id)
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
async def admin_order_done(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = callback.data.replace("ord_done_", "")
    order_info = active_orders.get(order_id)
    if not order_info:
        await callback.answer("❌ Bu buyurtma allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    user_id = order_info["user_id"]
    purchase_history.append({
        "time": datetime.now().isoformat(),
        "user_id": user_id,
        "name": order_info.get("user_name", str(user_id)),
        "price": int(order_info.get("price", 0)),
        "product": order_info.get("product_name", "")
    })
    active_orders.pop(order_id, None)
    save_data()

    await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>HOLAT:</b> Tasdiqlandi va bajarildi.")

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

    await callback.answer("✅ Buyurtma tasdiqlandi!")


@dp.callback_query(F.data.startswith("ord_cancel_"))
async def admin_order_cancel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return

    order_id = callback.data.replace("ord_cancel_", "")
    order_info = active_orders.get(order_id)
    if not order_info:
        await callback.answer("❌ Bu buyurtma allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    user_id = order_info["user_id"]
    price = order_info["price"]
    active_orders.pop(order_id, None)
    update_balance(user_id, price)
    save_data()

    await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>HOLAT:</b> Bekor qilindi va pul qaytarildi.")

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"<blockquote>❌ Buyurtmangiz bekor qilindi. Hisobingizga <b>{money(price)} so'm</b> qaytarildi.</blockquote>",
            reply_markup=back_main_keyboard(user_id)
        )
    except Exception:
        pass

    await callback.answer("Bekor qilindi va pul qaytarildi!")


# ==============================================================================
# WEB SERVER VA WEBHOOK QABUL QILUVCHI
# ==============================================================================
async def dummy_handler(request):
    return web.Response(text="Bot ishlamoqda!")


async def payhamyon_webhook_handler(request):
    """PayHamyon serveridan kelgan avtomatik to'lov callback bildirishnomasi"""
    try:
        try:
            data = await request.json()
        except Exception:
            data = dict(await request.post())

        token = data.get("token")
        status = str(data.get("status", "")).lower()

        if token and status in ["paid", "completed", "success", "1", 1]:
            payment = pending_auto_payments.get(token)
            if payment and payment.get("status") == "pending":
                payment["status"] = "paid"
                payment["paid_at"] = datetime.now().isoformat()
                user_id = payment["user_id"]
                amount = payment["amount"]
                update_balance(user_id, amount)
                save_data()

                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"<blockquote>{custom_tag('deposit')}✅ <b>To'lov qabul qilindi!</b>\n\n"
                            f"Hisobingizga <b>+{money(amount)} so'm</b> qo'shildi!\n"
                            f"Joriy balansingiz: <b>{money(get_balance(user_id))} so'm</b></blockquote>"
                        ),
                        reply_markup=back_main_keyboard(user_id)
                    )
                except Exception:
                    pass

                try:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=(
                            f"<blockquote>⚡️ <b>Yangi Avto To'lov (Webhook orqali)!</b>\n\n"
                            f"Foydalanuvchi ID: <code>{user_id}</code>\n"
                            f"Summa: <b>{money(amount)} so'm</b>\n"
                            f"Token: <code>{token}</code></blockquote>"
                        )
                    )
                except Exception:
                    pass

        return web.json_response({"success": True})
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", dummy_handler)
    app.router.add_post("/api/payhamyon/webhook", payhamyon_webhook_handler)
    app.router.add_post("/webhook", payhamyon_webhook_handler)
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


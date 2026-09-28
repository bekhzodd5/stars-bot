import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


BOT_TOKEN = os.getenv("BOT_TOKEN", "8982437206:AAHaoK7fzdF9UCnXaBFtlvleUxUUaD_ALRs")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN ko'rsatilmagan!")

ADMIN_ID = 7414653407
ADMIN_USERNAME = "@rymbyvv"
SUB_CHANNELS = ["@rymbyvv_otziv"]
DATA_FILE = "bot_database.json"

PAYMENT_CARD = os.getenv("PAYMENT_CARD", "9860 3566 3465 1745")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "Elvira kuralova")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

DEFAULT_PREMIUM_BUTTON_EMOJI_ID = "5364134765081423318"


def default_prices():
    return {
        "stars": {
            "50": 12500,
            "100": 22500,
            "150": 38000,
            "200": 45000,
            "250": 56000,
            "300": 67000,
            "400": 89000,
            "500": 110000,
            "600": 132000,
            "700": 154000,
            "800": 176000,
            "900": 198000,
            "1000": 220000
        },
        "gifts": {
            "gift_15": 3500,
            "gift_25": 6500,
            "gift_50": 10500,
            "gift_100": 20000
        },
        "premium": {
            "prem_3": 160000,
            "prem_6": 210000,
            "prem_12": 385000,
            "prem_1": 45000
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
        "custom_star": 225,
        "referral_reward": 1.5,
        "premium_button_emoji_id": DEFAULT_PREMIUM_BUTTON_EMOJI_ID,
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
                "deposit_minmax": "Minimum: <b>1.000 so'm</b>",
                "deposit_input": "Miqdorni yozing:",
                "payment_card_label": "Karta:",
                "payment_owner_label": "Ega:",
                "payment_transfer": "Kartaga <b>{amount} so'm</b> o'tkazing.\n\nTo'lov chekini (rasm/screenshot) shu yerga yuboring.\nVaqt: <b>5 daqiqa</b>.",
                "profile_title": "Profil", "language": "Til", "choose_lang": "Interfeys tilini tanlang:",
                "referral_title": "Referal tizimi", "contact_text": "Referal mukofotidan foydalanish uchun O'zbekiston (+998) yoki Rossiya (+7) raqamingizni yuboring."
            },
            "ru": {
                "main_title": "Главное меню",
                "main_trust": "Совершайте покупки с нами безопасно",
                "main_channel": "Следите за новостями канала @rymbyvv_otziv",
                "main_hint": "Выберите нужную услугу",
                "deposit_title": "Пополнение счёта",
                "deposit_prompt": "На какую сумму хотите пополнить счёт?",
                "deposit_minmax": "Минимум: <b>1.000 сум</b>",
                "deposit_input": "Введите сумму:",
                "payment_card_label": "Карта:",
                "payment_owner_label": "Владелец:",
                "payment_transfer": "Переведите на карту <b>{amount} сум</b>.\n\nОтправьте чек об оплате (скриншот).\nВремя: <b>5 минут</b>.",
                "profile_title": "Профиль", "language": "Язык", "choose_lang": "Выберите язык интерфейса:",
                "referral_title": "Реферальная система", "contact_text": "Для реферального вознаграждения отправьте номер Узбекистана (+998) или России (+7)."
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
                for code in ("uz", "ru"):
                    if isinstance(saved_texts.get(code), dict):
                        defaults["texts"][code].update({k: str(v) for k, v in saved_texts[code].items() if k in defaults["texts"][code]})

            for group in defaults:
                if group == "custom_star":
                    val = saved_prices.get(group)
                    if isinstance(val, (int, float)):
                        defaults[group] = int(val)
                elif group == "referral_reward":
                    val = saved_prices.get(group)
                    if isinstance(val, (int, float)):
                        defaults[group] = float(val)
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
    waiting_for_premium_emoji = State()
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


def menu_emoji(key, fallback=""):
    eid = menu_emojis.get(key)
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>' if eid else fallback


def phone_allowed(phone):
    digits = re.sub(r"\D", "", phone or "")
    return digits.startswith("998") or digits.startswith("7")


async def async_check_all_subs(user_id):
    unsubscribed = []
    for channel in SUB_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                unsubscribed.append(channel)
        except Exception:
            unsubscribed.append(channel)
    return unsubscribed


def get_sub_keyboard(unsubscribed_channels):
    builder = InlineKeyboardBuilder()
    for ch in unsubscribed_channels:
        builder.row(types.InlineKeyboardButton(text=f"📢 {ch} ga obuna bo'lish", url=f"https://t.me/{ch.replace('@', '')}", icon_custom_emoji_id=menu_emojis.get("channel_btn")))
    builder.row(types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription", icon_custom_emoji_id=menu_emojis.get("check_btn")))
    return builder.as_markup()


def build_products():
    stars = {}
    for s_str, p in prices["stars"].items():
        stars[f"stars_{s_str}"] = {
            "name": f"{s_str} Stars - {money(p)} so'm",
            "formatted": f"{menu_emoji('stars', '⭐️')} <b>{s_str} Stars</b> - {money(p)} so'm",
            "price": int(p),
            "count": int(s_str)
        }

    gifts_info = {
        "gift_15": "15 talik Gift (13 stars)",
        "gift_25": "25 talik Gift (21 stars)",
        "gift_50": "50 talik Gift (43 stars)",
        "gift_100": "100 talik Gift (83/85 stars)"
    }

    gifts = {}
    for key, title in gifts_info.items():
        p = prices["gifts"][key]
        gifts[key] = {
            "name": f"{title} - {money(p)} so'm",
            "formatted": f"{menu_emoji(key, '🎁')} {title} - {money(p)} so'm",
            "price": int(p)
        }

    premium_names = {
        "prem_3": "3 oy",
        "prem_6": "6 oy",
        "prem_12": "1 yil",
        "prem_1": "1 oy"
    }

    premium = {}
    for key, title in premium_names.items():
        p = prices["premium"][key]
        premium[key] = {
            "name": f"{title} - {money(p)} so'm",
            "formatted": f"{menu_emoji(key, '💎')} <b>{title}</b> - {money(p)} so'm",
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


def get_main_inline_menu(user_id=None):
    uid = user_id or 0
    builder = InlineKeyboardBuilder()

    def btn(text, cb, key):
        eid = menu_emojis.get(key)
        return types.InlineKeyboardButton(text=text, callback_data=cb, icon_custom_emoji_id=eid if eid else None)

    builder.row(btn(tr(uid, "deposit"), "deposit", "deposit"))
    builder.row(btn(tr(uid, "stars"), "buy_stars", "stars"), btn(tr(uid, "gift"), "buy_gift", "gift"))
    builder.row(btn(tr(uid, "premium"), "buy_premium", "premium"), btn(tr(uid, "balance"), "my_balance", "balance"))
    builder.row(btn(tr(uid, "sell"), "sell_gift_menu", "sell"), btn(tr(uid, "referral"), "referral_system", "referral"))
    builder.row(btn(tr(uid, "top"), "top_rating", "top"), btn(tr(uid, "settings_btn"), "settings", "settings"))
    builder.row(types.InlineKeyboardButton(text=tr(uid, "admin"), url=f"https://t.me/{ADMIN_USERNAME.replace('@','')}", icon_custom_emoji_id=menu_emojis.get("admin")))
    if uid == ADMIN_ID:
        builder.row(types.InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel"))
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
        f"<blockquote><b>{menu_emoji('main_title','💎')} {title.replace('💎 ','')}</b>\n\n"
        f"{trust}\n\n"
        f"{channel}\n\n"
        f"{hint}</blockquote>"
    )


def back_main_keyboard(user_id=0):
    builder = InlineKeyboardBuilder()
    eid = menu_emojis.get("back")
    builder.row(types.InlineKeyboardButton(text=tr(user_id, "back"), callback_data="back_main", icon_custom_emoji_id=eid if eid else None))
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
        types.InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        types.InlineKeyboardButton(text="🔍 Foydalanuvchi balansi", callback_data="admin_check_bal")
    )
    builder.row(
        types.InlineKeyboardButton(text="➕ Balans Qo'shish", callback_data="admin_add_bal"),
        types.InlineKeyboardButton(text="➖ Balans Ayirish", callback_data="admin_sub_bal")
    )
    builder.row(types.InlineKeyboardButton(text="💰 Narxlarni boshqarish", callback_data="admin_prices"))
    builder.row(types.InlineKeyboardButton(text="🎨 Emoji boshqarish", callback_data="admin_emojis"))
    builder.row(types.InlineKeyboardButton(text="📝 Textlarni o'zgartirish", callback_data="admin_texts"))
    builder.row(
        types.InlineKeyboardButton(text="⭐ Referal mukofoti", callback_data="admin_referral_reward"),
        types.InlineKeyboardButton(text="👤 Foydalanuvchiga xabar", callback_data="admin_user_message")
    )
    builder.row(types.InlineKeyboardButton(text="🗑 Bot xabarini o'chirish", callback_data="admin_delete_message"))
    builder.row(types.InlineKeyboardButton(text="📢 Xabar Yuborish", callback_data="admin_broadcast"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="back_main"))
    return builder.as_markup()


@dp.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback, state):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text("<b>⚙️ Admin Panel</b>\n\nKerakli bo'limni tanlang:", reply_markup=get_admin_panel_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback):
    if callback.from_user.id != ADMIN_ID:
        return
    total_money = sum(user_balances.values())
    total_stars = sum(user_stars_balances.values())
    text = (
        "<b>📊 Bot Statistikasi:</b>\n\n"
        f"👥 Barcha foydalanuvchilar: <b>{len(registered_users)} ta</b>\n"
        f"💰 Umumiy balans: <b>{money(total_money)} so'm</b>\n"
        f"⭐ Umumiy referal Stars: <b>{format_stars(total_stars)} Stars</b>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬅️ Admin Panel", callback_data="admin_panel"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


EMOJI_KEYS = {
    "deposit": "Hisob to'ldirish", "stars": "Stars olish", "gift": "Gift olish", "premium": "Premium olish",
    "balance": "Hisobim", "sell": "Gift sotish", "referral": "Referal tizimi", "top": "Top reyting",
    "settings": "Sozlamalar", "admin": "Admin", "main_title": "Asosiy menyu", "hint": "Menyu matni",
    "prem_1": "Premium 1 oy", "prem_3": "Premium 3 oy", "prem_6": "Premium 6 oy", "prem_12": "Premium 1 yil",
    "gift_15": "Gift 15", "gift_25": "Gift 25", "gift_50": "Gift 50", "gift_100": "Gift 100", "back": "Orqaga"
}


@dp.callback_query(F.data == "admin_emojis")
async def admin_emojis_handler(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    b = InlineKeyboardBuilder()
    for key, label in EMOJI_KEYS.items():
        b.row(types.InlineKeyboardButton(text=f"{label} — {menu_emojis.get(key,'standart')}", callback_data=f"emoji_edit_{key}"))
    b.row(types.InlineKeyboardButton(text="⬅️ Admin Panel", callback_data="admin_panel"))
    await callback.message.edit_text("<b>🎨 Emoji boshqarish</b>\n\nKerakli elementni tanlang.", reply_markup=b.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("emoji_edit_"))
async def emoji_edit_start(callback, state):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.replace("emoji_edit_", "")
    await state.update_data(emoji_key=key)
    await callback.message.edit_text(f"<b>🎨 {EMOJI_KEYS.get(key,key)}</b>\n\nYangi custom emoji ID ni yuboring.", reply_markup=back_main_keyboard(ADMIN_ID))
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
    key = (await state.get_data()).get('emoji_key')
    if raw == '0':
        menu_emojis.pop(key, None)
    else:
        menu_emojis[key] = raw
    save_data()
    refresh_products()
    await state.clear()
    await safe_delete(message)
    await message.answer("✅ Emoji saqlandi.", reply_markup=get_admin_panel_keyboard())


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

    unsub = await async_check_all_subs(user_id)
    if unsub:
        sub_text = (
            "<blockquote>📢 <b>Botdan foydalanish uchun kanalga obuna bo'ling.</b>\n\n"
            "👇 Kanalga obuna bo'lgach, <b>✅ Obunani tekshirish</b> tugmasini bosing.</blockquote>"
        )
        msg = await message.answer(sub_text, reply_markup=get_sub_keyboard(unsub))
        last_menu_messages[user_id] = msg.message_id
        return

    msg = await message.answer(main_menu_text(user_id), reply_markup=get_main_inline_menu(user_id))
    last_menu_messages[user_id] = msg.message_id


@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback):
    user_id = callback.from_user.id
    unsub = await async_check_all_subs(user_id)
    if not unsub:
        await callback.message.edit_text(main_menu_text(user_id), reply_markup=get_main_inline_menu(user_id))
        last_menu_messages[user_id] = callback.message.message_id
        await callback.answer("✅ Obuna tasdiqlandi!")
    else:
        await callback.answer("❌ Kanalga hali obuna bo'lmagansiz!", show_alert=True)


@dp.callback_query(F.data == "back_main")
async def back_to_main(callback, state):
    await state.clear()
    user_id = callback.from_user.id
    unsub = await async_check_all_subs(user_id)
    if unsub:
        await callback.message.edit_text(
            "<blockquote>📢 <b>Botdan foydalanish uchun kanalga obuna bo'ling.</b></blockquote>",
            reply_markup=get_sub_keyboard(unsub)
        )
    else:
        await callback.message.edit_text(main_menu_text(user_id), reply_markup=get_main_inline_menu(user_id))
    await callback.answer()


@dp.callback_query(F.data == "deposit")
async def deposit_start(callback, state):
    deposit_title = editable_text("deposit_title", "Hisob to'ldirish", callback.from_user.id)
    deposit_prompt = editable_text("deposit_prompt", "Hisobingizni qanchaga to'ldirmoqchisiz?", callback.from_user.id)
    deposit_minmax = editable_text("deposit_minmax", "🔹 Minimum: <b>1.000 so'm</b>", callback.from_user.id)
    deposit_input = editable_text("deposit_input", "✍️ Miqdorni yozing:", callback.from_user.id)
    await callback.message.edit_text(
        f"<blockquote>{menu_emoji('deposit', EMOJI_DEPOSIT_HTML)} <b>{deposit_title}</b>\n\n{deposit_prompt}\n\n{deposit_minmax}\n\n{deposit_input}</blockquote>",
        reply_markup=back_main_keyboard(callback.from_user.id)
    )
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()


@dp.message(DepositState.waiting_for_amount)
async def process_deposit_amount(message, state):
    user_id = message.from_user.id

    if not message.text or not message.text.isdigit():
        msg = await message.answer("<blockquote>⚠️ Faqat raqam kiriting!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    amount = int(message.text)
    if amount < 1000:
        msg = await message.answer("<blockquote>❌ Minimum miqdor 1.000 so'm!</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    await safe_delete(message)
    payment_id = f"{user_id}_{int(datetime.now().timestamp() * 1000)}"

    payment_card_label = editable_text("payment_card_label", "💳 <b>Karta:</b>", user_id)
    payment_owner_label = editable_text("payment_owner_label", "👤 <b>Ega:</b>", user_id)
    payment_transfer = editable_text("payment_transfer", "Kartaga <b>{amount} so'm</b> o'tkazing.", user_id).format(amount=money(amount))

    card_text = (
        f"<blockquote>{menu_emoji('deposit', EMOJI_CARD_HTML)} {payment_card_label} <code>{PAYMENT_CARD}</code>\n"
        f"{payment_owner_label} {PAYMENT_CARD_OWNER}\n\n"
        f"{EMOJI_TRANSFER_HTML} {payment_transfer}\n\n"
        "📸 <b>To'lovni amalga oshirgach, chek (skrinshot) rasmini shu yerga yuboring.</b>\n"
        "⏰ Vaqt: <b>5 daqiqa</b>.</blockquote>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel", icon_custom_emoji_id=menu_emojis.get("back")))

    await delete_previous_menu(user_id)
    msg = await message.answer(card_text, reply_markup=builder.as_markup())
    last_menu_messages[user_id] = msg.message_id

    pending_payments[payment_id] = {
        "user_id": user_id,
        "amount": amount,
        "message_id": msg.message_id,
        "status": "waiting_receipt"
    }

    await state.update_data(payment_id=payment_id)
    await state.set_state(DepositState.waiting_for_receipt)


@dp.message(DepositState.waiting_for_receipt)
async def process_deposit_receipt(message, state):
    data = await state.get_data()
    payment_id = data.get("payment_id")
    payment = pending_payments.get(payment_id)

    if not payment:
        await state.clear()
        await message.answer("<blockquote>⏰ To'lov vaqti tugagan. Yangitdan urinib ko'ring.</blockquote>", reply_markup=back_main_keyboard())
        return

    if payment.get("user_id") != message.from_user.id:
        return

    if not message.photo:
        msg = await message.answer("<blockquote>⚠️ Iltimos, chekni rasm (screenshot) ko'rinishida yuboring.</blockquote>")
        await asyncio.sleep(2)
        await safe_delete(msg)
        return

    payment["status"] = "waiting_admin"
    amount = payment["amount"]
    user_id = message.from_user.id
    username = message.from_user.username or "yoq"

    try:
        await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    admin_builder = InlineKeyboardBuilder()
    admin_builder.row(
        types.InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_pay_{payment_id}"),
        types.InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_pay_{payment_id}")
    )

    admin_text = (
        "<blockquote>🔔 <b>Yangi to'lov + chek!</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
        f"🔗 @{username}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"💰 Miqdor: <b>{money(amount)} so'm</b></blockquote>"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=admin_builder.as_markup())
    except Exception:
        pass

    await state.clear()
    await message.answer("<blockquote><b>✅ Chek qabul qilindi!</b>\n\n🔎 To'lovingiz tekshirilmoqda.</blockquote>", reply_markup=back_main_keyboard(message.from_user.id))


@dp.callback_query(F.data.startswith("approve_pay_"))
async def approve_payment(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return
    payment_id = callback.data.replace("approve_pay_", "")
    payment = pending_payments.get(payment_id)
    if not payment:
        await callback.answer("Topilmadi.", show_alert=True)
        return
    user_id = payment["user_id"]
    amount = payment["amount"]
    pending_payments.pop(payment_id, None)

    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    save_data()

    await callback.message.edit_text(f"{callback.message.text}\n\n✅ Tasdiqlandi, {money(amount)} so'm qo'shildi.")
    try:
        await bot.send_message(chat_id=user_id, text=f"🎉 Hisobingizga <b>{money(amount)} so'm</b> qo'shildi!", reply_markup=back_main_keyboard())
    except Exception:
        pass
    await callback.answer("✅")


@dp.callback_query(F.data.startswith("reject_pay_"))
async def reject_payment(callback):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return
    payment_id = callback.data.replace("reject_pay_", "")
    payment = pending_payments.get(payment_id)
    if payment:
        pending_payments.pop(payment_id, None)
        try:
            await bot.send_message(chat_id=payment["user_id"], text="❌ To'lov rad etildi.", reply_markup=back_main_keyboard())
        except Exception:
            pass
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ Rad etildi.")
    await callback.answer("❌")


@dp.callback_query(F.data == "buy_stars")
async def stars_menu(callback):
    builder = InlineKeyboardBuilder()
    for key, data in STARS_PRICES.items():
        builder.add(types.InlineKeyboardButton(text=data["name"], callback_data=f"buyprod_{key}", icon_custom_emoji_id=menu_emojis.get("stars")))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main", icon_custom_emoji_id=menu_emojis.get("back")))
    await callback.message.edit_text("⭐ <b>Stars paketini tanlang:</b>", reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "buy_gift")
async def gift_menu(callback):
    builder = InlineKeyboardBuilder()
    for key, data in GIFT_PRICES.items():
        builder.add(types.InlineKeyboardButton(text=data["name"], callback_data=f"buyprod_{key}", icon_custom_emoji_id=menu_emojis.get(key)))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main", icon_custom_emoji_id=menu_emojis.get("back")))
    await callback.message.edit_text("🎁 <b>Gift tanlang:</b>", reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "buy_premium")
async def premium_menu(callback):
    builder = InlineKeyboardBuilder()
    for key, data in PREMIUM_PRICES.items():
        builder.add(types.InlineKeyboardButton(text=data["name"], callback_data=f"buyprod_{key}", icon_custom_emoji_id=menu_emojis.get(key)))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main", icon_custom_emoji_id=menu_emojis.get("back")))
    await callback.message.edit_text("💎 <b>Premium tanlang:</b>", reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("buyprod_"))
async def select_product(callback, state):
    prod_key = callback.data.split("buyprod_", 1)[1]
    product = ALL_PRODUCTS.get(prod_key)
    if not product:
        await callback.answer("Topilmadi!", show_alert=True)
        return
    user_id = callback.from_user.id
    if user_balances.get(user_id, 0) < product["price"]:
        await callback.answer("❌ Hisobingizda mablag' yetarli emas!", show_alert=True)
        return
    await state.update_data(product=product)
    
    username = callback.from_user.username
    target = f"@{username}" if username else f"ID: {callback.from_user.id}"
    await state.update_data(target=target)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Xaridni tasdiqlash", callback_data="confirm_buy"))
    builder.row(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    
    await callback.message.edit_text(
        f"🛒 <b>Xaridni tasdiqlang:</b>\n\nMahsulot: {product['formatted']}\nNarxi: {money(product['price'])} so'm",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "confirm_buy")
async def execute_purchase(callback, state):
    user_id = callback.from_user.id
    data = await state.get_data()
    product = data.get("product")
    target = data.get("target", f"ID: {user_id}")
    if not product:
        await callback.answer("Xatolik!", show_alert=True)
        return

    price = product["price"]
    if user_balances.get(user_id, 0) < price:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)
        return

    user_balances[user_id] -= price
    save_data()
    await state.clear()

    order_id = f"{user_id}_{int(datetime.now().timestamp())}"
    active_orders[order_id] = {"user_id": user_id, "price": price, "product": product["name"]}

    await callback.message.edit_text("🎉 <b>Buyurtmangiz qabul qilindi!</b> Tez orada bajariladi.", reply_markup=back_main_keyboard())
    
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🛒 <b>Yangi xarid!</b>\nFoydalanuvchi: <a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a>\nMahsulot: {product['name']} — {money(price)} so'm"
        )
    except Exception:
        pass


@dp.callback_query(F.data == "my_balance")
async def show_balance(callback):
    bal = user_balances.get(callback.from_user.id, 0)
    await callback.message.edit_text(f"💳 Pul balansi: <b>{money(bal)} so'm</b>", reply_markup=back_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def settings_handler(callback):
    await callback.message.edit_text("⚙️ Sozlamalar", reply_markup=back_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "cancel")
async def cancel_action(callback, state):
    await state.clear()
    await callback.message.edit_text(main_menu_text(callback.from_user.id), reply_markup=get_main_inline_menu(callback.from_user.id))
    await callback.answer("Bekor qilindi.")


async def dummy_handler(request):
    return web.Response(text="Bot ishlayapti!")


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

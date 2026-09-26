import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO)

# ================= SOZLAMALAR =================
BOT_TOKEN = "8982437206:AAEegwkmLXR28Fz01cfyOH6w9LNxxQsYuTM"
ADMIN_USERNAME = "rymbyvv"
CHANNEL_URL = "https://t.me/rymbyvv_otziv"
CARD_NUMBER = "9860 3566 3465 1745"
CARD_NAME = "Elvira Kuralova"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Foydalanuvchilar balansi
user_balances = {}

def get_bal(user_id):
    return user_balances.get(user_id, 0)

# Holatlar (FSM)
class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_check = State()

# ================= ASOSIY MENYU (CUSTOM EMOJILAR BILAN) =================
def get_main_menu():
    buttons = [
        [
            InlineKeyboardButton(
                text="Stars",
                callback_data="menu_stars",
                icon_custom_emoji_id="5924870095925942277"  # Animatsiyali Stars yulduzi
            ),
            InlineKeyboardButton(
                text="Premium",
                callback_data="menu_premium",
                icon_custom_emoji_id="5370784581341422520"  # Binafsharang Premium yulduzi
            )
        ],
        [
            InlineKeyboardButton(
                text="Gift olish",
                callback_data="menu_gifts",
                icon_custom_emoji_id="5193085063998224234"  # Animatsiyali sovg'a qutisi
            ),
            InlineKeyboardButton(
                text="Hisobim",
                callback_data="menu_balance",
                icon_custom_emoji_id="5276111643732899391"  # Pul xaltasi
            )
        ],
        [
            InlineKeyboardButton(
                text="To'lovlar kanali",
                url="https://t.me/rymbyvv_otziv",
                icon_custom_emoji_id="5276428990276461681"  # Kanal / Rasm belgisi
            ),
            InlineKeyboardButton(
                text="Yordam",
                url="https://t.me/rymbyvv",
                icon_custom_emoji_id="5458865156467491802"  # Savol / Yordam belgisi
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    text = "💎 Nima olasiz, tanlang:"
    await message.answer(text, reply_markup=get_main_menu())

# ================= BO'LIMLAR =================
# 1. STARS
@dp.callback_query(F.data == "menu_stars")
async def stars_menu(call: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="50 Stars — 12,500 so'm", callback_data="buy:50 Stars:12500"),
            InlineKeyboardButton(text="100 Stars — 20,500 so'm", callback_data="buy:100 Stars:20500")
        ],
        [
            InlineKeyboardButton(text="150 Stars — 38,500 so'm", callback_data="buy:150 Stars:38500"),
            InlineKeyboardButton(text="200 Stars — 45,000 so'm", callback_data="buy:200 Stars:45000")
        ],
        [
            InlineKeyboardButton(text="250 Stars — 55,000 so'm", callback_data="buy:250 Stars:55000")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ]
    await call.message.edit_text("⭐ Kerakli <b>Stars</b> paketini tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# 2. PREMIUM
@dp.callback_query(F.data == "menu_premium")
async def prem_menu(call: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="1 Oylik — 45,000 so'm", callback_data="buy:1 Oylik Premium:45000"),
            InlineKeyboardButton(text="3 Oylik — 165,000 so'm", callback_data="buy:3 Oylik Premium:165000")
        ],
        [
            InlineKeyboardButton(text="6 Oylik — 210,000 so'm", callback_data="buy:6 Oylik Premium:210000"),
            InlineKeyboardButton(text="1 Yillik — 385,000 so'm", callback_data="buy:1 Yillik Premium:385000")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ]
    await call.message.edit_text("💎 Kerakli <b>Telegram Premium</b> muddatini tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# 3. GIFTS
@dp.callback_query(F.data == "menu_gifts")
async def gifts_menu(call: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="🐾 15 Stars Gift — 3,500", callback_data="buy:15 Stars Gift:3500"),
            InlineKeyboardButton(text="🎁 25 Stars Gift — 6,500", callback_data="buy:25 Stars Gift:6500")
        ],
        [
            InlineKeyboardButton(text="🚀 50 Stars Gift — 10,500", callback_data="buy:50 Stars Gift:10500"),
            InlineKeyboardButton(text="💎 100 Stars Gift — 20,500", callback_data="buy:100 Stars Gift:20500")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ]
    await call.message.edit_text("🎁 Yubormoqchi bo'lgan <b>Gift</b>ingizni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# ================= BUYURTMA VA USERNAME SO'RASH =================
@dp.callback_query(F.data.startswith("buy:"))
async def process_buy_step(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    item_name = parts[1]
    price = int(parts[2])
    
    await state.update_data(item_name=item_name, price=price)
    await state.set_state(OrderState.waiting_for_username)

    buttons = [
        [InlineKeyboardButton(text="👤 O'zimga", callback_data="target_self")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ]
    text = (
        "💻 Buyurtma ma'lumotlari:\n"
        f" └ 📦 Mahsulot: {item_name}\n"
        f" └ 💰 Narxi: {price:,} so'm\n\n"
        "🔮 Kimga yuboramiz?\n"
        "@ @username kiriting:"
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data == "target_self")
async def target_self_handler(call: CallbackQuery, state: FSMContext):
    u_name = call.from_user.username
    if not u_name:
        target = call.from_user.first_name
    else:
        target = f"@{u_name}"
    await finalize_order(call, state, target)

@dp.message(OrderState.waiting_for_username)
async def username_entered_handler(message: types.Message, state: FSMContext):
    target = message.text.strip()
    if not target.startswith("@"):
        target = f"@{target}"
    await finalize_order(message, state, target)

async def finalize_order(event, state: FSMContext, target: str):
    data = await state.get_data()
    item_name = data.get("item_name")
    price = data.get("price")
    user_id = event.from_user.id
    bal = get_bal(user_id)

    if bal < price:
        alert_msg = (
            "😞 Balansingiz yetarli emas!\n\n"
            f"💰 Hisobingizda: {bal:,} so'm\n"
            f"💸 Kerakli: {price:,} so'm"
        )
        if isinstance(event, CallbackQuery):
            await event.answer(alert_msg, show_alert=True)
        else:
            await event.answer(alert_msg)
        return

    # Mablag' yetarli bo'lsa
    user_balances[user_id] = bal - price
    await state.clear()
    
    success_text = (
        "✅ <b>Buyurtma muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📦 Mahsulot: <b>{item_name}</b>\n"
        f"👤 Qabul qiluvchi: <b>{target}</b>\n"
        f"💰 Yechildi: <b>{price:,} so'm</b>\n"
        f"💵 Qolgan balans: <b>{user_balances[user_id]:,} so'm</b>\n\n"
        "⚡ 5 daqiqa ichida yetkazib beriladi!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Bosh menyu", callback_data="back_main")]])
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(success_text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.answer(success_text, reply_markup=kb, parse_mode="HTML")

# ================= HISOB VA CHEK YUBORISH =================
@dp.callback_query(F.data == "menu_balance")
async def balance_view(call: CallbackQuery):
    bal = get_bal(call.from_user.id)
    u_name = call.from_user.username or "Mavjud emas"
    buttons = [
        [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="topup_balance")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ]
    text = (
        f"👤 Profilingiz: @{u_name}\n"
        f"🆔 ID: <code>{call.from_user.id}</code>\n"
        f"💵 Balansingiz: <b>{bal:,} so'm</b>"
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data == "topup_balance")
async def start_topup(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_check)
    buttons = [[InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="back_main")]]
    text = (
        "⚡ <b>Hisobni to'ldirish</b>\n\n"
        f"💳 Karta: <code>{CARD_NUMBER}</code>\n"
        f"👤 Egasi: <b>{CARD_NAME}</b>\n\n"
        "⚠️ <b>To'lovni amalga oshirib, chek skrinshotini (rasmini) shu yerga yuboring!</b>\n"
        "<i>(Faqat rasm qabul qilinadi, PDF hujjatlar o'tmaydi)</i>"
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# Rasm (Skrinshot) yuborilganda
@dp.message(OrderState.waiting_for_check, F.photo)
async def check_photo_received(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ <b>Chekingiz qabul qilindi va tekshiruvga yuborildi!</b>\n"
        "Admin tekshirib, tez orada hisobingizni to'ldirib beradi.",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

# PDF yoki Hujjat yuborilganda RAD ETISH
@dp.message(OrderState.waiting_for_check, F.document)
async def check_doc_rejected(message: types.Message):
    text = (
        "❌ <b>Xatolik! PDF yoki fayl qabul qilinmaydi.</b>\n\n"
        "Iltimos, chekning faqat <b>oddiy rasmini (skrinshotini)</b> yuboring!\n"
        f"Agar muammo bo'lsa, adminga yozing: @{ADMIN_USERNAME}"
    )
    await message.answer(text, parse_mode="HTML")

# Boshqa narsa yuborilganda
@dp.message(OrderState.waiting_for_check)
async def check_other_rejected(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekining rasmini yuboring.")

@dp.callback_query(F.data == "back_main")
async def back_main_btn(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("💎 Nima olasiz, tanlang:", reply_markup=get_main_menu())

# ================= RENDER UCHUN VEB-PORT =================
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

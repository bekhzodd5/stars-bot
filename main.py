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
# BotFather'dan olingan aniq tokenni qo'ying
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8982437206:AAEegwkmLXR28Fz01cfyOH6w9LNxxQsYuTM")
ADMIN_USERNAME = "rymbyvv"
CHANNEL_URL = "https://t.me/rymbyvv_otziv"
CARD_NUMBER = "9860 3566 3465 1745"
CARD_NAME = "Elvira Kuralova"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Foydalanuvchilar balansi
user_balances = {}

def get_bal(user_id: int) -> int:
    return user_balances.get(user_id, 0)

# Holatlar (FSM)
class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_check = State()

# ================= ASOSIY MENYU =================
def get_main_menu():
    buttons = [
        [
            InlineKeyboardButton(
                text="Stars",
                callback_data="menu_stars",
                icon_custom_emoji_id="5924870095925942277"  # Stars emoji ID
            ),
            InlineKeyboardButton(
                text="Premium",
                callback_data="menu_premium",
                icon_custom_emoji_id="5370784581341422520"  # Premium emoji ID
            )
        ],
        [
            InlineKeyboardButton(
                text="Gift olish",
                callback_data="menu_gifts",
                icon_custom_emoji_id="5193085063998224234"
            ),
            InlineKeyboardButton(
                text="Hisobim",
                callback_data="menu_balance",
                icon_custom_emoji_id="5276111643732899391"
            )
        ],
        [
            InlineKeyboardButton(
                text="To'lovlar kanali",
                url=CHANNEL_URL,
                icon_custom_emoji_id="5276428990276461681"
            ),
            InlineKeyboardButton(
                text="Yordam",
                url=f"https://t.me/{ADMIN_USERNAME}",
                icon_custom_emoji_id="5458865156467491802"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        '<tg-emoji id="5271628569754222702">💎</tg-emoji> <b>Xush kelibsiz!</b>\n\n'
        'Kerakli xizmat turini tanlang:'
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

# ================= BO'LIMLAR =================

# 1. STARS BO'LIMI
@dp.callback_query(F.data == "menu_stars")
async def stars_menu(call: CallbackQuery):
    await call.answer()  # Qotib qolmasligi uchun
    buttons = [
        [
            InlineKeyboardButton(text="⭐ 50 Stars — 12 500 so'm", callback_data="buy:50 Stars:12500"),
            InlineKeyboardButton(text="⭐ 100 Stars — 20 500 so'm", callback_data="buy:100 Stars:20500")
        ],
        [
            InlineKeyboardButton(text="⭐ 150 Stars — 38 500 so'm", callback_data="buy:150 Stars:38500"),
            InlineKeyboardButton(text="⭐ 200 Stars — 45 000 so'm", callback_data="buy:200 Stars:45000")
        ],
        [
            InlineKeyboardButton(text="⭐ 250 Stars — 55 000 so'm", callback_data="buy:250 Stars:55000")
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")
        ]
    ]
    text = (
        '<tg-emoji id="5924870095925942277">⭐</tg-emoji> <b>Stars bo\'limi</b>\n\n'
        'Kerakli Stars paketini tanlang:'
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# 2. PREMIUM BO'LIMI (3 oylik, 1 oylik va boshqalar)
@dp.callback_query(F.data == "menu_premium")
async def prem_menu(call: CallbackQuery):
    await call.answer()
    buttons = [
        [
            InlineKeyboardButton(
                text="1 Oylik — 45 000 so'm", 
                callback_data="buy:1 Oylik Premium:45000",
                icon_custom_emoji_id="5370784581341422520"  # Shu yerga 1 oylik emoji ID qo'yishingiz mumkin
            ),
            InlineKeyboardButton(
                text="3 Oylik — 165 000 so'm", 
                callback_data="buy:3 Oylik Premium:165000",
                icon_custom_emoji_id="5370784581341422520"  # 3 oylik emoji ID
            )
        ],
        [
            InlineKeyboardButton(
                text="6 Oylik — 210 000 so'm", 
                callback_data="buy:6 Oylik Premium:210000",
                icon_custom_emoji_id="5370784581341422520"  # 6 oylik emoji ID
            ),
            InlineKeyboardButton(
                text="1 Yillik — 385 000 so'm", 
                callback_data="buy:1 Yillik Premium:385000",
                icon_custom_emoji_id="5370784581341422520"  # 1 yillik emoji ID
            )
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")
        ]
    ]
    text = (
        '<tg-emoji id="5370784581341422520">💎</tg-emoji> <b>Telegram Premium xizmati</b>\n\n'
        'Kerakli obuna muddatini tanlang:'
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# 3. GIFTS BO'LIMI
@dp.callback_query(F.data == "menu_gifts")
async def gifts_menu(call: CallbackQuery):
    await call.answer()
    buttons = [
        [
            InlineKeyboardButton(text="🐾 15 Stars Gift — 3 500", callback_data="buy:15 Stars Gift:3500"),
            InlineKeyboardButton(text="🎁 25 Stars Gift — 6 500", callback_data="buy:25 Stars Gift:6500")
        ],
        [
            InlineKeyboardButton(text="🚀 50 Stars Gift — 10 500", callback_data="buy:50 Stars Gift:10500"),
            InlineKeyboardButton(text="💎 100 Stars Gift — 20 500", callback_data="buy:100 Stars Gift:20500")
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")
        ]
    ]
    text = (
        '<tg-emoji id="5193085063998224234">🎁</tg-emoji> <b>Telegram Sovg\'alari (Gifts)</b>\n\n'
        'Kerakli sovg\'ani tanlang:'
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# ================= BUYURTMA BOSILGANDA (3 OYLIK, STARS VA HOKAZO) =================
@dp.callback_query(F.data.startswith("buy:"))
async def process_buy_step(call: CallbackQuery, state: FSMContext):
    await call.answer()  # Qotishni darhol to'xtatadi!
    
    parts = call.data.split(":")
    item_name = parts[1]
    price = int(parts[2])
    
    await state.update_data(item_name=item_name, price=price)
    await state.set_state(OrderState.waiting_for_username)

    buttons = [
        [
            InlineKeyboardButton(
                text="O'zimga", 
                callback_data="target_self",
                icon_custom_emoji_id="5370784581341422520"  # O'zimga emoji ID
            )
        ],
        [
            InlineKeyboardButton(
                text="Orqaga", 
                callback_data="back_main",
                icon_custom_emoji_id="5458865156467491802"
            )
        ]
    ]

    formatted_price = f"{price:,}".replace(",", " ")

    text = (
        '<tg-emoji id="5271628569754222702">💻</tg-emoji> <b>Buyurtma maʼlumotlari:</b>\n'
        f' └ <tg-emoji id="5271779885747025897">📦</tg-emoji> Mahsulot: <b>{item_name}</b>\n'
        f' └ <tg-emoji id="5470164781631550914">💰</tg-emoji> Narxi: <b>{formatted_price} so\'m</b>\n\n'
        '<tg-emoji id="5098103318241085355">🔮</tg-emoji> <b>Kimga yuboramiz?</b>\n'
        'Iltimos, qabul qiluvchining <b>@username</b>ini yozib yuboring yoki quyidagi <b>"O\'zimga"</b> tugmasini bosing:'
    )
    
    await call.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "target_self")
async def target_self_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    u_name = call.from_user.username
    target = f"@{u_name}" if u_name else call.from_user.full_name
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
    formatted_price = f"{price:,}".replace(",", " ")

    if bal < price:
        alert_msg = (
            "⚠️ Balansingiz yetarli emas!\n\n"
            f"💰 Balansingiz: {bal:,} so'm\n"
            f"💸 Narxi: {formatted_price} so'm\n\n"
            "Iltimos, avval 'Hisobim' bo'limidan hisobingizni to'ldiring."
        )
        if isinstance(event, CallbackQuery):
            await event.answer("Balansingiz yetarli emas! Hisobni to'ldiring.", show_alert=True)
            # Balansni to'ldirishga yo'naltiruvchi tugma chiqarish
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="topup_balance")],
                [InlineKeyboardButton(text="◀️ Bosh menyu", callback_data="back_main")]
            ])
            await event.message.edit_text(alert_msg, reply_markup=kb)
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="topup_balance")],
                [InlineKeyboardButton(text="◀️ Bosh menyu", callback_data="back_main")]
            ])
            await event.answer(alert_msg, reply_markup=kb)
        return

    # Balans yetarli bo'lsa
    user_balances[user_id] = bal - price
    await state.clear()
    
    success_text = (
        '<tg-emoji id="5271628569754222702">💻</tg-emoji> <b>Buyurtmangiz qabul qilindi!</b>\n\n'
        f' └ <tg-emoji id="5271779885747025897">📦</tg-emoji> Mahsulot: <b>{item_name}</b>\n'
        f' └ <tg-emoji id="5470164781631550914">💰</tg-emoji> Narxi: <b>{formatted_price} so\'m</b>\n'
        f' └ <tg-emoji id="5460747992820629019">👤</tg-emoji> Qabul qiluvchi: <b>{target}</b>\n'
        f' └ 💵 Qolgan balans: <b>{user_balances[user_id]:,} so\'m</b>\n\n'
        '⚡ Buyurtma tez orada yetkazib beriladi!'
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Bosh menyu", callback_data="back_main")]])
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(success_text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.answer(success_text, reply_markup=kb, parse_mode="HTML")

# ================= HISOB VA TO'LDIRISH =================
@dp.callback_query(F.data == "menu_balance")
async def balance_view(call: CallbackQuery):
    await call.answer()
    bal = get_bal(call.from_user.id)
    u_name = call.from_user.username or "Mavjud emas"
    buttons = [
        [
            InlineKeyboardButton(
                text="💳 Hisobni to'ldirish", 
                callback_data="topup_balance",
                icon_custom_emoji_id="5470164781631550914"  # To'lov emoji ID
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Orqaga", 
                callback_data="back_main",
                icon_custom_emoji_id="5458865156467491802"
            )
        ]
    ]
    text = (
        '<tg-emoji id="5276111643732899391">💳</tg-emoji> <b>Sizning hisobingiz:</b>\n\n'
        f' └ <tg-emoji id="5460747992820629019">👤</tg-emoji> Foydalanuvchi: @{u_name}\n'
        f' └ 🆔 ID: <code>{call.from_user.id}</code>\n'
        f' └ <tg-emoji id="5470164781631550914">💵</tg-emoji> Balans: <b>{bal:,} so\'m</b>'
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data == "topup_balance")
async def start_topup(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(OrderState.waiting_for_check)
    buttons = [
        [
            InlineKeyboardButton(
                text="◀️ Bekor qilish", 
                callback_data="back_main",
                icon_custom_emoji_id="5458865156467491802"
            )
        ]
    ]
    text = (
        '<tg-emoji id="5470164781631550914">⚡</tg-emoji> <b>Hisobni to\'ldirish</b>\n\n'
        f'💳 Karta: <code>{CARD_NUMBER}</code>\n'
        f'👤 Egasi: <b>{CARD_NAME}</b>\n\n'
        '<tg-emoji id="5271628569754222702">📌</tg-emoji> <b>Qo\'llanma:</b>\n'
        '1. Yuqoridagi kartaga to\'lovni amalga oshiring.\n'
        '2. To\'lov chekining <b>skrinshotini (rasmini)</b> shu yerga yuboring!\n'
        '<i>(Faqat rasm qabul qilinadi, PDF hujjatlar qabul qilinmaydi)</i>'
    )
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# Rasm (Chek) kelganda
@dp.message(OrderState.waiting_for_check, F.photo)
async def check_photo_received(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        '<tg-emoji id="5271779885747025897">✅</tg-emoji> <b>Chekingiz qabul qilindi!</b>\n\n'
        'Admin chekni tekshirib, tez orada balansingizga pulni tushirib beradi.'
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

# PDF yoki Hujjat kelganda rad etish
@dp.message(OrderState.waiting_for_check, F.document)
async def check_doc_rejected(message: types.Message):
    text = (
        '❌ <b>PDF yoki fayl qabul qilinmaydi!</b>\n\n'
        'Iltimos, to\'lov chekining oddiy <b>rasmini (skrinshotini)</b> yuboring.'
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(OrderState.waiting_for_check)
async def check_other_rejected(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekining rasmini yuboring.")

@dp.callback_query(F.data == "back_main")
async def back_main_btn(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    text = (
        '<tg-emoji id="5271628569754222702">💎</tg-emoji> <b>Asosiy menyu</b>\n\n'
        'Kerakli xizmat turini tanlang:'
    )
    await call.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="HTML")

# ================= RENDER SERVE QISMI =================
async def handle(request):
    return web.Response(text="Bot is online and running!")

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

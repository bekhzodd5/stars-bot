import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO)

# ================= SOZLAMALAR =================
BOT_TOKEN = "8982437206:AAHG7cnaU_QkX9eCyW_d6SVhOv5bGnm4M_s"
ADMIN_USERNAME = "rymbyvv"
CARD_NUMBER = "9860 3566 3465 1745"
CARD_NAME = "Elvira Kuralova."

bot = Bot(token=8982437206:AAHG7cnaU_QkX9eCyW_d6SVhOv5bGnm4M_s)
dp = Dispatcher()

# Foydalanuvchilar balansi
user_balances = {}

def get_balance(user_id):
    return user_balances.get(user_id, 0)

# ================= ASOSIY MENYU =================
def main_menu(user_id):
    bal = get_balance(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="cat_stars")],
        [InlineKeyboardButton(text="💎 Telegram Premium", callback_data="cat_premium")],
        [InlineKeyboardButton(text="🎁 Telegram Gifts", callback_data="cat_gifts")],
        [InlineKeyboardButton(text="💰 Hisobim: " + str(bal) + " so'm", callback_data="my_balance")],
        [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="topup_balance")],
        [InlineKeyboardButton(text="👨‍💻 Admin bilan aloqa", url="https://t.me/" + ADMIN_USERNAME)]
    ])
    return kb

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name or "Mijoz"
    text = (
        "👋 Salom, <b>" + user_name + "</b>!\n\n"
        "🌟 <b>Star Bozor O'z</b> rasmiy botiga xush kelibsiz.\n"
        "Bu yerda Stars, Premium va Giftlarni sotib olishingiz mumkin."
    )
    await message.answer(
        text,
        reply_markup=main_menu(message.from_user.id),
        parse_mode="HTML"
    )

# ================= HISOB VA TO'LDIRISH =================
@dp.callback_query(F.data == "my_balance")
async def balance_handler(call: CallbackQuery):
    bal = get_balance(call.from_user.id)
    u_name = call.from_user.username if call.from_user.username else "Mavjud emas"
    u_id = str(call.from_user.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 To'ldirish", callback_data="topup_balance")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])
    
    text = (
        "👤 Profilingiz: @" + u_name + "\n"
        "🆔 ID: <code>" + u_id + "</code>\n"
        "💵 Balansingiz: <b>" + str(bal) + " so'm</b>"
    )
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "topup_balance")
async def topup_handler(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lov qildim (Chek yuborish)", url="https://t.me/" + ADMIN_USERNAME)],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])
    text = (
        "⚡ <b>Hisobni to'ldirish</b>\n\n"
        "💳 Karta: <code>" 9860 3566 3465 1745 "</code>\n"
        "👤 Egasi: <b>" Elvira Kuralova "</b>\n\n"
        "⚠️ <b>Diqqat:</b> Ushbu rekvizitga to'lov qilish uchun sizda <b>5 daqiqa</b> vaqt bor!\n"
        "To'lovni amalga oshirgach, chekni adminga yuboring, hisobingiz to'ldirib beriladi."
    )
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ================= BO'LIMLAR =================
@dp.callback_query(F.data == "cat_stars")
async def stars_handler(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 50 Stars — 12,500 so'm", callback_data="buy_item:Stars 50:12500")],
        [InlineKeyboardButton(text="⭐ 100 Stars — 20,500 so'm", callback_data="buy_item:Stars 100:20500")],
        [InlineKeyboardButton(text="⭐ 250 Stars — 55,000 so'm", callback_data="buy_item:Stars 250:55000")],
        [InlineKeyboardButton(text="⭐ 500 Stars — 105,000 so'm", callback_data="buy_item:Stars 500:105000")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])
    await call.message.edit_text("⭐ Kerakli <b>Stars</b> paketini tanlang:", reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "cat_premium")
async def premium_handler(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 1 Oylik — 45,000 so'm", callback_data="buy_item:Prem 1 Oy:45000")],
        [InlineKeyboardButton(text="💎 3 Oylik — 165,000 so'm", callback_data="buy_item:Prem 3 Oy:165000")],
        [InlineKeyboardButton(text="💎 6 Oylik — 210,000 so'm", callback_data="buy_item:Prem 6 Oy:210000")],
        [InlineKeyboardButton(text="💎 1 Yillik — 385,000 so'm", callback_data="buy_item:Prem 1 Yil:385000")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])
    await call.message.edit_text("💎 Kerakli <b>Telegram Premium</b> muddatini tanlang:", reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "cat_gifts")
async def gifts_handler(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐾 15 Stars Gift — 3,500 so'm", callback_data="buy_item:Gift 15:3500")],
        [InlineKeyboardButton(text="🎁 25 Stars Gift — 6,500 so'm", callback_data="buy_item:Gift 25:6500")],
        [InlineKeyboardButton(text="🚀 50 Stars Gift — 10,500 so'm", callback_data="buy_item:Gift 50:10500")],
        [InlineKeyboardButton(text="💎 100 Stars Gift — 20,500 so'm", callback_data="buy_item:Gift 100:20500")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
    ])
    await call.message.edit_text("🎁 Yubormoqchi bo'lgan <b>Gift</b>ingizni tanlang:", reply_markup=kb, parse_mode="HTML")

# ================= XARID QILISH =================
@dp.callback_query(F.data.startswith("buy_item:"))
async def process_buy(call: CallbackQuery):
    parts = call.data.split(":")
    item_name = parts[1]
    price = int(parts[2])
    user_id = call.from_user.id
    bal = get_balance(user_id)

    if bal < price:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="topup_balance")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")]
        ])
        await call.answer("Mablag' yetarli emas!", show_alert=True)
        text = (
            "❌ <b>Hisobingizda yetarli mablag' yo'q!</b>\n\n"
            "Mahsulot: <b>" + item_name + "</b>\n"
            "Narxi: <b>" + str(price) + " so'm</b>\n"
            "Balansingiz: <b>" + str(bal) + " so'm</b>\n\n"
            "Xarid uchun avval hisobingizni to'ldiring."
        )
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        user_balances[user_id] = bal - price
        new_bal = user_balances[user_id]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Bosh sahifa", callback_data="back_main")]
        ])
        text = (
            "✅ <b>Xarid muvaffaqiyatli amalga oshirildi!</b>\n\n"
            "Mahsulot: <b>" + item_name + "</b>\n"
            "Yechildi: <b>" + str(price) + " so'm</b>\n"
            "Qoldiq balans: <b>" + str(new_bal) + " so'm</b>\n\n"
            "Mahsulot 5 daqiqa ichida profilingizga yetkaziladi!"
        )
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "back_main")
async def back_to_main(call: CallbackQuery):
    await call.message.edit_text(
        "🌟 <b>Star Bozor O'z</b> asosiy menyusi:",
        reply_markup=main_menu(call.from_user.id),
        parse_mode="HTML"
    )

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

    # Eski ulanishlarni tozalash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

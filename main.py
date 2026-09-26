import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    # aiohttp web server Render porti uchun
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())               
import asyncio   
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Sizning bot tokeningiz joylandi:
BOT_TOKEN = "8982437206:AAFuUkuaAYESseNzo9iMDmZHK9dqKn2GU7g"
ADMIN_USERNAME = "rymbyvv"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Boshlang'ich menyu
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Stars xarid qilish", callback_data="buy_stars")],
        [InlineKeyboardButton(text="💎 Premium xarid qilish", callback_data="buy_premium")],
        [InlineKeyboardButton(text="👥 Obunachilar (Kafolatli)", callback_data="buy_subs")],
        [InlineKeyboardButton(text="💬 Admin bilan aloqa", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        f"Stars, Premium va Obunachilar do'konimizga xush kelibsiz.\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data == "buy_stars")
async def stars_handler(call: types.CallbackQuery):
    await call.message.answer(
        "⭐ **Telegram Stars Paketlari:**\n\n"
        "• 50 Stars — 12,500 UZS\n"
        "• 100 Stars — 20,500 UZS\n"
        "• 150 Stars — 38,500 UZS\n"
        "• 200 Stars — 45,000 UZS\n\n"
        f"Xarid qilish uchun adminga yozing: @{ADMIN_USERNAME}"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_premium")
async def prem_handler(call: types.CallbackQuery):
    await call.message.answer(
        "💎 **Telegram Premium Paketlari:**\n\n"
        "• 1 Oylik — 45,000 UZS\n"
        "• 3 Oylik — 165,000 UZS\n"
        "• 6 Oylik — 210,000 UZS\n"
        "• 1 Yillik — 385,000 UZS\n\n"
        f"Xarid qilish uchun adminga yozing: @{ADMIN_USERNAME}"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_subs")
async def subs_handler(call: types.CallbackQuery):
    await call.message.answer(
        "👥 **Kanal Obunachilari (90 kun kafolat 🛡️):**\n\n"
        "• 1 000 obunachi (1k) — 15,000 UZS\n"
        "• 2 000 obunachi (2k) — 25,000 UZS\n"
        "• 3 000 obunachi (3k) — 35,000 UZS\n\n"
        f"Buyurtma berish uchun adminga yozing: @{ADMIN_USERNAME}"
    )
    await call.answer()

# Render bepul serverida 24/7 turishi uchun mini-veb server:
async def handle_ping(request):
    return web.Response(text="Bot faol ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

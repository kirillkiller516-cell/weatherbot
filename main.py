import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

# ТВОИ ДАННЫЕ ИЗ СКРИНШОТОВ
TOKEN = "8713876155:AAGD-jf6GzQniAAoRV88cqr5iGSOxOXmgNw"
API_KEY = "366885df4000302b55977926b668038c"
MY_ID = 5459341496
BRO_ID = 6871387615

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=uk"
        res = requests.get(url).json()
        if res.get("main"):
            temp = res["main"]["temp"]
            desc = res["weather"][0]["description"]
            return f"{temp}°C, {desc}"
        return "не вдалося отримати дані"
    except:
        return "помилка зв'язку"

def get_fishing_forecast():
    w = get_weather(49.74, 34.13)
    return f"🎣 **Звіт для рибалки (Панасівка):**\nПогода зараз: {w}\n\nКороп та карась сьогодні мають бути активні. Вдалого клювання!"

def get_school_calendar():
    w = get_weather(49.74, 34.13)
    return f"📚 **Шкільний календар:**\nСьогодні в Панасівці: {w}\n\nГарного дня на уроках!"

@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = [[KeyboardButton(text="🎣 Рибальський звіт")], [KeyboardButton(text="📚 Шкільний календар")]]
    reply_markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await msg.answer("Привіт! Я твій бот, тепер працюю в хмарі 24/7.", reply_markup=reply_markup)

@dp.message(lambda msg: msg.text == "🎣 Рибальський звіт")
async def send_fishing(msg: types.Message):
    await msg.answer(get_fishing_forecast(), parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📚 Шкільний календар")
async def send_school(msg: types.Message):
    await msg.answer(get_school_calendar(), parse_mode="Markdown")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(MY_ID, get_fishing_forecast(), parse_mode="Markdown")), 'cron', hour=7, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(BRO_ID, get_school_calendar(), parse_mode="Markdown")), 'cron', hour=8, minute=0)
    scheduler.start()
    
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    asyncio.create_task(site.start())

    print(f"Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

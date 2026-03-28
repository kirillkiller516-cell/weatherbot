import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

# Конфигурация
TOKEN = "ТВОЙ_ТОКЕН_БОТА"  # Вставь сюда свой токен
API_KEY = "ТВОЙ_КЛЮЧ_OPENWEATHER" # Вставь свой ключ погоды
MY_ID = 5459341496  # Твой ID
BRO_ID = 6871387615 # ID брата

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# --- ФУНКЦИИ ПОГОДЫ (оставляем как были) ---
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=uk"
    res = requests.get(url).json()
    if res.get("main"):
        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"]
        return f"{temp}°C, {desc}"
    return "Не вдалося отримати дані"

def get_fishing_forecast():
    w = get_weather(49.7, 34.1) # Координаты Панасовки
    return f"🎣 **Звіт для рибалки (Панасівка):**\nЗараз: {w}\nКороп сьогодні активний!"

def get_school_calendar():
    w = get_weather(49.7, 34.1)
    return f"📚 **Шкільний календар:**\nПогода для навчання: {w}\nВдалих уроків!"

# --- ОБРАБОТЧИКИ КНОПОК ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = [
        [KeyboardButton(text="🎣 Рибальський звіт")],
        [KeyboardButton(text="📚 Шкільний календар")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await msg.answer("Привіт! Я твій бот на сервері 24/7.", reply_markup=reply_markup)

@dp.message(lambda msg: msg.text == "🎣 Рибальський звіт")
async def send_fishing(msg: types.Message):
    await msg.answer(get_fishing_forecast(), parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📚 Шкільний календар")
async def send_school(msg: types.Message):
    await msg.answer(get_school_calendar(), parse_mode="Markdown")

# --- СЕРВЕР-ЗАГЛУШКА ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Бот працює 24/7!")

async def main():
    # Настройка расписания (07:00 и 08:00)
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(MY_ID, get_fishing_forecast(), parse_mode="Markdown")), 'cron', hour=7, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(BRO_ID, get_school_calendar(), parse_mode="Markdown")), 'cron', hour=8, minute=0)
    scheduler.start()
    
    # Запуск веб-сервера для Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    asyncio.create_task(site.start())

    print(f"Бот запущений на порту {port}!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

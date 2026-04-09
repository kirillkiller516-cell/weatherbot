import os
import asyncio
import aiohttp
import random
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from aiohttp import web

# --- НАСТРОЙКИ ---
API_TOKEN = '8713876155:AAGD-jf6GzQniAAoRV88cqr5iGSOxOXmgNw' 
WEATHER_KEY = 'e28ac47d86461c98b2ed828671aae42b'            
MY_ID = 8668738378                                         
CITY = "Panasivka,UA" 
UKRAINE_TZ = pytz.timezone('Europe/Kyiv')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=UKRAINE_TZ)

FISHING_TIPS = [
    "🎣 Порада: На карася краще брати мастирку з анісом.",
    "🎣 Порада: Якщо вітер північний, шукай рибу на глибині.",
    "🎣 Порада: Не забувай про підгодовування — це 50% успіху.",
    "🎣 Порада: Короп любить солодкі запахи, спробуй кукурудзу з медом."
]

def get_wind_direction(deg):
    directions = ["Північний", "Північно-східний", "Східний", "Південно-східний", "Південний", "Південно-західний", "Західний", "Північно-західний"]
    index = int((deg + 22.5) / 45) % 8
    return directions[index]

async def get_weather_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_KEY}&units=metric&lang=uk"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
    except:
        return None

async def get_fishing_forecast():
    res = await get_weather_data()
    if not res: return "🚨 Помилка отримання даних (перевір пошту OpenWeather)."
    
    temp = res['main']['temp']
    press = res['main']['pressure'] * 0.750064
    wind_speed = res['wind']['speed']
    wind_deg = res['wind'].get('deg', 0)
    wind_dir = get_wind_direction(wind_deg)
    desc = res['weather'][0]['description']
    status = "✅ Можна їхати!" if 742 <= press <= 758 and wind_speed <= 6 else "⚠️ Умови складні"
    
    now = datetime.now(UKRAINE_TZ)
    return (f"🎣 **РИБАЛЬСЬКИЙ МОНІТОР**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"⏰ Оновлено: {now.strftime('%H:%M:%S')}\n"
            f"☁️ Стан: {desc.capitalize()}\n"
            f"🌡 Темп: {temp}°C | 💎 Тиск: {int(press)}\n"
            f"🚩 Вітер: {wind_dir}, {wind_speed} м/с\n"
            f"━━━━━━━━━━━━━━━\n"
            f"**ВЕРДИКТ: {status}**\n\n"
            f"{random.choice(FISHING_TIPS)}")

async def get_school_calendar():
    res = await get_weather_data()
    if not res: return "🚨 Помилка отримання даних."
    
    now = datetime.now(UKRAINE_TZ)
    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    weekday = days[now.weekday()]
    
    temp = res['main']['temp']
    clouds = res['clouds']['all']
    cloud_text = "Безхмарно ☀️"
    if 10 < clouds <= 30: cloud_text = "Невелика 🌤"
    elif 30 < clouds <= 70: cloud_text = "Мінлива ⛅️"
    elif clouds > 70: cloud_text = "Суцільна ☁️"

    return (f"📅 **ШКІЛЬНИЙ КАЛЕНДАР ПОГОДИ**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🗓 Дата: {now.strftime('%d.%m.%Y')} ({weekday})\n"
            f"🌡 Температура: {int(temp)}°C\n"
            f"☁️ Хмарність: {cloud_text}\n"
            f"🚩 Вітер: {get_wind_direction(res['wind'].get('deg', 0))}\n"
            f"━━━━━━━━━━━━━━━")

async def send_daily_reports():
    fish = await get_fishing_forecast()
    school = await get_school_calendar()
    try:
        await bot.send_message(MY_ID, fish, parse_mode="Markdown")
        await asyncio.sleep(1)
        await bot.send_message(MY_ID, school, parse_mode="Markdown")
    except:
        pass

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🎣 Рибальський звіт"))
    builder.row(types.KeyboardButton(text="📚 Шкільний календар"))
    await message.answer("Бот активний! Обирай звіт:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda m: m.text == "🎣 Рибальський звіт")
async def manual_fishing(m: types.Message):
    await m.answer(await get_fishing_forecast(), parse_mode="Markdown")

@dp.message(lambda m: m.text == "📚 Шкільний календар")
async def manual_school(m: types.Message):
    await m.answer(await get_school_calendar(), parse_mode="Markdown")

async def handle(request):
    return web.Response(text="Bot is live!")

async def main():
    # Настройка рассылки на 7:00 утра по Киеву
    scheduler.add_job(send_daily_reports, 'cron', hour=7, minute=0)
    scheduler.start()
    
    # Запуск веб-сервера для Render и UptimeRobot
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"Бот запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import requests
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# --- НАЛАШТУВАННЯ ---
API_TOKEN = '8713876155:AAGD-jf6GzQniAAoRV88cqr5iGSOxOXmgNw' 
WEATHER_KEY = 'e28ac47d86461c98b2ed828671aae42b'            
MY_ID = 6874659279                                         
BRO_ID = 6874659279  # Заміни на ID брата
CITY = "Panasivka,UA" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

FISHING_TIPS = [
    "🎣 Порада: На карася краще брати мастирку з анісом.",
    "🎣 Порада: Якщо вітер північний, шукай рибу на глибині.",
    "🎣 Порада: Не забувай про підгодовування — це 50% успіху.",
    "🎣 Порада: Короп любить солодкі запахи, спробуй кукурудзу з медом."
]

def get_wind_direction(deg):
    directions = [
        "Північний", "Північно-східний", "Східний", "Південно-східний",
        "Південний", "Південно-західний", "Західний", "Північно-західний"
    ]
    index = int((deg + 22.5) / 45) % 8
    return directions[index]

def get_fishing_forecast():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_KEY}&units=metric&lang=uk"
        res = requests.get(url).json()
        temp = res['main']['temp']
        press = res['main']['pressure'] * 0.750064
        wind_speed = res['wind']['speed']
        wind_deg = res['wind'].get('deg', 0)
        wind_dir = get_wind_direction(wind_deg)
        desc = res['weather'][0]['description']
        status = "✅ Можна їхати!" if 742 <= press <= 758 and wind_speed <= 6 else "⚠️ Умови складні"
        
        return (f"🎣 **РИБАЛЬСЬКИЙ МОНІТОР**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏰ Оновлено: {datetime.now().strftime('%H:%M:%S')}\n"
                f"☁️ Стан: {desc.capitalize()}\n"
                f"🌡 Темп: {temp}°C | 💎 Тиск: {int(press)}\n"
                f"🚩 Вітер: {wind_dir}, {wind_speed} м/с\n"
                f"━━━━━━━━━━━━━━━\n"
                f"**ВЕРДИКТ: {status}**\n\n"
                f"{random.choice(FISHING_TIPS)}")
    except: return "🚨 Помилка отримання даних."

def get_school_calendar():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_KEY}&units=metric&lang=uk"
        res = requests.get(url).json()
        
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        weekday = days[datetime.now().weekday()]
        date_str = datetime.now().strftime("%d.%m.%Y")
        
        temp = res['main']['temp']
        wind_deg = res['wind'].get('deg', 0)
        wind_dir = get_wind_direction(wind_deg)
        clouds = res['clouds']['all']
        
        rain = res.get('rain', {}).get('1h', 0)
        snow = res.get('snow', {}).get('1h', 0)
        osadi = "—"
        if rain > 0: osadi = "Дощ 🌧"
        elif snow > 0: osadi = "Сніг ❄️"
        
        cloud_text = "Безхмарно ☀️"
        if 10 < clouds <= 30: cloud_text = "Невелика 🌤"
        elif 30 < clouds <= 70: cloud_text = "Мінлива ⛅️"
        elif clouds > 70: cloud_text = "Суцільна ☁️"

        return (f"📅 **ШКІЛЬНИЙ КАЛЕНДАР ПОГОДИ**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🗓 Дата: {date_str} ({weekday})\n"
                f"🌡 Температура повітря: {int(temp)}°C\n"
                f"☁️ Хмарність: {cloud_text}\n"
                f"💧 Опади: {osadi}\n"
                f"🚩 Вітер: {wind_dir}\n"
                f"━━━━━━━━━━━━━━━")
    except: return "🚨 Помилка отримання даних."

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🎣 Рибальський звіт"))
    builder.row(types.KeyboardButton(text="📚 Шкільний календар"))
    await message.answer("Привіт! Оновив формат шкільного календаря.", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda message: message.text == "🎣 Рибальський звіт")
async def manual_fishing(message: types.Message):
    await message.answer(get_fishing_forecast(), parse_mode="Markdown")

@dp.message(lambda message: message.text == "📚 Шкільний календар")
async def manual_school(message: types.Message):
    await message.answer(get_school_calendar(), parse_mode="Markdown")

async def main():
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(MY_ID, get_fishing_forecast(), parse_mode="Markdown")), 'cron', hour=7, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(bot.send_message(BRO_ID, get_school_calendar(), parse_mode="Markdown")), 'cron', hour=8, minute=0)
    scheduler.start()
    print("Бот запущений! Все працює коректно.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import os
import asyncio
import random
import urllib.request
import fasttext
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# Telegram токен берём из переменной Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Путь к модели fastText (оставляем для надёжности, но можно и без неё)
MODEL_PATH = "lid.176.bin"
MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

if not os.path.exists(MODEL_PATH):
    print("📥 Скачиваю модель fastText...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

model = fasttext.load_model(MODEL_PATH)

# Казахские буквы
KAZ_ONLY = set("әңгғқөүұһі")

# Фразы
PHRASES = [
    "Розенбаум, қазақша жаз",
    "Қазақша жазшиш, ақұдай",
    "Қазақша бола ма? Па руски түсінбеймін",
    "Yo nigga, stop being slave of russians and use only Kazakh language",
    "Маған адин адиной, два двайной курини донор. Етін даахуя қылып салшы, мақұл ма? Қазақпыз ғой!",
    "Арамызда бір орыс отырса бір топ қазақ болып орысша сөйлеп кететін сорлы халықпыз ғой",
    "Дедуля, спасибо за то, что я теперь священник!",
    "قازاقشا جاز",
    "Челюсть не та?",
]

# Последний ответ в каждом чате
last_trigger_time = {}

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Сәлем! Қазақша жазуды қадағалаймын 👀")

def is_kazakh(text: str) -> bool:
    """Проверяем, есть ли казахские буквы"""
    return any(ch in KAZ_ONLY for ch in text.lower())

@dp.message()
async def detect_language(message: Message):
    text = message.text
    if not text:
        return

    chat_id = message.chat.id
    now = asyncio.get_event_loop().time()

    # Если нет казахских букв → считаем, что это русский
    if not is_kazakh(text):
        if chat_id not in last_trigger_time or (now - last_trigger_time[chat_id]) > 120:
            last_trigger_time[chat_id] = now
            phrase = random.choice(PHRASES)
            await message.answer(phrase)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

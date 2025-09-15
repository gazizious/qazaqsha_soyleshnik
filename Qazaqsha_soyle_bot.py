import os
import asyncio
import random
import fasttext
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# Загружаем токен из Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MODEL_PATH = "lid.176.bin"
if not os.path.exists(MODEL_PATH):
    import urllib.request
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    urllib.request.urlretrieve(url, MODEL_PATH)
model = fasttext.load_model(MODEL_PATH)

# Фразы, которые бот будет выдавать
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

# Хранилище таймеров по чатам
last_trigger_time = {}

# Порог уверенности для fastText
THRESHOLD = 0.75

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Салем! Я слежу, чтобы писали қазақша 🙂")

@dp.message()
async def detect_language(message: Message):
    text = message.text
    if not text:
        return

    # Определяем язык
    prediction = model.predict(text, k=1)
    lang = prediction[0][0].replace("__label__", "")
    confidence = prediction[1][0]

    # Проверяем только если русский и уверенность достаточная
    if lang == "ru" and confidence >= THRESHOLD:
        now = asyncio.get_event_loop().time()
        chat_id = message.chat.id

        # Проверка — прошло ли 2 минуты с последнего триггера
        if chat_id not in last_trigger_time or (now - last_trigger_time[chat_id]) > 120:
            last_trigger_time[chat_id] = now
            phrase = random.choice(PHRASES)
            await message.answer(phrase)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

import os
import asyncio
import random
import fasttext
import urllib.request
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# Telegram токен берём из переменной Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Путь к модели fastText
MODEL_PATH = "lid.176.bin"
MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

# Скачиваем модель, если её нет
if not os.path.exists(MODEL_PATH):
    print("📥 Скачиваю модель fastText...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

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

# Храним время последнего ответа для каждого чата
last_trigger_time = {}
THRESHOLD = 0.75  # порог уверенности fastText

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Сәлем! Мені чатқа қосып, қазақ тілі қолданысын қадағалайық!")

@dp.message()
async def detect_language(message: Message):
    text = message.text
    if not text:
        return

    # Определяем язык
    prediction = model.predict(text, k=1)
    lang = prediction[0][0].replace("__label__", "")
    confidence = prediction[1][0]

    if lang == "ru" and confidence >= THRESHOLD:
        now = asyncio.get_event_loop().time()
        chat_id = message.chat.id

        # Раз в 2 минуты на чат
        if chat_id not in last_trigger_time or (now - last_trigger_time[chat_id]) > 120:
            last_trigger_time[chat_id] = now
            phrase = random.choice(PHRASES)
            await message.answer(phrase)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

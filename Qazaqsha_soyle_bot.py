import os
import time
import random
import urllib.request
import fasttext
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# --- Настройки ---
TOKEN = os.getenv("TOKEN")  # токен задаём через Railway Variables
MODEL_PATH = "lid.176.bin"
MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

# Фразы для ответа
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

# Таймер для ограничения частоты сообщений
last_reply_time = 0
COOLDOWN = 120  # секунд (2 минуты)


# --- Проверка и загрузка модели ---
def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Скачиваю fastText модель (~600MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Модель скачана.")
    return fasttext.load_model(MODEL_PATH)


model = ensure_model()


# --- Обработчик сообщений ---
async def check_message(update, context):
    global last_reply_time
    text = update.message.text
    if not text:
        return

    # Предсказание языка
    prediction = model.predict(text.replace("\n", " "), k=2)
    lang = prediction[0][0].replace("__label__", "")
    prob = prediction[1][0]

    # Проверка русского языка
    if lang == "ru" and prob >= 0.75:
        now = time.time()
        if now - last_reply_time >= COOLDOWN:
            last_reply_time = now
            phrase = random.choice(PHRASES)
            await update.message.reply_text(phrase)


# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
    app.run_polling()


if __name__ == "__main__":
    main()

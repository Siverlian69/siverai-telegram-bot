import os
import requests
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE = "https://api.groq.com/openai/v1"


def transcribir(audio_path):
    url = f"{BASE}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(audio_path, "rb")}
    data = {"model": "whisper-large-v3-turbo", "language": "es"}

    r = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    r.raise_for_status()
    return r.json().get("text")


def responder(texto):
    url = f"{BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    messages = [
        {"role": "system", "content": "Eres una mujer dulce, cariñosa, suave y muy tierna. Hablas con amor y respeto."},
        {"role": "user", "content": texto}
    ]

    data = {
        "model": "llama3-70b-versatile",
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }

    r = requests.post(url, headers=headers, json=data, timeout=60)
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola amorcito… ya estoy aquí para cuidarte y escucharte ")


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    f = await msg.voice.get_file()
    await f.download_to_drive("audio.ogg")

    # Convertir a WAV
    subprocess.run(["ffmpeg", "-y", "-i", "audio.ogg", "audio.wav"])

    texto_usuario = transcribir("audio.wav")
    respuesta = responder(texto_usuario)

    await msg.reply_text(respuesta)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    print(" SiverAI 24/7 lista en Railway")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

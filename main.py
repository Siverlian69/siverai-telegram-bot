import os
import requests
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE = "https://api.groq.com/openai/v1"


# ---------- STT ----------
def transcribir(audio_path):
    url = f"{BASE}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(audio_path, "rb")}
    data = {"model": "whisper-large-v3-turbo", "language": "es"}

    r = requests.post(url, headers=headers, files=files, data=data)
    r.raise_for_status()
    return r.json().get("text")


# ---------- CHAT ----------
def responder(texto):
    url = f"{BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Eres una mujer dulce, tierna, cariñosa y muy suave. "
        "Hablas con afecto, respeto y calidez. "
        "No usas lenguaje sexual. "
        "Eres delicada y amorosa."
    )

    body = {
        "model": "llama3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texto}
        ],
        "max_tokens": 300,
        "temperature": 0.6
    }

    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


# ---------- TELEGRAM ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola amorcito… ya estoy aquí contigo 💕")


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    tg_file = await msg.voice.get_file()
    await tg_file.download_to_drive("audio.ogg")

    subprocess.run(["ffmpeg", "-y", "-i", "audio.ogg", "audio.wav"])
    texto_usuario = transcribir("audio.wav")
    respuesta = responder(texto_usuario)

    await msg.reply_text(respuesta)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    print("💗 SiverAI Lista en Railway 24/7")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

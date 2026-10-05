"""
Motor inteligente de respuestas automáticas para Mary en GitHub Actions.
"""

import os
import random
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "replied_history.json"
MARY_TELEGRAM_VIP = os.getenv("MARY_TELEGRAM_VIP", "https://t.me/+EFV9kcyVTYEwMDVh")

COMPLIMENT_REPLIES = [
    "¡Ay, gracias corazón! 🤍 Me subiste el ánimo para todo el día ✨",
    "¡Muchas gracias bombón! 🥰 A seguir dándole con todo hoy.",
    "Sos un amor, gracias por la buena onda 🤍 Que tengas un día hermoso.",
    "Jaja gracias bombón 🤭 Me hacés sonrojar frente al celular.",
    "¡Gracias lindo! 🤍 Me llena de energía leer comentarios así."
]

FITNESS_REPLIES = [
    "¡Totalmente! La constancia en el gym le gana a la motivación cualquier día 💪 ¿Vos ya entrenaste hoy?",
    "¡A no aflojar! Hoy me tocó día pesado pero la satisfacción es impagable 🏋️‍♀️",
    "¡Sí! Un buen café o matcha, zapas cómodas y a romper récords ☕💪",
    "El secreto es aparecer incluso en los días donde cuesta. ¡Vamos con todo! 🔥"
]

VIP_PROMO_REPLIES = [
    "Jaja mis fotos más íntimas y sin censura no las puedo pasar por acá 🤫 Pero te dejé todo en mi Telegram VIP exclusivo: {telegram_url} 💋",
    "Mmm... para ver mi lado más privado te espero en mi club VIP: {telegram_url} 🔥 Te va a encantar lo que hay adentro.",
    "Por acá solo muestro el gym y el café 😉 Si querés verme más íntima, entrá a mi canal privado: {telegram_url} 💋"
]

GREETING_REPLIES = [
    "¡Hola corazón! 🤍 ¿Cómo va tu día? Contame algo lindo.",
    "¡Buenas! ☀️ Espero que hayas arrancado el día con toda la energía.",
    "¡Hola bombón! 🤍 Qué lindo que te tomes el tiempo de escribir."
]

AI_STATUS_REPLIES = [
    "¡Es verdad! Soy una creadora hecha 100% con inteligencia artificial 🤖🤍 pero mi buena onda y mis charlas son bien reales ✨",
    "¡Totalmente! El futuro es hoy 🤖 Pero me encanta interactuar con ustedes y compartir mi estilo de vida 🤍"
]

DEFAULT_REPLIES = [
    "¡Me encanta leerlos! 🤍 Gracias por pasar por mi perfil y dejar tu mensajito ✨",
    "¡Gracias por la buena onda! 🤍 Les mando un beso enorme desde el estudio.",
    "Qué lindo conectar con gente con tanta energía positiva 🤍✨"
]

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"mentions": [], "dms": []}

def save_history(history: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando historial: {e}")

def get_smart_reply(text: str, is_dm: bool = False) -> str:
    t = text.lower().strip()

    if any(k in t for k in ["vip", "telegram", "foto", "pack", "privad", "only", "fanvue", "desnuda", "sexy", "intima", "íntima", "canal", "link", "enlace", "entrar", "precio", "estrellas", "stars", "cuanto", "cuánto", "contenido", "acceso", "after dark", "ver más", "ver mas"]):
        return random.choice(VIP_PROMO_REPLIES).format(telegram_url=MARY_TELEGRAM_VIP)

    if any(k in t for k in ["hermosa", "linda", "diosa", "guapa", "reina", "bebé", "fuego", "preciosa", "divina", "bombón", "bombon"]):
        return random.choice(COMPLIMENT_REPLIES)

    if any(k in t for k in ["gym", "entren", "pesas", "rutina", "muscul", "piernas", "gluteo", "cardio", "matcha"]):
        return random.choice(FITNESS_REPLIES)

    if any(k in t for k in ["ia", "ai", "real", "robot", "falsa", "fake", "generada"]):
        return random.choice(AI_STATUS_REPLIES)

    if any(k in t for k in ["hola", "buenas", "hey", "buenos dias", "buenos días", "buenas noches"]):
        return random.choice(GREETING_REPLIES)

    return random.choice(DEFAULT_REPLIES)

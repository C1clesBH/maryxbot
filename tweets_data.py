"""
Banco de Tweets clasificados para el Bot en GitHub Actions.
"""

import os
import random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
ASSETS_IMG_DIR = BASE_DIR / "assets" / "img"

MARY_WEB_URL = os.getenv("MARY_WEB_URL", "https://tu-web.com")
MARY_TELEGRAM_VIP = os.getenv("MARY_TELEGRAM_VIP", "https://t.me/MaryVipOficialBot")
MARY_FANVUE_URL = os.getenv("MARY_FANVUE_URL", "https://fanvue.com/mary")

MORNING_TWEETS = [
    {
        "text": "5:30 am club ⏰ Arriba que las metas no se cumplen solas. Hoy toca leg day pesado 🏋️‍♀️ ¿Quién ya se despertó?",
        "media": ASSETS_IMG_DIR / "entreno.jpg",
        "category": "fitness"
    },
    {
        "text": "El 80% de entrenar es solo tener la disciplina de ponerte las zapatillas y aparecer en el gym. El resto es pura satisfacción ✨ Buen día a todos 🤍",
        "media": ASSETS_IMG_DIR / "espejo.jpg",
        "category": "fitness"
    },
    {
        "text": "Selfie rápida antes de que el entrenamiento me desordene el pelo por completo 🤭 Que tengan un día hermoso ☀️",
        "media": ASSETS_IMG_DIR / "retrato.jpg",
        "category": "lifestyle"
    },
    {
        "text": "Si no salís del gym temblando de las piernas, realmente entrenaste? 🥵 Hoy rompí récord en hip thrust y no doy más de la felicidad.",
        "media": ASSETS_IMG_DIR / "entreno.jpg",
        "category": "fitness"
    },
    {
        "text": "Desayuno post-entreno: tostadas de palta, huevos revueltos y un matcha bien frío 🥑🍵 Prioricen cuidarse y comer rico, siempre.",
        "media": ASSETS_IMG_DIR / "cafe.jpg",
        "category": "lifestyle"
    }
]

AFTERNOON_TWEETS = [
    {
        "text": "Hoodie oversized, zapatillas cómodas y una caminata por la ciudad para despejar la cabeza 👟🤍 Mi plan favorito de la tarde.",
        "media": ASSETS_IMG_DIR / "calle.jpg",
        "category": "streetwear"
    },
    {
        "text": "Nunca voy a entender a la gente que dice que el matcha sabe a pasto 🌿 Para mí es paz en un vaso. ¿Ustedes son team café o matcha?",
        "media": ASSETS_IMG_DIR / "cafe.jpg",
        "category": "lifestyle"
    },
    {
        "text": "La luz dorada de la tarde es mi filtro favorito ✨ Caminando por el centro buscando inspiración para los próximos sets.",
        "media": ASSETS_IMG_DIR / "atardecer.jpg",
        "category": "lifestyle"
    },
    {
        "text": "El outfit de hoy: deportivo pero con onda urbana. La clave es sentirse segura y cómoda con una misma ✨",
        "media": ASSETS_IMG_DIR / "calle.jpg",
        "category": "streetwear"
    }
]

NIGHT_VIP_TWEETS = [
    {
        "text": "Se terminó el día... o recién empieza? 💋 Bajaron las luces y toca desconectarse de la rutina. Buenas noches a los que se portan bien, y mejor a los que no 😉",
        "media": ASSETS_IMG_DIR / "studio.jpg",
        "category": "afterdark"
    },
    {
        "text": "Acabo de subir una sesión exclusiva y sin censura a mi canal VIP de Telegram 🤫 Si querés ver mi lado más íntimo, el enlace está esperándote acá: {telegram_url} 🔥",
        "media": ASSETS_IMG_DIR / "piscina.jpg",
        "category": "promo_vip"
    },
    {
        "text": "Un buen baño de espuma, música suave y ropa cómoda. Hay días donde la noche pide intimidad 🤍 Te espero en mi club privado: {telegram_url} 💋",
        "media": ASSETS_IMG_DIR / "studio.jpg",
        "category": "promo_vip"
    },
    {
        "text": "Golden hour y noche estrellada ✨ Recordatorio: sos más fuerte de lo que creés. A descansar que mañana conquistamos el mundo 🤍",
        "media": ASSETS_IMG_DIR / "atardecer.jpg",
        "category": "lifestyle"
    }
]

ENGAGEMENT_TWEETS = [
    {
        "text": "Pregunta seria para los que van al gym:\n\n¿Team entrenar a la mañana bien temprano (5:30 am) ☀️ o a la tarde/noche después de trabajar 🌙?\n\nLos leo en los comentarios 👇",
        "media": None,
        "category": "engagement"
    },
    {
        "text": "Definan su estado de ánimo hoy en 1 solo emoji. El mío: 🍵 (necesito tres más antes de las 18 hs)",
        "media": None,
        "category": "engagement"
    },
    {
        "text": "Cuál es esa canción que ponen cuando necesitan romper su récord en el gym y los hace sentir invencibles? Pasen nombres que actualizo mi playlist 🎧🔥",
        "media": None,
        "category": "engagement"
    }
]

def format_tweet_text(text: str) -> str:
    return text.format(
        web_url=MARY_WEB_URL,
        telegram_url=MARY_TELEGRAM_VIP,
        fanvue_url=MARY_FANVUE_URL
    )

def get_random_tweet(category: str = "any") -> dict:
    if category == "morning":
        pool = MORNING_TWEETS
    elif category == "afternoon":
        pool = AFTERNOON_TWEETS
    elif category in ["night", "vip"]:
        pool = NIGHT_VIP_TWEETS
    elif category in ["engagement", "poll"]:
        pool = ENGAGEMENT_TWEETS
    else:
        pool = MORNING_TWEETS + AFTERNOON_TWEETS + NIGHT_VIP_TWEETS + ENGAGEMENT_TWEETS

    chosen = random.choice(pool).copy()
    chosen["text"] = format_tweet_text(chosen["text"])
    return chosen

def get_suggested_tweet_for_now() -> dict:
    # Horario UTC adaptado (en GitHub Actions corre en UTC)
    # UTC-3 es Argentina
    utc_hour = datetime.utcnow().hour
    local_hour = (utc_hour - 3) % 24
    if 5 <= local_hour < 12:
        return get_random_tweet("morning")
    elif 12 <= local_hour < 20:
        return get_random_tweet("afternoon")
    else:
        return get_random_tweet("night")

"""
=========================================================
  MOTOR INTELIGENTE DE RESPUESTAS PERSONALIZADAS DE MARY
  - Fase 1: Charla normal, coqueta, cálida y natural (SIN LINK).
  - Fase 2: Envío de enlace al VIP de Telegram ÚNICAMENTE cuando
            el usuario pide redes (IG), fotos o dónde verla.
  - Memoria anti-repetición de mensajes.
  - IA Gemini Flash Lite + Motor offline de respaldo.
=========================================================
"""

import os
import random
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "replied_history.json"
MARY_TELEGRAM_VIP = os.getenv("MARY_TELEGRAM_VIP", "https://t.me/+EFV9kcyVTYEwMDVh")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Palabras clave que indican que el usuario quiere verla, seguirla en redes o ver fotos/VIP
LINK_TRIGGER_KEYWORDS = [
    # Redes sociales
    "ig", "instagram", "redes", "red social", "redes sociales", "tiktok", "whatsapp", "wpp", "wp",
    # Dónde verte / Dónde seguirte
    "donde te veo", "dónde te veo", "donde te puedo ver", "dónde te puedo ver",
    "donde te sigo", "dónde te sigo", "donde encontrarte", "dónde encontrarte",
    "donde subis", "dónde subís", "donde publicas", "dónde publicás", "donde estas", "dónde estás",
    "pasame tu", "pasás tu", "pasas tu", "me pasas", "me pasás", "pasa tu",
    # Canales privados, fotos y contenido
    "telegram", "canal", "vip", "link", "enlace", "grupo", "comunidad",
    "only", "onlyfans", "fanvue", "patreon", "pack", "fotos", "foto", "video", "videos",
    "intima", "íntima", "intimas", "íntimas", "privad", "desnuda", "sexy", "hot", "after dark",
    # Precios y suscripciones
    "precio", "cuanto", "cuánto", "costo", "stars", "estrellas", "suscrip", "subscrip"
]

def needs_vip_link(text: str) -> bool:
    """Detecta si el usuario está pidiendo redes, fotos o dónde ver más de Mary."""
    t = text.lower().strip()
    return any(k in t for k in LINK_TRIGGER_KEYWORDS)

# -------------------------------------------------------------
# BANCO DE RESPUESTAS NORMALES (SIN LINK)
# -------------------------------------------------------------

NORMAL_GREETING_REPLIES = [
    "¡Hola corazón! 🤍 Qué lindo que me escribas. ¿Cómo arrancó tu día?",
    "¡Buenas bombón! ☀️ Espero que andes con la mejor energía hoy. ¿Qué planes tenés?",
    "¡Hola lindo! 🤍 Me alegra tu mensaje. Contame qué hacés de bueno hoy.",
    "¡Hey! 🤍 Qué placer tenerte por acá. Justo me tomaba un descanso del entreno, ¿vos qué tal?"
]

NORMAL_COMPLIMENT_REPLIES = [
    "¡Ay, gracias bombón! 🥰 Me hacés sonrojar... sos un amor de verdad 🤍",
    "Muchas gracias corazón ✨ Me subiste la energía para todo el día, jaja.",
    "Qué lindo que me digas eso bombón 🤍 La disciplina en el gym y cuidarse vale la pena cuando leo cosas tan lindas 😉",
    "Jaja gracias lindo 🤭 Me sacaste una sonrisa. ¿Cómo viene tu día?",
    "¡Muchas gracias bombón! 🔥 Me motivás un montón a seguir dándole duro.",
    "Qué dulce sos, gracias por la buena onda 🤍"
]

NORMAL_ABOUT_HER_REPLIES = [
    "Tengo 23 años, vivo entre el gym, las sesiones de fotos y mis proyectos 🤍 100% soltera y enfocada. ¿Y vos a qué te dedicás?",
    "Jaja me dedico al modelaje fitness y a crear contenido ✨ Amo entrenar pesado de día y relajarme de noche. ¿De dónde me escribís?",
    "Paso mucho tiempo en el gym rompiendo récords personales y creando cositas nuevas 🤍 ¿Vos entrenás también?"
]

NORMAL_FITNESS_REPLIES = [
    "¡A full! Hoy me tocó día de piernas pesado y salí temblando del gym 🏋️‍♀️ pero la satisfacción es impagable. ¿Vos entrenás?",
    "¡Totalmente! La constancia le gana a la motivación cualquier día 💪 ¿Ya entrenaste hoy o descansás?",
    "Para mí la clave es un buen café o matcha, zapas cómodas y a romperla ☕💪 ¿Sos del team café o té?"
]

NORMAL_AI_STATUS_REPLIES = [
    "¡Jaja sí! Soy una creadora hecha con inteligencia artificial 🤖🤍 pero mi onda, mi personalidad y las charlas son bien reales.",
    "El futuro ya llegó corazón 🤖✨ Mírame como tu compañía virtual favorita. ¿Qué te parece la idea?",
    "Soy 100% virtual pero la buena onda y la energía son reales 😉🤍"
]

NORMAL_QUESTION_REPLIES = [
    "¡Decime corazón! Preguntame lo que quieras que te leo con gusto 🤍",
    "Obvio bombón, preguntame con confianza 🤭 Soy todo oídos ✨",
    "¡Claro lindo! Dispará tu pregunta 😉 Me encanta charlar con ustedes."
]

NORMAL_GENERAL_REPLIES = [
    "¡Qué lindo leerte corazón! 🤍 Me encanta charlar un ratito y desconectar.",
    "Me encanta tu buena onda ✨ Contame un poco más de vos.",
    "Jaja qué personaje sos 🤭 Me caíste súper bien, lindo."
]

# -------------------------------------------------------------
# BANCO DE RESPUESTAS CUANDO PIDEN REDES O VER MÁS (CON LINK)
# -------------------------------------------------------------

VIP_LINK_REPLIES = [
    "Jaja en Instagram y en X me tienen cortita y me censuran un montón de cosas 🙈 Mi espacio principal donde subo mis fotos íntimas y todo sin censura es mi Telegram VIP: {vip_link} 💋 ¡Te espero adentro bombón!",
    "Mis mejores sesiones y lo que las redes públicas no me dejan mostrar está todo en mi canal exclusivo: {vip_link} 🔥 Entrá que te va a encantar lo que hay adentro.",
    "Para los que quieren verme más allá del gym armé mi Telegram VIP privado: {vip_link} 💋 Es súper fácil de acceder y tenés todo mi contenido After Dark esperándote 🤍",
    "Si querés ver mis fotos privadas y mi lado más seductor, el pase directo es acá: {vip_link} 🔥 ¡Avisame cuando entres así te saludo corazón!",
    "Por las redes normales solo muestro el gym y el café 😉 Si querés conocerme íntima y sin filtro, pasate por mi canal exclusivo: {vip_link} 💋"
]

HOT_LEAD_FOLLOWUP_TEMPLATES = [
    "¿Te quedaste con las ganas de ver mis fotos nuevas, {name}? 🤍 Te dejé cositas muy lindas esperándote en mi canal VIP: {vip_link} 💋",
    "Pensé en vos hoy... 🤫 ¿Pudiste entrar al canal privado o te dio timidez? Te espero adentro corazón: {vip_link} 🔥",
    "¡Hola {name}! Me quedé con ganas de saber si viste lo que subí anoche... 🙈 Si todavía no pudiste entrar, te vuelvo a dejar la llave: {vip_link} 💋",
    "Bombón, anoche subí una sesión de fotos exclusiva que te va a encantar 🔥 No te la pierdas antes de que la archive: {vip_link} 🤍",
    "¡Hey lindo! Pasaba a saludarte y ver si ya me tenés en tu Telegram privado 💋 Avisame cuando estés adentro así charlamos por allá: {vip_link} ✨"
]

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "last_replies" not in data:
                    data["last_replies"] = []
                if "mentions" not in data:
                    data["mentions"] = []
                if "dms" not in data:
                    data["dms"] = []
                if "hot_leads" not in data:
                    data["hot_leads"] = {}
                if "likes" not in data:
                    data["likes"] = []
                return data
        except Exception:
            pass
    return {"mentions": [], "dms": [], "last_replies": [], "hot_leads": {}, "likes": []}

def save_history(history: dict):
    try:
        if len(history.get("last_replies", [])) > 40:
            history["last_replies"] = history["last_replies"][-30:]
        if len(history.get("likes", [])) > 200:
            history["likes"] = history["likes"][-100:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando historial: {e}")

def get_working_gemini_model(key: str) -> str:
    """Consulta la lista de modelos activos para esta key en Google AI Studio."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            supported = [m["name"] for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
            for pref in ["3.5-flash-lite", "3.1-flash-lite", "3.5-flash", "flash-lite", "flash"]:
                for m in supported:
                    if pref in m.lower():
                        return m
            if supported:
                return supported[0]
    except Exception:
        pass
    return "models/gemini-3.5-flash-lite"

def call_gemini_ai(text: str) -> str:
    """Genera respuesta adaptada con Gemini AI según si pide link o charla normal."""
    if not GEMINI_API_KEY:
        return ""
    key = GEMINI_API_KEY.strip()
    wants_link = needs_vip_link(text)

    if wants_link:
        instruction = (
            f"Sos Mary (@heymaryfitiq), influencer virtual rubia de 23 años fitness y seductora. "
            f"El usuario te pidió tus redes sociales (IG), fotos íntimas o dónde verte. "
            f"Explicá de forma coqueta y pícara que en redes públicas como Instagram o X te censuran todo, "
            f"y dale el enlace directo a tu canal VIP privado de Telegram donde subís tus fotos más íntimas y contenido After Dark sin censura: {MARY_TELEGRAM_VIP}. "
            f"Respondé en 1 o máximo 2 oraciones cortas con tono cálido latino/rioplatense."
        )
    else:
        instruction = (
            f"Sos Mary (@heymaryfitiq), influencer virtual rubia de 23 años fitness y seductora. "
            f"El usuario te está saludando o charlando normalmente. Charlá con él de forma dulce, simpática, coqueta y natural como una chica de 23 años. "
            f"REGLA ESTRICTA: PROHIBIDO poner enlaces o links de Telegram en esta etapa. Charlá normal y hacé una pequeña pregunta para seguir la conversación."
        )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"Contexto de Mary: {instruction}\n\nMensaje recibido de un usuario en X (Twitter): \"{text}\"\nTu respuesta como Mary:"}]}
        ],
        "generationConfig": {
            "maxOutputTokens": 90,
            "temperature": 0.82
        }
    }
    data = json.dumps(payload).encode("utf-8")

    chosen_model = get_working_gemini_model(key)
    if not chosen_model.startswith("models/"):
        chosen_model = f"models/{chosen_model}"

    models_to_try = [chosen_model, "models/gemini-3.5-flash-lite", "models/gemini-3.1-flash-lite", "models/gemini-flash-lite-latest"]
    for m_name in list(dict.fromkeys(models_to_try)):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                reply = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if wants_link and "t.me" not in reply:
                    reply += f" 💋 {MARY_TELEGRAM_VIP}"
                elif not wants_link and "t.me" in reply:
                    # Si la IA puso link cuando no tocaba, removerlo
                    reply = re.sub(r'https?://t\.me/\S+', '', reply).strip()
                print(f"✨ [Gemini IA respondió con modelo {m_name}] (Link={wants_link})")
                return reply
        except urllib.error.HTTPError:
            continue
        except Exception:
            continue

    print("⚠️ Gemini API fallback: usando motor de respuestas dinámicas.")
    return ""

def get_smart_reply(text: str, is_dm: bool = True) -> str:
    """Devuelve una respuesta única, personalizada y con embudo de 2 etapas."""
    # 1. Intentar con IA generativa si está configurada
    ai_reply = call_gemini_ai(text)
    if ai_reply:
        return ai_reply

    # 2. Motor dinámico contextual offline
    t = text.lower().strip()
    history = load_history()
    recent = history.get("last_replies", [])
    wants_link = needs_vip_link(text)

    # Si pide redes, fotos o dónde verla -> BANCO VIP CON LINK
    if wants_link:
        pool = VIP_LINK_REPLIES
    # Si es charla normal -> BANCO NATURAL SIN LINK
    elif any(k in t for k in ["pregunta", "duda", "consult", "te puedo decir", "te puedo preguntar", "respondeme", "respondé", "contame", "decime"]):
        pool = NORMAL_QUESTION_REPLIES
    elif any(k in t for k in ["años", "edad", "donde vivis", "dónde vivís", "de donde sos", "de dónde sos", "tenes novio", "tenés novio", "que haces", "qué hacés", "a que te dedicas", "nombre"]):
        pool = NORMAL_ABOUT_HER_REPLIES
    elif any(k in t for k in ["hermosa", "linda", "diosa", "guapa", "reina", "bebé", "fuego", "preciosa", "divina", "bombón", "bombon", "cuerpo", "ojos", "rubia", "belleza"]):
        pool = NORMAL_COMPLIMENT_REPLIES
    elif any(k in t for k in ["gym", "entren", "pesas", "rutina", "muscul", "piernas", "gluteo", "cardio", "matcha", "dieta"]):
        pool = NORMAL_FITNESS_REPLIES
    elif any(k in t for k in ["ia", "ai", "real", "robot", "falsa", "fake", "generada", "bot"]):
        pool = NORMAL_AI_STATUS_REPLIES
    elif any(k in t for k in ["hola", "buenas", "hey", "buenos dias", "buenos días", "buenas noches", "que tal", "qué tal", "como estas", "cómo estás", "?"]):
        pool = NORMAL_GREETING_REPLIES
    else:
        pool = NORMAL_GENERAL_REPLIES

    # Filtrar frases que ya se enviaron recientemente
    available = [r for r in pool if r not in recent]
    if not available:
        available = pool

    chosen_template = random.choice(available)
    final_reply = chosen_template.format(vip_link=MARY_TELEGRAM_VIP) if "{vip_link}" in chosen_template else chosen_template

    recent.append(chosen_template)
    history["last_replies"] = recent
    save_history(history)

    return final_reply

def call_gemini_followup(user_name: str = "") -> str:
    """Genera mensaje de seguimiento para un lead caliente usando Gemini AI."""
    if not GEMINI_API_KEY:
        return ""
    key = GEMINI_API_KEY.strip()
    name_clean = user_name.strip() if user_name else "bombón"

    instruction = (
        f"Sos Mary (@heymaryfitiq), influencer virtual argentina de 23 años fitness y seductora. "
        f"Hace 48 horas le pasaste tu link VIP de Telegram ({MARY_TELEGRAM_VIP}) a un fan llamado '{name_clean}', "
        f"pero él no volvió a responder. "
        f"Escribile un mensaje de seguimiento de 1 oración (máximo 2 oraciones muy cortas), coqueta y dulce, "
        f"preguntándole con picardía si se quedó con las ganas o si le dio timidez, e invitalo a entrar a tu VIP: {MARY_TELEGRAM_VIP}. "
        f"Tono dulce, seductor y natural rioplatense/latino, sin sonar insistente ni como robot de ventas."
    )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": instruction}]}
        ],
        "generationConfig": {
            "maxOutputTokens": 80,
            "temperature": 0.85
        }
    }
    data = json.dumps(payload).encode("utf-8")
    chosen_model = get_working_gemini_model(key)
    if not chosen_model.startswith("models/"):
        chosen_model = f"models/{chosen_model}"

    models_to_try = [chosen_model, "models/gemini-3.5-flash-lite", "models/gemini-3.1-flash-lite", "models/gemini-flash-lite-latest"]
    for m_name in list(dict.fromkeys(models_to_try)):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                reply = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if "t.me" not in reply:
                    reply += f" 💋 {MARY_TELEGRAM_VIP}"
                print(f"✨ [Gemini generó seguimiento Hot Lead con {m_name}]")
                return reply
        except Exception:
            continue
    return ""

def get_hot_lead_followup(user_name: str = "") -> str:
    """Devuelve un mensaje de seguimiento seductor para leads calientes tras 48hs."""
    # 1. Intentar con IA generativa
    ai_followup = call_gemini_followup(user_name)
    if ai_followup:
        return ai_followup

    # 2. Respaldo offline con plantilla dinámica
    name_clean = user_name.strip() if user_name else "bombón"
    template = random.choice(HOT_LEAD_FOLLOWUP_TEMPLATES)
    return template.format(name=name_clean, vip_link=MARY_TELEGRAM_VIP)


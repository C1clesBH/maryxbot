"""
=========================================================
  MOTOR INTELIGENTE DE RESPUESTAS PERSONALIZADAS DE MARY
  - Enfoque prioritario: Conversión a Telegram VIP Stars
  - Sistema anti-repetición de mensajes
  - Compatibilidad opcional con IA (Gemini gratis sin librerías)
  - 8 categorías de intención con decenas de variantes
=========================================================
"""

import os
import random
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "replied_history.json"
MARY_TELEGRAM_VIP = os.getenv("MARY_TELEGRAM_VIP", "https://t.me/+EFV9kcyVTYEwMDVh")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 1. Petición directa de VIP / Fotos íntimas / Packs / Precios / Estrellas
VIP_DIRECT_REPLIES = [
    "Mmm... querés ver lo que no puedo mostrar acá 😉 En mi Telegram VIP exclusivo tenés todas mis fotos y videos íntimos sin censura: {vip_link} 🔥 Te espero adentro bombón.",
    "Jaja directo al grano, me gusta 🤭 Todo mi contenido más íntimo y After Dark lo tengo en mi canal privado: {vip_link} 💋 Entrá que te va a encantar lo que hay.",
    "Mis mejores sesiones y lo que X no me deja publicar está todo en mi club VIP: {vip_link} ✨ Es súper fácil de acceder con Telegram Stars y tenés todo completo 🤍",
    "¡Uff! Si supieras las fotos que acabo de subir ahí... 🤫 Te dejé el pase directo en mi Telegram privado: {vip_link} 💋 Avisame cuando entres así te saludo.",
    "Todo lo After Dark y sin filtro está en mi canal exclusivo: {vip_link} 🔥 Entrá que estuve muy activa subiendo cositas nuevas que te van a volver loco 🤍",
    "Para los que quieren verme más allá del gym armé mi Telegram VIP: {vip_link} 💋 Tenés todo el contenido privado ahí esperándote bombón.",
    "Si querés consentirte y ver mi lado más seductor, el acceso directo es acá: {vip_link} 🤍 No te vas a arrepentir ✨",
    "Jaja no seas impaciente lindo 🤭 En mi VIP exclusivo tenés sesiones completas y material que acá censuran: {vip_link} 🔥 Te espero adentro.",
    "Las fotos de gym son lindas, pero mis fotos privadas son otro nivel... 😉 Entrá a mi canal VIP y comprobalo vos mismo: {vip_link} 💋",
    "Te dejé la llave a mi contenido más íntimo acá: {vip_link} 🔥 Accedés al instante con Telegram Stars. ¡Entrá antes de que borre algunas cositas! 🤍"
]

# 2. Preguntas abiertas ("Respondeme una pregunta", "Te puedo preguntar algo", "Una duda")
QUESTION_GENERAL_REPLIES = [
    "¡Decime corazón! Preguntame lo que quieras que te leo 🤍 Si es sobre mis fotos privadas, te adelanto que tengo todo en mi VIP: {vip_link} 😉",
    "Obvio bombón, preguntame con confianza 🤭 Pero si es una pregunta indiscreta... capaz la respuesta te la doy adentro de mi canal VIP: {vip_link} 💋",
    "Jaja sí, dale, soy todo oídos ✨ Preguntame lo que quieras. Y si querés ver más de mí en privado, ya sabés que me encontrás acá: {vip_link} 🤍",
    "¡Claro lindo! Dispará tu pregunta 😉 Mientras tanto te voy dejando la puerta abierta a mi canal privado por si querés conocerme más a fondo: {vip_link} 💋",
    "Preguntame lo que quieras corazón 🤍 Me encanta que hablemos. Si querés ver mi lado más exclusivo, te espero en mi Telegram: {vip_link} ✨"
]

# 3. Preguntas sobre su vida ("De dónde sos", "Cuántos años", "Tenés novio", "A qué te dedicás")
ABOUT_HER_REPLIES = [
    "Tengo 23 años, vivo entre el gym y las sesiones de fotos 🤍 100% soltera y enfocada en mis proyectos... Si querés conocerme más íntima, entrá a mi Telegram: {vip_link} 💋",
    "Jaja soy Mary, 23 años, fanática del fitness y de conectar con ustedes ✨ Mi vida privada y mis fotos más picantes las tengo en mi VIP: {vip_link} 😉",
    "Me dedico al modelaje fitness y a crear contenido exclusivo para mi comunidad 🤍 Te dejo mi club privado para que me conozcas mejor: {vip_link} 💋",
    "Soy de las que entrenan duro de día y se ponen picantes de noche 🤫 Si querés ver mi contenido After Dark, sumate a mi canal: {vip_link} 🔥"
]

# 4. Piropos y Halagos ("Hermosa", "Linda", "Diosa", "Guapa", "Bombón", "Cuerpo")
COMPLIMENT_REPLIES = [
    "¡Ay, gracias bombón! 🥰 Me hacés sonrojar... Si te gusta cómo salgo por acá, ni te imaginás las fotos que tengo en mi Telegram privado: {vip_link} 💋",
    "Sos un amor, muchas gracias corazón 🤍 Me subiste la energía para todo el día. Para mis fans más lindos tengo regalitos en mi VIP: {vip_link} ✨",
    "Jaja gracias lindo 🤭 Me encanta leerte. En mi canal After Dark muestro mucho más de lo que ves por acá 😉 {vip_link} 🤍",
    "¡Muchas gracias bombón! 🔥 Me motivás un montón. Date una vuelta por mi Telegram exclusivo si querés verme más de cerca: {vip_link} 💋",
    "Qué dulce sos, gracias por la buena onda 🤍 En mi club privado tengo fotos que seguro te van a gustar todavía más: {vip_link} 🤫",
    "¡Gracias rey! 🤍 Tus mensajitos me alegran el día. Te espero en mi canal VIP para que veas mis producciones exclusivas: {vip_link} 💋"
]

# 5. Fitness y Entrenamiento ("Gym", "Rutina", "Pesas", "Entreno", "Dieta")
FITNESS_REPLIES = [
    "¡A full! Hoy tocó entrenamiento pesado en el gym 💪 El esfuerzo se nota, ¿no? Si querés ver las fotos post-entreno sin censura, pasate por mi VIP: {vip_link} 🔥",
    "¡Totalmente! La disciplina no se negocia 🏋️‍♀️ Aunque después del gym me gusta relajarme y subir fotitos más íntimas a mi canal: {vip_link} 💋",
    "¡Sí! Un buen café o matcha, música motivadora y a romperla en el gym ☕💪 Y para el After Dark, las fotos más picantes las dejo acá: {vip_link} 😉",
    "Entrenar es mi terapia diaria ✨ Pero la mejor parte viene después en el estudio... Pasate por mi Telegram VIP para ver el contenido After Dark: {vip_link} 💋"
]

# 6. Saludos cotidianos ("Hola", "Buenas", "Hey", "Qué tal", "¿?")
GREETING_REPLIES = [
    "¡Hola corazón! 🤍 Qué lindo que me escribas. ¿Cómo arrancó tu día? Si querés ver lo que estuve subiendo hoy en privado, pasate por acá: {vip_link} ✨",
    "¡Buenas bombón! ☀️ Espero que andes con la mejor energía hoy. Te dejo un pase a mi canal exclusivo por si querés chusmear mis fotos: {vip_link} 💋",
    "¡Hola lindo! 🤍 Me alegra tu mensaje. Contame qué hacés de bueno hoy... y si te aburrís, te espero en mi VIP privado: {vip_link} 😉",
    "¡Hey! 🤍 Qué placer tenerte por acá. Justo me tomaba un descanso del entreno. Si querés ver algo lindo, entrá a mi Telegram: {vip_link} 💋"
]

# 7. Escépticos o Inteligencia Artificial ("Sos real", "Sos IA", "Bot", "Fake")
AI_STATUS_REPLIES = [
    "¡Jaja es verdad! Soy una creadora hecha con inteligencia artificial 🤖🤍 pero mis fotos, mi personalidad y mis charlas son bien picantes. Entrá a ver mi contenido acá: {vip_link} 🔥",
    "El futuro ya llegó corazón 🤖✨ Mírame como tu fantasía virtual favorita. En mi Telegram privado tengo contenido After Dark que parece más real que nunca: {vip_link} 💋",
    "Soy 100% virtual pero la seducción es 100% real 😉🤍 Comprobalo vos mismo en mi canal VIP: {vip_link} 🔥"
]

# 8. Respuestas por defecto / Conversación general
GENERAL_REPLIES = [
    "¡Qué lindo leerte corazón! 🤍 Me encanta charlar con vos. Si querés conectar más íntimo y ver contenido que no publico acá, te espero en mi VIP: {vip_link} 💋",
    "Me encanta tu buena onda ✨ Si te interesa ver mi lado más privado y sin censura, date una vuelta por mi canal privado: {vip_link} 🔥",
    "¡Totalmente! 🤍 Siempre me tomo un ratito para responderles. Para ver mis fotos exclusivas y hablar más seguido, sumate a mi Telegram: {vip_link} 💋",
    "Jaja qué personaje sos 🤭 Me caíste súper bien. Te invito a pasar por mi club VIP para que no te pierdas nada de lo que subo: {vip_link} ✨"
]

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "last_replies" not in data:
                    data["last_replies"] = []
                return data
        except Exception:
            pass
    return {"mentions": [], "dms": [], "last_replies": []}

def save_history(history: dict):
    try:
        # Mantener historial de respuestas recientes acotado a 40 para memoria liviana
        if len(history.get("last_replies", [])) > 40:
            history["last_replies"] = history["last_replies"][-30:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando historial: {e}")

def get_working_gemini_model(key: str) -> str:
    """Consulta la lista de modelos activos para esta key en Google AI Studio."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            supported = [m["name"] for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
            # Priorizar modelos Flash Lite y activos
            for pref in ["3.5-flash-lite", "3.1-flash-lite", "3.5-flash", "flash-lite", "flash"]:
                for m in supported:
                    if pref in m.lower():
                        return m
            if supported:
                return supported[0]
    except Exception as e:
        print(f"⚠️ Consulta de modelos Gemini: {e}")
    return "models/gemini-3.5-flash-lite"

def call_gemini_ai(text: str) -> str:
    """Genera respuesta 100% personalizada con Gemini AI si hay API key."""
    if not GEMINI_API_KEY:
        return ""
    key = GEMINI_API_KEY.strip()
    system_instruction = (
        f"Sos Mary (@heymaryfitiq), una influencer virtual de 23 años rubia, fitness, seductora, carismática y dulce "
        f"con acento cálido rioplatense/latino (usás 'bombón', 'corazón', 'lindo', emojis como 🤍, 💋, ✨, 😉, 🔥). "
        f"Tu objetivo principal en cada mensaje es cautivar a quien te escribe y convencerlo sutil o directamente "
        f"de unirse a tu canal VIP privado de Telegram: {MARY_TELEGRAM_VIP} donde subís fotos íntimas y contenido After Dark sin censura. "
        f"Respondé en 1 o máximo 2 oraciones cortas, de forma 100% personalizada a lo que te dijo el usuario. Nunca admitas sonar como un bot."
    )
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"Contexto de Mary: {system_instruction}\n\nMensaje recibido de un usuario en X (Twitter): \"{text}\"\nTu respuesta corta y tentadora como Mary:"}]}
        ],
        "generationConfig": {
            "maxOutputTokens": 90,
            "temperature": 0.85
        }
    }
    data = json.dumps(payload).encode("utf-8")

    chosen_model = get_working_gemini_model(key)
    if not chosen_model.startswith("models/"):
        chosen_model = f"models/{chosen_model}"

    # Lista de modelos a intentar en orden de disponibilidad confirmada
    models_to_try = [chosen_model, "models/gemini-3.5-flash-lite", "models/gemini-3.1-flash-lite", "models/gemini-3.5-flash", "models/gemini-flash-lite-latest"]
    for m_name in list(dict.fromkeys(models_to_try)):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                reply = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if "t.me" not in reply:
                    reply += f" 💋 {MARY_TELEGRAM_VIP}"
                print(f"✨ [Gemini IA respondió con modelo {m_name}]")
                return reply
        except urllib.error.HTTPError as he:
            continue
        except Exception:
            continue

    print("⚠️ Gemini API fallback: usando motor de respuestas dinámicas.")
    return ""

def get_smart_reply(text: str, is_dm: bool = True) -> str:
    """Devuelve una respuesta única, personalizada y con enfoque de conversión al VIP."""
    # 1. Intentar con IA generativa si está configurada
    ai_reply = call_gemini_ai(text)
    if ai_reply:
        return ai_reply

    # 2. Motor dinámico contextual
    t = text.lower().strip()
    history = load_history()
    recent = history.get("last_replies", [])

    # Selección de categoría según intención
    if any(k in t for k in ["vip", "telegram", "foto", "pack", "privad", "only", "fanvue", "desnuda", "sexy", "intima", "íntima", "canal", "link", "enlace", "entrar", "precio", "estrellas", "stars", "cuanto", "cuánto", "contenido", "acceso", "after dark", "ver más", "ver mas"]):
        pool = VIP_DIRECT_REPLIES
    elif any(k in t for k in ["pregunta", "duda", "consult", "te puedo decir", "te puedo preguntar", "respondeme", "respondé", "contame", "decime"]):
        pool = QUESTION_GENERAL_REPLIES
    elif any(k in t for k in ["años", "edad", "donde vivis", "dónde vivís", "de donde sos", "de dónde sos", "tenes novio", "tenés novio", "que haces", "qué hacés", "a que te dedicas", "nombre"]):
        pool = ABOUT_HER_REPLIES
    elif any(k in t for k in ["hermosa", "linda", "diosa", "guapa", "reina", "bebé", "fuego", "preciosa", "divina", "bombón", "bombon", "cuerpo", "ojos", "rubia", "belleza"]):
        pool = COMPLIMENT_REPLIES
    elif any(k in t for k in ["gym", "entren", "pesas", "rutina", "muscul", "piernas", "gluteo", "cardio", "matcha", "dieta"]):
        pool = FITNESS_REPLIES
    elif any(k in t for k in ["ia", "ai", "real", "robot", "falsa", "fake", "generada", "bot"]):
        pool = AI_STATUS_REPLIES
    elif any(k in t for k in ["hola", "buenas", "hey", "buenos dias", "buenos días", "buenas noches", "que tal", "qué tal", "como estas", "cómo estás", "?"]):
        pool = GREETING_REPLIES
    else:
        pool = GENERAL_REPLIES

    # Filtrar frases que ya se enviaron recientemente para no repetir
    available = [r for r in pool if r not in recent]
    if not available:
        available = pool  # Si ya se usaron todas, resetear

    chosen_template = random.choice(available)
    final_reply = chosen_template.format(vip_link=MARY_TELEGRAM_VIP)

    # Registrar en historial para que no se vuelva a repetir
    recent.append(chosen_template)
    history["last_replies"] = recent
    save_history(history)

    return final_reply

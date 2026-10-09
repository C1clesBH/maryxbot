"""
=========================================================
  MOTOR DE VOZ Y NOTAS DE AUDIO DE MARY (ELEVENLABS)
  - Soporte de generación TTS en tiempo real con ElevenLabs API.
  - Modelo eleven_multilingual_v2 con modulación seductora/natural.
  - Banco de Audios de Oro offline (0 costo, 0 latencia).
  - Manejo de fallbacks automáticos para garantizar 100% estabilidad.
=========================================================
"""

import os
import json
import random
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Variables de configuración (pueden venir de GitHub Secrets o entorno local)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
# Default voice: Rachel o voz seleccionada por el usuario
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()

# Configuración acústica para lograr tono coqueto, cálido y natural (rioplatense/latino)
VOICE_SETTINGS = {
    "stability": 0.42,         # Menor estabilidad = mayor emoción y expresividad
    "similarity_boost": 0.82,  # Fidelidad al timbre
    "style": 0.28,             # Toque pícaro/fresco
    "use_speaker_boost": True
}

# Guiones predeterminados para el Banco de Audios de Oro
GOLDEN_AUDIO_SCRIPTS = {
    "vip_invite": [
        "Jaja, no te puedo pasar mi IG por acá porque me censuran todo... pero venite a mi canal privado de Telegram que ahí te subo todo sin filtro, te va a encantar bombón.",
        "Para los que quieren conocerme más allá del gym armé mi canal VIP exclusivo... pasate que te dejé fotos que te van a volver loco, avisame cuando entres así te saludo corazón."
    ],
    "greeting": [
        "¡Hola corazón! Qué lindo leerte, justo me estaba tomando un descanso después de entrenar a full... ¿vos qué hacés de bueno hoy?",
        "¡Buenas bombón! Qué placer tenerte por acá, me sacaste una sonrisa... contame cómo viene tu día."
    ],
    "after_dark": [
        "Uff... si supieras la sesión de fotos que acabo de subir anoche... te dejé la llave directa en mi canal privado, no te la pierdas antes de que archive algunas cositas.",
        "Por las redes públicas me porto bien... pero en mi club privado tengo fotos que seguro te van a encantar mucho más, animate y vení a verme."
    ],
    "followup_48h": [
        "¿Te quedaste con las ganas de ver mis fotos nuevas, bombón? Dale, animate que te dejé cositas muy lindas esperándote en mi canal VIP.",
        "Hola lindo... me quedé con ganas de saber si viste lo que te dejé preparado. No seas tímido y vení a darme un saludito adentro."
    ]
}

def is_elevenlabs_configured() -> bool:
    """Verifica si la clave de API de ElevenLabs está activa."""
    return bool(ELEVENLABS_API_KEY)

def generate_tts(text: str, filename: str = None) -> Path | None:
    """
    Genera un archivo de audio .mp3 mediante la API oficial de ElevenLabs.
    """
    if not is_elevenlabs_configured():
        return None

    filename = filename or f"mary_tts_{random.randint(1000, 9999)}.mp3"
    target_path = AUDIO_DIR / filename

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            audio_bytes = resp.read()
            target_path.write_bytes(audio_bytes)
            print(f"🎙️ [ElevenLabs TTS] Audio generado con éxito: {target_path.name} ({len(audio_bytes)} bytes)")
            return target_path
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        print(f"⚠️ [ElevenLabs Error HTTP {e.code}]: {err_msg}")
    except Exception as ex:
        print(f"⚠️ [ElevenLabs Exception]: {ex}")

    return None

def get_voice_for_scenario(scenario: str, user_name: str = "", text_custom: str = None) -> Path | None:
    """
    Estrategia Híbrida:
    1. Si ElevenLabs está configurado y se solicita personalización, genera TTS en tiempo real.
    2. Si falla o no hay clave, busca un audio pre-grabado en el Banco de Audios de Oro (assets/audio/).
    """
    # 1. Intentar generación dinámica en tiempo real si hay API Key
    if is_elevenlabs_configured():
        prompt_text = text_custom
        if not prompt_text:
            scripts = GOLDEN_AUDIO_SCRIPTS.get(scenario, GOLDEN_AUDIO_SCRIPTS["vip_invite"])
            base_script = random.choice(scripts)
            if user_name and user_name.strip():
                prompt_text = f"¡Hola {user_name.strip()}! " + base_script
            else:
                prompt_text = base_script

        audio_file = generate_tts(prompt_text, filename=f"dyn_{scenario}_{random.randint(100, 999)}.mp3")
        if audio_file and audio_file.exists():
            return audio_file

    # 2. Respaldo: Banco de Audios de Oro locales
    matching = list(AUDIO_DIR.glob(f"{scenario}*.mp3")) or list(AUDIO_DIR.glob("*.mp3"))
    if matching:
        chosen = random.choice(matching)
        print(f"🎧 [Banco de Audios de Oro] Utilizando audio local: {chosen.name}")
        return chosen

    return None

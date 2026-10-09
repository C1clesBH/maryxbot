"""
=========================================================
  GENERADOR DE BANCO DE AUDIOS DE ORO (ELEVENLABS)
  Crea de forma masiva los audios de alta calidad para Mary
  para que queden guardados permanentemente en assets/audio/
=========================================================
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from voice_engine import generate_tts, GOLDEN_AUDIO_SCRIPTS, is_elevenlabs_configured

def generate_all():
    if not is_elevenlabs_configured():
        print("❌ Error: ELEVENLABS_API_KEY no está configurada en las variables de entorno.")
        print("   Ejecutá: set ELEVENLABS_API_KEY=tu_clave y volvé a intentar.")
        sys.exit(1)

    print("🚀 [ELEVENLABS] Iniciando generación del Banco de Audios de Oro de Mary...")

    for scenario, scripts in GOLDEN_AUDIO_SCRIPTS.items():
        print(f"\n📂 Generando categoría: {scenario.upper()}")
        for i, text in enumerate(scripts, start=1):
            filename = f"{scenario}_{i}.mp3"
            print(f"[*] Generando ({filename}): \"{text[:50]}...\"")
            res = generate_tts(text, filename=filename)
            if res:
                print(f"    ✅ Guardado en assets/audio/{filename}")
            else:
                print(f"    ❌ Falló la generación de {filename}")

    print("\n🎉 ¡BANCO DE AUDIOS DE ORO GENERADO CON ÉXITO! 🎧✨")

if __name__ == "__main__":
    generate_all()

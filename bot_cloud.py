"""
=========================================================
  BOT EN LA NUBE (GITHUB ACTIONS) PARA MARY (@heymaryfitiq)
=========================================================
"""

import os
import sys
import time
import argparse
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

from tweets_data import get_suggested_tweet_for_now, get_random_tweet
from reply_engine import get_smart_reply, load_history, save_history

BASE_DIR = Path(__file__).resolve().parent

def hash_text(text: str) -> str:
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()

def get_browser_context(p):
    auth_token = os.getenv("X_AUTH_TOKEN")
    if not auth_token:
        raise ValueError("❌ Falta la variable de entorno X_AUTH_TOKEN en GitHub Secrets.")

    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    context.add_cookies([
        {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": True},
        {"name": "auth_token", "value": auth_token, "domain": ".twitter.com", "path": "/", "secure": True, "httpOnly": True}
    ])
    return browser, context

def post_tweet(category: str = "now"):
    tweet = get_suggested_tweet_for_now() if category == "now" else get_random_tweet(category)
    print(f"\n🚀 [CLOUD] Preparando tweet ({tweet['category'].upper()}):")
    print(f"{tweet['text']}\n")

    with sync_playwright() as p:
        browser, context = get_browser_context(p)
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        try:
            print("[*] Abriendo redactor en X...")
            page.goto("https://x.com/compose/post", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)

            print("[*] Escribiendo texto...")
            editor = page.locator('[data-testid="tweetTextarea_0"]').first
            editor.wait_for(state="visible", timeout=20000)
            editor.click()
            time.sleep(0.5)
            editor.fill(tweet["text"])
            time.sleep(1)

            media = tweet.get("media")
            if media and Path(media).exists():
                print(f"[*] Adjuntando foto: {Path(media).name}...")
                file_input = page.locator('[data-testid="fileInput"]').first
                file_input.set_input_files(str(media))
                time.sleep(4)

            print("[*] Publicando...")
            post_btn = page.locator('[data-testid="tweetButton"]').first
            post_btn.wait_for(state="visible", timeout=10000)
            post_btn.click()
            time.sleep(5)
            print("🎉 ¡TWEET PUBLICADO EN LA NUBE CON ÉXITO! 🚀✨")

        except Exception as e:
            print(f"❌ Error al publicar en la nube: {e}")
            sys.exit(1)
        finally:
            browser.close()

def unlock_chat_if_needed(page, pin: str = None):
    pin = pin or os.getenv("X_CHAT_PIN", "0416")
    try:
        inputs = page.locator("input").all()
        if len(inputs) == 4 or page.locator("text=Enter Passcode").count() > 0:
            print(f"[*] Pantalla de Passcode detectada. Ingresando clave {pin}...")
            for i in range(min(4, len(inputs))):
                inputs[i].click()
                inputs[i].fill(pin[i])
                time.sleep(0.3)
            print(f"[+] PIN {pin} ingresado con éxito.")
            time.sleep(3)
    except Exception as e:
        print(f"⚠️ Error al verificar/ingresar PIN: {e}")

def reply_all():
    print("\n💬 [CLOUD] Revisando menciones y DMs pendientes...")
    history = load_history()

    with sync_playwright() as p:
        browser, context = get_browser_context(p)
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        try:
            # 1. Menciones
            page.goto("https://x.com/notifications/mentions", timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3.5)

            tweets = page.locator('article[data-testid="tweet"]')
            count = min(tweets.count(), 5)
            for i in range(count):
                tweet = tweets.nth(i)
                txt = tweet.inner_text()
                if "heymaryfit" in txt[:50] and txt.count("@heymaryfitiq") == 1:
                    continue
                h = hash_text(txt[:100])
                if h in history["mentions"]:
                    continue

                reply = get_smart_reply(txt, is_dm=False)
                reply_btn = tweet.locator('[data-testid="reply"]').first
                if reply_btn.count() > 0:
                    reply_btn.click()
                    time.sleep(1)
                    box = page.locator('[data-testid="tweetTextarea_0"]').first
                    box.wait_for(state="visible", timeout=8000)
                    box.fill(reply)
                    time.sleep(1)
                    page.locator('[data-testid="tweetButton"]').first.click()
                    time.sleep(3)
                    print(f"✅ [Mención respondida]: {reply}")
                    history["mentions"].append(h)
                    save_history(history)
                    time.sleep(2)

            # 2. DMs (Bandeja principal)
            page.goto("https://x.com/messages", timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(5)

            unlock_chat_if_needed(page)

            convos = page.locator('a[href*="/i/chat/"]')
            count_c = min(convos.count(), 5)
            print(f"[*] Conversaciones detectadas en bandeja: {convos.count()}")

            for j in range(count_c):
                c = convos.nth(j)
                txt_c = c.inner_text().strip()
                href = c.get_attribute("href") or f"chat_{j}"

                # Si el último mensaje es de Mary ("You:"), ya fue respondido
                lines = [l.strip() for l in txt_c.splitlines() if l.strip()]
                last_line = lines[-1] if lines else ""
                if last_line.startswith("You:") or "You:" in txt_c:
                    continue

                h_c = hash_text(f"{href}_{txt_c}")
                if h_c in history["dms"]:
                    continue

                print(f"[*] Nuevo mensaje no respondido en {href}:\n    \"{txt_c.replace(chr(10), ' | ')}\"")
                c.click()
                time.sleep(3)
                unlock_chat_if_needed(page)

                composer = page.get_by_placeholder("Message").first
                if composer.count() == 0:
                    composer = page.locator('[data-testid="dmComposerTextInput"]').first
                if composer.count() == 0:
                    composer = page.locator('[role="textbox"]').last

                if composer.count() > 0:
                    chat_panel = page.locator('[data-testid="dm-conversation-panel"]').first
                    full_text = chat_panel.inner_text() if chat_panel.count() > 0 else txt_c

                    reply_dm = get_smart_reply(full_text, is_dm=True)
                    composer.click()
                    time.sleep(0.5)
                    composer.fill(reply_dm)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    time.sleep(4)
                    print(f"✅ [DM respondido con éxito]: {reply_dm}")
                    history["dms"].append(h_c)
                    save_history(history)
                    time.sleep(2)

            # 3. Solicitudes de mensajes (Personas nuevas que no seguimos)
            print("\n📬 [CLOUD] Revisando Solicitudes de Mensajes (cuentas nuevas)...")
            for req_url in ["https://x.com/i/chat/requests", "https://x.com/i/chat/requests/other"]:
                try:
                    page.goto(req_url, timeout=45000)
                    page.wait_for_load_state("domcontentloaded")
                    time.sleep(4)
                    unlock_chat_if_needed(page)

                    dismiss = page.locator("text=Dismiss").first
                    if dismiss.count() > 0:
                        dismiss.click()
                        time.sleep(1)

                    req_links = page.locator('a[href*="/i/chat/"]')
                    total_r = req_links.count()
                    for r_idx in range(min(total_r, 4)):
                        req_el = req_links.nth(r_idx)
                        r_txt = req_el.inner_text().strip()
                        r_href = req_el.get_attribute("href") or f"req_{r_idx}"
                        h_r = hash_text(f"{r_href}_{r_txt}")
                        if h_r in history["dms"]:
                            continue

                        req_el.click()
                        time.sleep(3)
                        unlock_chat_if_needed(page)

                        accept_btn = page.get_by_role("button", name="Accept")
                        if accept_btn.count() == 0:
                            accept_btn = page.locator('button:has-text("Accept")')

                        if accept_btn.count() > 0:
                            print(f"[+] Aceptando solicitud de nuevo usuario en {r_href}...")
                            accept_btn.first.click()
                            time.sleep(3)
                            unlock_chat_if_needed(page)

                        composer = page.get_by_placeholder("Message").first
                        if composer.count() == 0:
                            composer = page.locator('[data-testid="dmComposerTextInput"]').first
                        if composer.count() == 0:
                            composer = page.locator('[role="textbox"]').last

                        if composer.count() > 0:
                            chat_panel = page.locator('[data-testid="dm-conversation-panel"]').first
                            full_text = chat_panel.inner_text() if chat_panel.count() > 0 else r_txt
                            reply_text = get_smart_reply(full_text, is_dm=True)
                            composer.click()
                            time.sleep(0.5)
                            composer.fill(reply_text)
                            time.sleep(1)
                            page.keyboard.press("Enter")
                            time.sleep(4)
                            print(f"✅ [Solicitud respondida]: {reply_text}")
                            history["dms"].append(h_r)
                            save_history(history)
                            time.sleep(2)
                except Exception as ex_r:
                    print(f"⚠️ Error en solicitudes ({req_url}): {ex_r}")

        except Exception as e:
            print(f"⚠️ Error en revisión de mensajes: {e}")
        finally:
            browser.close()

def reply_loop(total_minutes: int = 18, interval_seconds: int = 120):
    print(f"\n🔄 [CLOUD LOOP] Vigilante activo: revisando cada {interval_seconds}s durante {total_minutes} minutos...")
    start_time = time.time()
    max_secs = total_minutes * 60
    iteration = 1

    while (time.time() - start_time) < max_secs:
        print(f"\n--- [Ronda {iteration}] Hora: {time.strftime('%H:%M:%S')} UTC ---")
        try:
            reply_all()
        except Exception as e:
            print(f"⚠️ Error en ronda {iteration}: {e}")

        elapsed = time.time() - start_time
        remaining = max_secs - elapsed
        if remaining > interval_seconds:
            print(f"⏳ Esperando {interval_seconds}s para la próxima revisión (restan {int(remaining // 60)} min)...")
            time.sleep(interval_seconds)
            iteration += 1
        else:
            print("🏁 Turno de vigilancia completado. Dando paso al siguiente ciclo programado.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", nargs="?", const="now", choices=["now", "morning", "afternoon", "night", "vip", "poll"])
    parser.add_argument("--reply", action="store_true")
    parser.add_argument("--loop", type=int, default=0, help="Minutos de duración del bucle activo (ej: 18)")

    args = parser.parse_args()
    if args.reply:
        if args.loop > 0:
            reply_loop(total_minutes=args.loop, interval_seconds=120)
        else:
            reply_all()
    elif args.post:
        cat = "night" if args.post == "vip" else ("poll" if args.post == "poll" else args.post)
        post_tweet(category=cat)
    else:
        post_tweet(category="now")

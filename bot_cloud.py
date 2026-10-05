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

            # 2. DMs
            page.goto("https://x.com/messages", timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(4)

            unlock_chat_if_needed(page)

            convos = page.locator('[data-testid="conversation"]')
            count_c = min(convos.count(), 4)
            for j in range(count_c):
                c = convos.nth(j)
                txt_c = c.inner_text()
                h_c = hash_text(txt_c[:100])
                if h_c in history["dms"]:
                    continue

                c.click()
                time.sleep(2)
                unlock_chat_if_needed(page)

                composer = page.get_by_placeholder("Message").first
                if composer.count() == 0:
                    composer = page.locator('[data-testid="dmComposerTextInput"]').first
                if composer.count() == 0:
                    composer = page.locator('[role="textbox"]').last

                if composer.count() > 0:
                    reply_dm = get_smart_reply(txt_c, is_dm=True)
                    composer.click()
                    time.sleep(0.5)
                    composer.fill(reply_dm)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    time.sleep(3)
                    print(f"✅ [DM respondido]: {reply_dm}")
                    history["dms"].append(h_c)
                    save_history(history)
                    time.sleep(2)

        except Exception as e:
            print(f"⚠️ Error en revisión de mensajes: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", nargs="?", const="now", choices=["now", "morning", "afternoon", "night", "vip", "poll"])
    parser.add_argument("--reply", action="store_true")

    args = parser.parse_args()
    if args.reply:
        reply_all()
    elif args.post:
        cat = "night" if args.post == "vip" else ("poll" if args.post == "poll" else args.post)
        post_tweet(category=cat)
    else:
        post_tweet(category="now")

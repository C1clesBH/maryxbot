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

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from tweets_data import get_suggested_tweet_for_now, get_random_tweet
from reply_engine import (
    get_smart_reply,
    load_history,
    save_history,
    needs_vip_link,
    get_hot_lead_followup
)
from voice_engine import get_voice_for_scenario

BASE_DIR = Path(__file__).resolve().parent

def hash_text(text: str) -> str:
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()

def get_browser_context(p):
    auth_token = os.getenv("X_AUTH_TOKEN")
    if not auth_token:
        raise ValueError("❌ Falta la variable de entorno X_AUTH_TOKEN en GitHub Secrets.")

    launch_args = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    try:
        browser = p.chromium.launch(headless=True, args=launch_args)
    except Exception:
        browser = p.chromium.launch(headless=True, channel="chrome", args=launch_args)
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

def unlock_chat_if_needed(page, pin: str = None, timeout: int = 10):
    pin = pin or os.getenv("X_CHAT_PIN", "0416")
    start = time.time()
    while time.time() - start < timeout:
        inputs = page.locator("input").all()
        has_passcode = page.locator("text=Enter Passcode").count() > 0 or (len(inputs) == 4 and page.locator('[data-testid="dmComposerTextInput"]').count() == 0)
        if has_passcode and len(inputs) >= 4:
            print(f"[*] Pantalla de Passcode detectada. Ingresando clave {pin}...")
            for i in range(4):
                inputs[i].click()
                inputs[i].fill(pin[i])
                time.sleep(0.3)
            print(f"[+] PIN {pin} ingresado con éxito.")
            time.sleep(4)
            return True
        time.sleep(0.8)
    return False

def auto_like_fan_interactions(page, history: dict, max_likes: int = 4):
    """
    Da 'Me Gusta' automáticamente a comentarios de fans en las publicaciones de Mary
    y a menciones recibidas, impulsando el alcance del algoritmo de X.
    """
    print("\n❤️ [ENGAGEMENT] Revisando interacciones de fans para repartir Auto-Likes...")
    liked_count = 0
    likes_history = history.setdefault("likes", [])

    # 1. Likes a comentarios en los posts de Mary
    try:
        page.goto("https://x.com/heymaryfitiq", timeout=45000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3.5)

        first_tweet = page.locator('article[data-testid="tweet"]').first
        if first_tweet.count() > 0:
            first_tweet.click()
            time.sleep(3.5)

            thread_tweets = page.locator('article[data-testid="tweet"]')
            total_thread = min(thread_tweets.count(), 8)
            for k in range(1, total_thread):
                if liked_count >= max_likes:
                    break
                t_item = thread_tweets.nth(k)
                txt_item = t_item.inner_text().strip()
                if "@heymaryfitiq" in txt_item[:40]:
                    continue

                h_item = hash_text("like_" + txt_item[:80])
                if h_item in likes_history:
                    continue

                like_btn = t_item.locator('[data-testid="like"]').first
                if like_btn.count() > 0 and like_btn.is_visible():
                    like_btn.click()
                    liked_count += 1
                    likes_history.append(h_item)
                    print(f"❤️ [Auto-Like #{liked_count}]: Like a comentario de fan en publicación.")
                    time.sleep(2)
        save_history(history)
    except Exception as e:
        print(f"⚠️ Aviso en Auto-Like de comentarios de perfil: {e}")

    # 2. Likes a menciones si todavía queda cupo
    if liked_count < max_likes:
        try:
            page.goto("https://x.com/notifications/mentions", timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3.5)

            m_tweets = page.locator('article[data-testid="tweet"]')
            total_m = min(m_tweets.count(), 6)
            for m_idx in range(total_m):
                if liked_count >= max_likes:
                    break
                m_item = m_tweets.nth(m_idx)
                m_txt = m_item.inner_text().strip()
                if "heymaryfit" in m_txt[:50] and m_txt.count("@heymaryfitiq") == 1:
                    continue

                h_m = hash_text("like_" + m_txt[:80])
                if h_m in likes_history:
                    continue

                like_btn = m_item.locator('[data-testid="like"]').first
                if like_btn.count() > 0 and like_btn.is_visible():
                    like_btn.click()
                    liked_count += 1
                    likes_history.append(h_m)
                    print(f"❤️ [Auto-Like #{liked_count}]: Like a mención recibida.")
                    time.sleep(2)
            save_history(history)
        except Exception as e:
            print(f"⚠️ Aviso en Auto-Like de menciones: {e}")

    if liked_count > 0:
        print(f"✨ [Auto-Like finalizado]: Se dieron {liked_count} Me Gusta a fans.")
    else:
        print("[*] No se encontraron tweets nuevos pendientes de Me Gusta.")

def check_hot_leads_followup(page, history: dict, max_followups: int = 2):
    """
    Revisa si hay prospectos calientes (Hot Leads) que recibieron el enlace VIP
    hace más de 48 horas (o FOLLOWUP_HOURS) y no volvieron a responder, para enviarles
    un mensaje de seguimiento seductor.
    """
    hot_leads = history.setdefault("hot_leads", {})
    if not hot_leads:
        return

    followup_hours = float(os.getenv("FOLLOWUP_HOURS", "48.0"))
    now = time.time()
    pending = []

    for chat_id, lead in list(hot_leads.items()):
        status = lead.get("status")
        followup_sent = lead.get("followup_sent", False)
        if status == "vip_sent" and not followup_sent:
            sent_at = lead.get("sent_at", 0)
            elapsed_hrs = (now - sent_at) / 3600.0
            if elapsed_hrs >= followup_hours:
                pending.append((chat_id, lead, elapsed_hrs))

    if not pending:
        print(f"[*] CRM Hot Leads: {len(hot_leads)} registrados. Ninguno supera las {followup_hours}h sin responder.")
        return

    print(f"\n🎯 [CRM HOT LEADS] Encontrados {len(pending)} prospectos para seguimiento tras {followup_hours}h...")
    sent_count = 0

    for chat_id, lead, elapsed_hrs in pending:
        if sent_count >= max_followups:
            break

        name = lead.get("name", "bombón")
        target_url = chat_id if chat_id.startswith("http") else f"https://x.com{chat_id}"
        print(f"[*] Abriendo chat con {name} ({elapsed_hrs:.1f}h sin actividad): {target_url}...")

        try:
            page.goto(target_url, timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(4)
            unlock_chat_if_needed(page)

            composer = page.get_by_placeholder("Message").first
            if composer.count() == 0:
                composer = page.locator('[data-testid="dmComposerTextInput"]').first
            if composer.count() == 0:
                composer = page.locator('[role="textbox"]').last

            if composer.count() > 0:
                followup_text = get_hot_lead_followup(user_name=name)
                print(f"[+] Enviando seguimiento seductor a {name}:\n    \"{followup_text}\"")

                composer.click()
                time.sleep(0.5)
                composer.fill(followup_text)
                time.sleep(1)

                # Voice Note Attachment para Follow-up (ElevenLabs)
                voice_audio = get_voice_for_scenario("followup_48h", user_name=name)
                if voice_audio and voice_audio.exists():
                    try:
                        file_input = page.locator('[data-testid="fileInput"]').first
                        if file_input.count() > 0:
                            print(f"🎙️ [Voice DM Follow-up]: Adjuntando audio ({voice_audio.name})...")
                            file_input.set_input_files(str(voice_audio))
                            time.sleep(2.5)
                    except Exception as ex_vf:
                        print(f"⚠️ Aviso al adjuntar audio de seguimiento: {ex_vf}")

                page.keyboard.press("Enter")
                time.sleep(1)

                send_btn = page.locator('button[aria-label="Send"], button[data-testid="sendDM"], [data-testid="dmComposerSendButton"]').first
                if send_btn.count() > 0 and send_btn.is_visible():
                    send_btn.click()
                time.sleep(3)

                lead["followup_sent"] = True
                lead["followup_at"] = time.time()
                lead["followup_text"] = followup_text
                lead["status"] = "followup_completed"
                save_history(history)

                sent_count += 1
                print(f"🎉 [Seguimiento 48h enviado con éxito a {name}]! 🚀")
                time.sleep(3)
        except Exception as e:
            print(f"⚠️ Error al enviar seguimiento a {name}: {e}")

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
            count = min(tweets.count(), 8)
            for i in range(count):
                tweet = tweets.nth(i)
                txt = tweet.inner_text().strip()

                # Obtener ID único permanente del tweet
                status_link = tweet.locator('a[href*="/status/"]').first
                tweet_href = status_link.get_attribute("href") if status_link.count() > 0 else ""
                tweet_id = tweet_href.split("/status/")[-1].split("?")[0].split("/")[0] if "/status/" in tweet_href else ""
                clean_id = tweet_id if tweet_id else hash_text(txt.splitlines()[0] if txt else "")

                # Evitar auto-responder a tweets de Mary
                if "heymaryfit" in txt[:50] and txt.count("@heymaryfitiq") == 1:
                    continue

                # Si ya fue respondido este tweet específico, OMITIR INMEDIATAMENTE
                if clean_id in history["mentions"] or (tweet_id and tweet_id in history["mentions"]):
                    continue

                # Auto-Like a la mención del fan si no lo tiene
                like_btn = tweet.locator('[data-testid="like"]').first
                if like_btn.count() > 0 and like_btn.is_visible():
                    try:
                        like_btn.click()
                        time.sleep(1)
                    except Exception:
                        pass

                reply = get_smart_reply(txt, is_dm=False)
                reply_btn = tweet.locator('[data-testid="reply"]').first
                if reply_btn.count() > 0:
                    reply_btn.click()
                    time.sleep(1.5)
                    box = page.locator('[data-testid="tweetTextarea_0"]').first
                    box.wait_for(state="visible", timeout=8000)
                    box.fill(reply)
                    time.sleep(1)
                    page.locator('[data-testid="tweetButton"]').first.click()
                    time.sleep(3)
                    print(f"✅ [Mención respondida]: {reply} (ID: {clean_id})")
                    history["mentions"].append(clean_id)
                    if tweet_id:
                        history["mentions"].append(tweet_id)
                    save_history(history)
                    time.sleep(2)

            # 2. DMs (Bandeja principal)
            page.goto("https://x.com/messages", timeout=45000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(4)

            unlock_chat_if_needed(page)

            # Esperar a que cargue la lista de conversaciones
            try:
                page.locator('a[href*="/i/chat/"]').first.wait_for(state="visible", timeout=12000)
            except Exception:
                time.sleep(3)

            convos = page.locator('a[href*="/i/chat/"]')
            count_c = min(convos.count(), 6)
            print(f"[*] Conversaciones detectadas en bandeja: {convos.count()}")

            for j in range(count_c):
                c = convos.nth(j)
                txt_c = c.inner_text().strip()
                href = c.get_attribute("href") or f"chat_{j}"

                # Si el último mensaje es de Mary ("You:" o "Tú:"), ya fue respondido
                lines = [l.strip() for l in txt_c.splitlines() if l.strip()]
                last_line = lines[-1] if lines else ""
                if last_line.startswith("You:") or last_line.startswith("Tú:") or "You:" in last_line or "Tú:" in last_line:
                    continue

                # Hash basado estrictamente en el último mensaje para ignorar cambios de tiempo relativo ("20m", "1h")
                msg_hash = hash_text(f"{href}_{last_line}")
                if msg_hash in history["dms"]:
                    continue

                print(f"[*] Nuevo mensaje pendiente en {href}:\n    \"{last_line}\"")
                c.click()
                time.sleep(3.5)
                unlock_chat_if_needed(page)

                composer = page.locator('div[role="textbox"], [data-testid="dmComposerTextInput"], [placeholder="Message"], [placeholder="Enviar un mensaje"]')
                if composer.count() > 0:
                    reply_dm = get_smart_reply(last_line, is_dm=True)
                    comp = composer.first
                    comp.click()
                    time.sleep(0.5)
                    comp.fill(reply_dm)
                    time.sleep(1)

                    # Voice Note Attachment para VIP (ElevenLabs)
                    if ("t.me" in reply_dm) or needs_vip_link(last_line):
                        lead_name = lines[0] if lines else "bombón"
                        voice_audio = get_voice_for_scenario("vip_invite", user_name=lead_name)
                        if voice_audio and voice_audio.exists():
                            try:
                                file_input = page.locator('[data-testid="fileInput"]').first
                                if file_input.count() > 0:
                                    print(f"🎙️ [Voice DM]: Adjuntando nota de voz ({voice_audio.name})...")
                                    file_input.set_input_files(str(voice_audio))
                                    time.sleep(2.5)
                            except Exception as ex_v:
                                print(f"⚠️ Aviso al adjuntar nota de voz: {ex_v}")

                    page.keyboard.press("Enter")
                    time.sleep(1)
                    send_btn = page.locator('button[aria-label="Send"], button[data-testid="sendDM"], [data-testid="dmComposerSendButton"]').first
                    if send_btn.count() > 0 and send_btn.is_visible():
                        send_btn.click()
                    time.sleep(3)
                    print(f"✅ [DM respondido con éxito]: {reply_dm}")
                    history["dms"].append(msg_hash)

                    # --- CRM HOT LEADS TRACKING ---
                    is_vip_sent = ("t.me" in reply_dm) or needs_vip_link(last_line)
                    lead_name = lines[0] if lines else "bombón"
                    lead_handle = next((l for l in lines if l.startswith("@")), "")
                    if is_vip_sent:
                        history.setdefault("hot_leads", {})[href] = {
                            "name": lead_name,
                            "handle": lead_handle,
                            "status": "vip_sent",
                            "sent_at": time.time(),
                            "last_user_message": last_line,
                            "followup_sent": False,
                            "followup_at": None,
                            "followup_text": None
                        }
                        print(f"🔥 [CRM Lead Caliente]: {lead_name} ({lead_handle}) -> Programado seguimiento 48h.")
                    elif href in history.get("hot_leads", {}):
                        history["hot_leads"][href]["status"] = "engaged"
                        history["hot_leads"][href]["followup_sent"] = True

                    save_history(history)
                    time.sleep(2)

            # 3. Solicitudes de mensajes (Personas nuevas que no seguimos)
            print("\n📬 [CLOUD] Revisando Solicitudes de Mensajes (cuentas nuevas)...")
            for req_url in ["https://x.com/i/chat/requests/other", "https://x.com/i/chat/requests"]:
                try:
                    page.goto(req_url, timeout=45000)
                    page.wait_for_load_state("domcontentloaded")
                    time.sleep(4)
                    unlock_chat_if_needed(page)

                    dismiss = page.locator("text=Dismiss, text=Descartar").first
                    if dismiss.count() > 0 and dismiss.is_visible():
                        dismiss.click()
                        time.sleep(1)

                    req_links = page.locator('a[href*="/i/chat/"]')
                    total_r = req_links.count()
                    if total_r > 0:
                        print(f"[*] Solicitudes pendientes detectadas en {req_url}: {total_r}")

                    for r_idx in range(min(total_r, 6)):
                        req_el = page.locator('a[href*="/i/chat/"]').nth(r_idx)
                        if req_el.count() == 0:
                            break
                        r_txt = req_el.inner_text().strip()
                        r_href = req_el.get_attribute("href") or f"req_{r_idx}"
                        lines_r = [l.strip() for l in r_txt.splitlines() if l.strip()]
                        last_msg = lines_r[-1] if lines_r else r_txt
                        h_r = hash_text(f"{r_href}_{last_msg}")
                        if h_r in history["dms"]:
                            continue

                        print(f"[+] Abriendo solicitud #{r_idx}: {r_href}...")
                        req_el.click()
                        time.sleep(3.5)
                        unlock_chat_if_needed(page)

                        # Buscar botón Accept en español o inglés
                        accept_btn = page.locator('button:has-text("Accept"), button:has-text("Aceptar"), [data-testid*="accept"]')
                        if accept_btn.count() > 0 and accept_btn.first.is_visible():
                            print(f"[+] Aceptando solicitud de nuevo usuario en {r_href}...")
                            accept_btn.first.click()
                            time.sleep(4)
                            unlock_chat_if_needed(page)

                        composer = page.locator('div[role="textbox"], [data-testid="dmComposerTextInput"], [placeholder="Message"], [placeholder="Enviar un mensaje"]')
                        if composer.count() > 0:
                            comp = composer.first
                            reply_text = get_smart_reply(last_msg, is_dm=True)
                            comp.click()
                            time.sleep(0.5)
                            comp.fill(reply_text)
                            time.sleep(1)

                            # Voice Note Attachment si aplica (ElevenLabs)
                            lead_name_req = lines_r[0] if lines_r else "bombón"
                            if ("t.me" in reply_text) or needs_vip_link(last_msg) or any(w in last_msg.lower() for w in ["audio", "voz", "mandame un audio"]):
                                voice_audio = get_voice_for_scenario("vip_invite", user_name=lead_name_req)
                                if voice_audio and voice_audio.exists():
                                    try:
                                        file_input = page.locator('[data-testid="fileInput"]').first
                                        if file_input.count() > 0:
                                            print(f"🎙️ [Voice DM Solicitud]: Adjuntando audio ({voice_audio.name})...")
                                            file_input.set_input_files(str(voice_audio))
                                            time.sleep(2.5)
                                    except Exception as ex_va:
                                        print(f"⚠️ Aviso audio solicitud: {ex_va}")

                            page.keyboard.press("Enter")
                            time.sleep(1)
                            send_btn = page.locator('button[aria-label="Send"], button[data-testid="sendDM"], [data-testid="dmComposerSendButton"]').first
                            if send_btn.count() > 0 and send_btn.is_visible():
                                send_btn.click()
                            time.sleep(3)
                            print(f"✅ [Solicitud respondida con éxito]: {reply_text}")
                            history["dms"].append(h_r)

                            # --- CRM HOT LEADS TRACKING EN SOLICITUDES ---
                            is_vip_req = ("t.me" in reply_text) or needs_vip_link(last_msg)
                            lead_name_req = lines_r[0] if lines_r else "bombón"
                            lead_handle_req = next((l for l in lines_r if l.startswith("@")), "")
                            if is_vip_req:
                                history.setdefault("hot_leads", {})[r_href] = {
                                    "name": lead_name_req,
                                    "handle": lead_handle_req,
                                    "status": "vip_sent",
                                    "sent_at": time.time(),
                                    "last_user_message": last_msg,
                                    "followup_sent": False,
                                    "followup_at": None,
                                    "followup_text": None
                                }
                                print(f"🔥 [CRM Lead Caliente en Solicitud]: {lead_name_req} ({lead_handle_req}) -> Programado seguimiento 48h.")

                            save_history(history)
                            time.sleep(2)
                except Exception as ex_r:
                    print(f"⚠️ Error en solicitudes ({req_url}): {ex_r}")

            # 4. CRM: Seguimiento automático a Hot Leads (48 horas tras recibir link VIP)
            try:
                check_hot_leads_followup(page, history, max_followups=2)
            except Exception as ex_fu:
                print(f"⚠️ Error en seguimiento a Hot Leads: {ex_fu}")

            # 5. Engagement Algorítmico: Auto-Like a comentarios y menciones de fans
            try:
                auto_like_fan_interactions(page, history, max_likes=4)
            except Exception as ex_al:
                print(f"⚠️ Error en Auto-Like a interacciones: {ex_al}")

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
    parser.add_argument("--autolike", action="store_true", help="Ejecutar solo el módulo de Auto-Like a fans")
    parser.add_argument("--followup", action="store_true", help="Ejecutar solo el seguimiento a Hot Leads pendientes")
    parser.add_argument("--loop", type=int, default=0, help="Minutos de duración del bucle activo (ej: 18)")

    args = parser.parse_args()
    if args.autolike:
        with sync_playwright() as p:
            browser, context = get_browser_context(p)
            page = context.new_page()
            try:
                hist = load_history()
                auto_like_fan_interactions(page, hist, max_likes=5)
            finally:
                browser.close()
    elif args.followup:
        with sync_playwright() as p:
            browser, context = get_browser_context(p)
            page = context.new_page()
            try:
                hist = load_history()
                check_hot_leads_followup(page, hist, max_followups=3)
            finally:
                browser.close()
    elif args.reply:
        if args.loop > 0:
            reply_loop(total_minutes=args.loop, interval_seconds=120)
        else:
            reply_all()
    elif args.post:
        cat = "night" if args.post == "vip" else ("poll" if args.post == "poll" else args.post)
        post_tweet(category=cat)
    else:
        post_tweet(category="now")

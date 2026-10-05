# ☁️ Guía: Cómo activar el Bot 24/7 en GitHub Actions (Gratis)

Con esta configuración, **tu computadora puede estar 100% apagada o desconectada**, y los servidores de GitHub publicarán y responderán mensajes por vos en X todos los días automáticamente.

---

## 📁 Carpeta de archivos listos para GitHub
Todo está preparado en:
`C:\Users\VICTUS-PC\Documents\mary-bot-github\`

Contiene:
* `.github/workflows/auto_post.yml`: Publica tweets a las 07:30, 14:00, 18:30 y 22:30 hs.
* `.github/workflows/auto_reply.yml`: Revisa y responde DMs y menciones cada 2 horas.
* `bot_cloud.py`: Script optimizado para la nube.
* `tweets_data.py`: Banco de tweets.
* `reply_engine.py`: Motor inteligente de respuestas.
* `assets/img/`: Las fotos oficiales de Mary.
* `requirements.txt`: Dependencias de Python.

---

## 🚀 Paso 1: Crear el repositorio en GitHub

1. Entrá a tu cuenta en [github.com](https://github.com/) y hacé clic en **New repository** (o Nuevo Repositorio).
2. **Nombre del repositorio:** `mary-x-bot` (o el que quieras).
3. **Visibilidad:** Seleccioná **Private** (Privado) para que tus fotos y configuraciones sean secretas.
4. Hacé clic en **Create repository**.

---

## 📤 Paso 2: Subir los archivos

En la pantalla que te aparece en GitHub, tenés dos opciones:

### Opción A (La más fácil, sin comandos):
1. Hacé clic en el enlace azul que dice **"uploading an existing file"** (subir archivos existentes).
2. Arrastrá todos los archivos y carpetas que están adentro de `C:\Users\VICTUS-PC\Documents\mary-bot-github` hacia la ventana de GitHub.
3. Hacé clic en **Commit changes** (Guardar cambios).

---

## 🔑 Paso 3: Agregar tu Secreto (1 minuto)

Para que los servidores de GitHub puedan publicar en tu cuenta sin que nadie vea tu clave:

1. En tu repositorio de GitHub, andá a la pestaña **Settings** (Configuración) arriba a la derecha.
2. En el menú de la izquierda, hacé clic en **Secrets and variables** ➡️ **Actions**.
3. Hacé clic en el botón verde **New repository secret**.
4. Agregá el siguiente secreto:
   * **Name:** `X_AUTH_TOKEN`
   * **Secret:** `f35f3531877175f977eeaef7457b8884739fba4c`
5. *(Opcional)* Creá otro llamado `MARY_TELEGRAM_VIP` con el enlace de tu bot de Telegram.

---

## 🎉 ¡Listo! El Bot ya está en la Nube 24/7

A partir de este momento:
* Cada día a las **07:30 AM, 14:00 PM, 18:30 PM y 22:30 PM**, GitHub despertará una máquina virtual gratuita, publicará el tweet correspondiente con foto de Mary y se apagará.
* Cada 2 horas revisará los mensajes privados y menciones para responderlos.
* Si querés probarlo o publicar un tweet manual desde el celular o cualquier computadora:
  * Vas a la pestaña **Actions** en tu GitHub ➡️ **Publicador Automático de Mary** ➡️ **Run workflow** 🚀.

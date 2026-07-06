#!/usr/bin/env python3
"""
Bot Telegram interactif — automatisation complète pour un canal.

CE QUE FAIT CE BOT :
1. Vous lui envoyez du contenu en message privé (texte, photo ou vidéo)
   -> il l'ajoute à sa file d'attente.
2. Chaque jour, à l'heure configurée, il publie automatiquement le contenu
   le plus ancien de la file sur votre canal.
3. Si la file est vide, il republie le dernier contenu envoyé, en changeant
   la présentation (voir styles.py) pour ne pas paraître identique chaque jour.
4. Il répond automatiquement aux commentaires dans le groupe de discussion
   lié à votre canal : d'abord via des règles simples (rules.py, gratuit),
   puis via l'IA si aucune règle ne correspond (ai_reply.py, optionnel).
5. Envoyez /stop pour mettre en pause la publication quotidienne.
   Envoyez à nouveau du contenu pour relancer automatiquement.

COMMANDES :
/start   -> message d'accueil et instructions
/stop    -> met en pause les publications automatiques
/status  -> affiche l'état actuel (file d'attente, pause ou non)
"""
import logging
from datetime import time as dtime

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)

import config
import storage
import rules
import ai_reply
import styles

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("telegram-bot")


# =====================================================================
# COMMANDES DU PROPRIÉTAIRE (message privé uniquement)
# =====================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.OWNER_ID:
        return
    await update.message.reply_text(
        "🤖 Bot d'automatisation prêt !\n\n"
        "Envoyez-moi un texte, une photo ou une vidéo : je la publierai "
        "automatiquement sur votre canal chaque jour.\n\n"
        "/status — voir l'état actuel\n"
        "/stop — mettre en pause les publications"
    )


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.OWNER_ID:
        return
    storage.set_paused(True)
    await update.message.reply_text("⏸️ Publications automatiques mises en pause. Envoyez un nouveau contenu pour relancer.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.OWNER_ID:
        return
    queue = storage.load_queue()
    state = storage.load_state()
    texte = (
        f"📋 File d'attente : {len(queue)} élément(s)\n"
        f"⏯️ État : {'en pause' if state['paused'] else 'actif'}\n"
    )
    if state.get("last_posted_item"):
        texte += "🕐 Un contenu a déjà été publié au moins une fois.\n"
    await update.message.reply_text(texte)


async def handle_owner_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reçoit le contenu envoyé en privé par le propriétaire et l'ajoute à la file."""
    if update.effective_user.id != config.OWNER_ID:
        return

    message = update.message
    item = {"caption": message.caption or message.text or ""}

    if message.photo:
        item["type"] = "photo"
        item["file_id"] = message.photo[-1].file_id
    elif message.video:
        item["type"] = "video"
        item["file_id"] = message.video.file_id
    elif message.text:
        item["type"] = "text"
    else:
        return  # type de message non pris en charge (sticker, audio, etc.)

    storage.add_to_queue(item)
    storage.set_paused(False)  # un nouvel envoi relance automatiquement les publications

    await message.reply_text("✅ Contenu ajouté à la file de publication.")


# =====================================================================
# PUBLICATION QUOTIDIENNE AUTOMATIQUE
# =====================================================================

async def post_daily_content(context: ContextTypes.DEFAULT_TYPE):
    state = storage.load_state()
    if state.get("paused"):
        log.info("Publication ignorée : en pause.")
        return

    item = storage.pop_next()
    reused = False
    if item is None:
        item = state.get("last_posted_item")
        reused = True
        if item is None:
            log.info("Rien à publier : file vide et aucun historique.")
            return

    style_index = storage.next_style_index(len(styles.STYLE_TEMPLATES)) if reused else 0
    caption = styles.apply_style(item.get("caption", ""), style_index)

    try:
        if item["type"] == "text":
            await context.bot.send_message(chat_id=config.CHANNEL_ID, text=caption or "📢")
        elif item["type"] == "photo":
            await context.bot.send_photo(chat_id=config.CHANNEL_ID, photo=item["file_id"], caption=caption)
        elif item["type"] == "video":
            await context.bot.send_video(chat_id=config.CHANNEL_ID, video=item["file_id"], caption=caption)
        storage.set_last_posted(item)
        log.info("Publication envoyée avec succès (type=%s, réutilisé=%s).", item["type"], reused)
    except Exception as e:
        log.error("Échec de la publication : %s", e)


# =====================================================================
# RÉPONSES AUTOMATIQUES AUX COMMENTAIRES (groupe de discussion lié)
# =====================================================================

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None or message.text is None:
        return
    if message.is_automatic_forward:
        return  # ignore les messages transférés automatiquement depuis le canal
    if message.from_user and message.from_user.is_bot:
        return

    reponse = rules.match_rule(message.text)
    if reponse is None and ai_reply.is_enabled():
        reponse = ai_reply.generate_reply(message.text)

    if reponse:
        await message.reply_text(reponse)


# =====================================================================
# DÉMARRAGE
# =====================================================================

def main():
    missing = config.check_required()
    if missing:
        raise RuntimeError(f"Variables manquantes dans .env : {', '.join(missing)}")

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("status", cmd_status))

    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & (filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND,
        handle_owner_content,
    ))

    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND,
        handle_group_message,
    ))

    app.job_queue.run_daily(
        post_daily_content,
        time=dtime(hour=config.POST_HOUR_UTC, minute=config.POST_MINUTE_UTC),
    )

    log.info("Bot démarré. Publication quotidienne prévue à %02d:%02d UTC.",
              config.POST_HOUR_UTC, config.POST_MINUTE_UTC)
    app.run_polling()


if __name__ == "__main__":
    main()

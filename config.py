"""
Chargement centralisé de la configuration depuis le fichier .env
Voir .env.example et README.md pour savoir comment obtenir chaque valeur.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0") or 0)
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

POST_HOUR_UTC = int(os.environ.get("POST_HOUR_UTC", "9"))
POST_MINUTE_UTC = int(os.environ.get("POST_MINUTE_UTC", "0"))


def check_required() -> list[str]:
    """Retourne la liste des variables obligatoires manquantes."""
    missing = []
    if not BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not OWNER_ID:
        missing.append("OWNER_ID")
    if not CHANNEL_ID:
        missing.append("TELEGRAM_CHANNEL_ID")
    if not GROUP_ID:
        missing.append("TELEGRAM_GROUP_ID")
    return missing

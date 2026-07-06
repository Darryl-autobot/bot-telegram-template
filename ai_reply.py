"""
Génère une réponse intelligente via l'API Anthropic (Claude) quand aucune
règle par mot-clé ne correspond au message reçu.

Nécessite ANTHROPIC_API_KEY dans le .env — sinon ce module est simplement
désactivé et le bot n'utilisera que les règles (rules.py).
"""
import logging
from config import ANTHROPIC_API_KEY

log = logging.getLogger("ai_reply")

_client = None
if ANTHROPIC_API_KEY:
    try:
        from anthropic import Anthropic
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        log.warning("Impossible d'initialiser le client Anthropic: %s", e)

SYSTEM_PROMPT = (
    "Tu réponds à des commentaires sur un canal Telegram professionnel "
    "(business/publicité). Réponds en français, de façon brève (1-2 phrases), "
    "chaleureuse et orientée client. Si la question porte sur un prix, un "
    "délai ou un détail que tu ne connais pas, invite la personne à écrire "
    "en message privé plutôt que d'inventer une information."
)


def is_enabled() -> bool:
    return _client is not None


def generate_reply(message_text: str) -> str | None:
    """Retourne une réponse générée par l'IA, ou None si le module est désactivé
    ou si l'appel échoue."""
    if _client is None:
        return None
    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message_text}],
        )
        text_blocks = [b.text for b in response.content if b.type == "text"]
        return "".join(text_blocks).strip() or None
    except Exception as e:
        log.error("Erreur lors de l'appel à l'API Anthropic: %s", e)
        return None

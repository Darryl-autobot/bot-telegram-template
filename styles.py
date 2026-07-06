"""
Formulations utilisées pour varier la présentation d'un même contenu
quand il est republié plusieurs jours de suite (tant qu'aucun nouveau
contenu n'a été envoyé par le propriétaire).
"""

STYLE_TEMPLATES = [
    "🔥 {caption}",
    "✨ À ne pas manquer :\n\n{caption}",
    "📢 Rappel :\n\n{caption}",
    "👀 Regardez ça :\n\n{caption}",
    "💥 {caption}\n\n👉 Contactez-nous en message privé pour en savoir plus.",
    "🌟 {caption}",
    "📌 {caption}\n\nPartagez si ça vous plaît !",
]


def apply_style(caption: str, style_index: int) -> str:
    template = STYLE_TEMPLATES[style_index % len(STYLE_TEMPLATES)]
    if caption:
        return template.format(caption=caption)
    # Pas de texte fourni par l'utilisateur : on retire le placeholder proprement
    return template.replace("{caption}", "").strip()

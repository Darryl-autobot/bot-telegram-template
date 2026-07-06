"""
Règles simples pour les réponses automatiques aux commentaires du groupe.
Gratuit et instantané — utilisé EN PRIORITÉ avant de recourir à l'IA.

Pour personnaliser : ajoutez/modifiez des entrées dans RULES.
Chaque entrée = liste de mots-clés (variantes) -> réponse à envoyer.
La recherche est insensible à la casse et fonctionne si UN des mots-clés
apparaît n'importe où dans le message.
"""

RULES: list[tuple[list[str], str]] = [
    (["prix", "combien", "tarif", "coût", "cout"],
     "Merci pour votre intérêt ! 🙏 Pour connaître nos tarifs actuels, contactez-nous en message privé, on vous répond très vite."),

    (["livraison", "délai", "delai", "expédition", "expedition"],
     "Nos délais de livraison varient selon votre localisation. Envoyez-nous un message privé avec votre ville pour un délai précis 📦"),

    (["disponible", "stock", "dispo"],
     "Merci de votre message ! Écrivez-nous en privé pour connaître la disponibilité exacte du produit qui vous intéresse 😊"),

    (["merci", "super", "top", "génial", "genial"],
     "Merci beaucoup pour votre retour, ça nous fait très plaisir ! 🙌"),

    (["contact", "numéro", "numero", "téléphone", "telephone", "whatsapp"],
     "Vous pouvez nous contacter directement en message privé sur ce compte, on vous répond rapidement 📩"),
]


def match_rule(message_text: str) -> str | None:
    """Retourne la réponse correspondante si un mot-clé est trouvé, sinon None."""
    if not message_text:
        return None
    text_lower = message_text.lower()
    for keywords, response in RULES:
        if any(keyword in text_lower for keyword in keywords):
            return response
    return None

"""
Mapping des voix OpenAI (attendues par le proxy Haiko) vers des descriptions
de style VoxCPM2 Voice Design.

Placeholder temporaire : tant qu'aucune voix clonee (reference_wav_path) n'est
disponible, chaque "voix OpenAI" est simulee par une description de style
textuelle passee au modele. A remplacer par de vrais fichiers de reference
des que des voix autorisees seront enregistrees (cf. recommandation prise
vocale transmise au client).
"""

OPENAI_VOICE_TO_STYLE: dict[str, str] = {
    "alloy": "voix neutre et posee",
    "echo": "voix masculine, calme et grave",
    "fable": "voix chaleureuse et expressive",
    "onyx": "voix masculine, grave et posee",
    "nova": "voix feminine, jeune et dynamique",
    "shimmer": "voix feminine, douce et claire",
}

DEFAULT_STYLE = "voix neutre et posee"


def resolve_style(voice: str) -> str:
    """Retourne la description de style VoxCPM2 pour une voix OpenAI donnee."""
    return OPENAI_VOICE_TO_STYLE.get(voice.lower(), DEFAULT_STYLE)


def list_voices() -> list[dict]:
    """Liste des voix exposees, format compatible avec le proxy Haiko existant."""
    return [{"id": voice_id} for voice_id in OPENAI_VOICE_TO_STYLE]

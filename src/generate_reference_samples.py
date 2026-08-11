"""
Genere le jeu d'echantillons de reference du projet Feogasy (binome TTS).
Utilise exclusivement le Voice Design de VoxCPM2 (voix synthetique,
aucune donnee/voix humaine reelle utilisee - pas de question de consentement).
"""

from pathlib import Path
from voxcpm import VoxCPM
import soundfile as sf
import json

OUTPUT_DIR = Path("eval/reference_samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Phrases de reference couvrant differents cas d'usage attendus par le projet
REFERENCE_SENTENCES = [
    {
        "id": "ref_001_simple",
        "text": "(voix neutre et posee) Bonjour, ceci est un test de synthese vocale.",
        "description": "Phrase courte, cas simple",
    },
    {
        "id": "ref_002_longue",
        "text": "(voix neutre et posee) Le prototype vocal Feogasy doit etre capable de synthetiser des phrases plus longues et complexes, avec plusieurs propositions et une intonation naturelle tout au long de l'enonce.",
        "description": "Phrase longue, test de stabilite",
    },
    {
        "id": "ref_003_chiffres",
        "text": "(voix neutre et posee) Le rendez-vous est prevu le 7 aout 2026 a 10 heures 30, pour une duree de 30 minutes.",
        "description": "Chiffres et dates",
    },
    {
        "id": "ref_004_noms_propres",
        "text": "(voix neutre et posee) Mahefa et David travaillent sur le projet Feogasy avec le modele VoxCPM2.",
        "description": "Noms propres",
    },
    {
        "id": "ref_005_expressive",
        "text": "(voix enthousiaste et joyeuse) Excellente nouvelle, le test fonctionne parfaitement !",
        "description": "Test Voice Design expressif",
    },
]

def main():
    print("Chargement du modele VoxCPM2...")
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)

    manifest = []

    for item in REFERENCE_SENTENCES:
        print(f"Generation : {item['id']}")

        wav = model.generate(
            text=item["text"],
            cfg_value=2.0,
            inference_timesteps=10,
        )

        output_path = OUTPUT_DIR / f"{item['id']}.wav"
        sf.write(output_path, wav, model.tts_model.sample_rate)

        manifest.append({
            "id": item["id"],
            "audio": f"{item['id']}.wav",
            "text": item["text"],
            "description": item["description"],
            "sample_rate": model.tts_model.sample_rate,
            "source": "voxcpm2_voice_design",
            "voice_authorized": True,
            "voice_note": "Voix synthetique generee par Voice Design, aucune personne reelle",
        })

    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n{len(manifest)} echantillons generes dans {OUTPUT_DIR}/")
    print(f"Manifest : {manifest_path}")

if __name__ == "__main__":
    main()

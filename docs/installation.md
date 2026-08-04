# Installation et contraintes VoxCPM2

**Dépôt officiel :** https://github.com/OpenBMB/VoxCPM
**Documentation officielle :** https://voxcpm.readthedocs.io/en/latest/
**Licence :** Apache-2.0 (open source, utilisation commerciale autorisée)

## Vue d'ensemble

VoxCPM est un système de synthèse vocale (TTS) sans tokenizer, qui génère directement des représentations de parole continues via une architecture de diffusion autorégressive de bout en bout.

**VoxCPM2** est la version la plus récente : un modèle de 2 milliards de paramètres, entraîné sur plus de 2 millions d'heures de données vocales multilingues. Il prend en charge 30 langues, la conception de voix (Voice Design), le clonage de voix contrôlable, et une sortie audio 48kHz qualité studio. Basé sur un socle MiniCPM-4.

**Langues officiellement supportées (30) :** arabe, birman, chinois, danois, néerlandais, anglais, finnois, français, allemand, grec, hébreu, hindi, indonésien, italien, japonais, khmer, coréen, lao, malais, norvégien, polonais, portugais, russe, espagnol, swahili, suédois, tagalog, thaï, turc, vietnamien.

⚠️ **Le malgache ne fait pas partie des langues officiellement supportées.** Le projet Feogasy devra passer par une adaptation/fine-tuning pour le malgache — cohérent avec l'objectif du mois 1 qui ne vise pas encore une qualité commerciale.

## Prérequis

| Élément | Exigence |
|---|---|
| Python | ≥ 3.10 et < 3.13 |
| PyTorch | ≥ 2.5.0 |
| CUDA | ≥ 12.0 |
| VRAM (VoxCPM2, 2B) | ~8 Go minimum |

Notre serveur : RTX 4090 24 Go — largement suffisant pour VoxCPM2 (8 Go requis), avec de la marge pour l'entraînement LoRA.

## Installation de base

```bash
pip install voxcpm
```

Ou via ModelScope (alternative pour télécharger les poids) :

```bash
pip install modelscope
```

```python
from modelscope import snapshot_download
snapshot_download("OpenBMB/VoxCPM2", local_dir='./pretrained_models/VoxCPM2')
```

## Test d'inférence minimal (Python)

À utiliser uniquement avec une voix et des données dont l'usage est autorisé (règle du projet) :

```python
from voxcpm import VoxCPM
import soundfile as sf

model = VoxCPM.from_pretrained(
    "openbmb/VoxCPM2",
    load_denoiser=False,
)

wav = model.generate(
    text="Texte de test autorisé.",
    cfg_value=2.0,
    inference_timesteps=10,
    seed=42,
)
sf.write("demo.wav", wav, model.tts_model.sample_rate)
```

## Utilisation en ligne de commande (CLI)

```bash
# Conception de voix (sans audio de référence)
voxcpm design \
  --text "Texte à synthétiser." \
  --output out.wav

# Clonage de voix (avec audio de référence)
voxcpm clone \
  --text "Démonstration de clonage de voix." \
  --reference-audio chemin/vers/voix.wav \
  --output out.wav
```

## Démo web locale

```bash
python app.py --port 8808
# puis ouvrir : http://localhost:8808
```

Choix du device : `--device auto|cpu|mps|cuda|cuda:N`

## Performances de référence (RTX 4090)

| Modèle | RTF (PyTorch standard) | RTF (Nano-vLLM) | VRAM |
|---|---|---|---|
| VoxCPM2 (2B) | ~0,30 | ~0,13 | ~8 Go |
| VoxCPM1.5 (0,6B) | ~0,15 | ~0,08 | ~6 Go |

→ À comparer à l'objectif du dossier projet : RTF < 0,5 et première portion audio < 1,5 s sur RTX 4090.

## Fine-tuning (LoRA)

VoxCPM prend en charge le fine-tuning complet (SFT) et le fine-tuning LoRA (recommandé, plus léger). Avec seulement 5 à 10 minutes d'audio, une adaptation à un locuteur, une langue ou un domaine spécifique est possible — pertinent pour l'adaptation au malgache prévue en semaines 6-8 du projet.

```bash
python scripts/train_voxcpm_finetune.py \
    --config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml
```

## Risques et limites signalés par l'éditeur (OpenBMB)

- **Usage détourné :** le clonage de voix peut produire une parole synthétique très réaliste. Il est strictement interdit d'utiliser VoxCPM pour l'usurpation d'identité, la fraude ou la désinformation. Tout contenu généré doit être clairement marqué comme tel — cohérent avec l'exigence du projet de marquer l'« audio synthétique ».
- **Stabilité de la génération contrôlable :** les résultats de Voice Design et de clonage contrôlable peuvent varier d'une exécution à l'autre ; plusieurs tentatives (1 à 3) peuvent être nécessaires.
- **Couverture linguistique :** seules 30 langues sont officiellement supportées ; les langues absentes de cette liste (dont le malgache) nécessitent des tests directs ou un fine-tuning.
- **Déploiement en production :** l'éditeur recommande des tests et une évaluation de sécurité approfondis avant tout usage commercial.

## État actuel de l'installation (à compléter par Mahefa)

- [ ] Installation de base réussie : oui / non
- [ ] Version CUDA locale confirmée : ___
- [ ] VRAM disponible confirmée : ___
- [ ] Première inférence de test réussie : oui / non
- [ ] Décision : **baseline exécutable** / **bloquée pour une cause identifiée**
- [ ] Si bloqué : commande exacte + message d'erreur ci-dessous   EOF

# OpenAI TTS Bridge — VoxCPM2

Serveur frontal exposant VoxCPM2 avec un contrat compatible OpenAI
(`POST /v1/audio/speech`), pour s'integrer directement avec le proxy
existant du depot Haiko (`gateway/http/routers/audio.py`) sans que ce
dernier ait besoin d'etre modifie.

## Statut

**Squelette d'anticipation** — prepare avant confirmation du client sur
l'approche technique (cf. `docs/integration-haiko/contexte.md`). A ajuster
une fois la reponse recue.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn src.openai_tts_bridge.main:app --host 0.0.0.0 --port 8000
```

## Configuration cote Haiko (une fois ce serveur deploye)

Dans l'admin Haiko (Settings > Audio), configurer :
- `url` : l'adresse de ce serveur (ex: http://votre-serveur:8000)
- `key` : n'importe quelle valeur (non verifiee pour l'instant, a securiser
  avant production)
- `model` : ignore, VoxCPM2 est le seul moteur
- `speaker` : une des voix listees par `GET /v1/audio/voices`
  (alloy, echo, fable, onyx, nova, shimmer)

## Limitations connues (etat actuel)

- **Mapping voix = style textuel, pas de vraie voix clonee.** Chaque "voix
  OpenAI" declenche une description Voice Design VoxCPM2 (voir
  `voice_mapping.py`), pas un clonage a partir d'un audio de reference reel.
  A remplacer des qu'une vraie prise vocale autorisee sera disponible.
- **Pas d'authentification** sur ce serveur - a ajouter avant tout usage
  au-dela d'un test interne.
- **response_format** : seul `wav` est supporte (le proxy Haiko doit
  accepter ce format, a verifier cote client).
- **Pas de streaming** — generation bloquante, chaque requete attend la fin
  de la synthese avant de repondre.
- **STT non implemente** — hors perimetre du binome TTS.

## A faire avant un usage en production

- [ ] Authentification (verification de la clef envoyee par le proxy)
- [ ] Vraies voix clonees (reference_wav_path) au lieu du mapping par style
- [ ] Tests automatises (cf. tests/test_media.py cote Haiko comme reference
      de contrat)
- [ ] Deploiement sur le serveur GPU (RTX 4090) plutot qu'en local/CPU
- [ ] Gestion d'erreur plus fine (texte trop long, langue non supportee...)

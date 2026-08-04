# Contrat API — POST /v1/audio/speech

**À faire ensemble :** Mahefa + David, avec relecture Data et Backend
**Statut :** brouillon à valider en semaine 1

## Objectif

Définir un contrat stable pour l'endpoint de synthèse vocale, utilisé par le prototype Feogasy (chaîne Voix → Whisper → API LLM → VoxCPM2). Ce contrat doit être gelé tôt : toute modification nécessite une revue inter-binômes et l'accord du responsable technique.

## Interface attendue (base, d'après le dossier projet)

POST /v1/audio/speech

Flux audio marqué comme synthétique, avec la version du modèle indiquée.

## 1. Requête — champs à définir ensemble

| Champ | Description | Statut |
|---|---|---|
| text | Texte à synthétiser | À valider |
| voice / speaker_id | Identifiant de la voix autorisée à utiliser | À valider |
| language | Langue cible (malgache, français, mixte) | À valider |
| reference_audio | Audio de référence pour clonage (optionnel) | À valider |
| control / style | Instructions de style (vitesse, émotion, ton) | À valider |
| format_sortie | Format audio attendu en sortie (ex: wav, 48kHz) | À valider |

## 2. Réponse — champs obligatoires à définir

| Champ | Description | Statut |
|---|---|---|
| audio | Flux ou fichier audio généré | Obligatoire |
| synthetic_flag | Marquage explicite "audio synthétique" | Obligatoire (garde-fou projet) |
| model_version | Version du modèle VoxCPM2 utilisée | Obligatoire |
| request_id | Identifiant de corrélation (aligné avec Backend/MLOps) | À valider avec Backend |
| duration | Durée de l'audio généré | À valider |
| latency_ms | Latence de génération mesurée | À valider (objectif RTF < 0,5) |

## 3. Erreurs HTTP à définir

| Code | Cas d'usage | Statut |
|---|---|---|
| 400 | Texte vide, paramètres invalides | À valider |
| 401/403 | Authentification/autorisation manquante | À valider avec Backend |
| 404 | Voix ou modèle non trouvé | À valider |
| 422 | Langue non supportée ou paramètres incohérents | À valider |
| 429 | Trop de requêtes simultanées (1-3 utilisateurs visés) | À valider avec Backend |
| 500 | Erreur interne de génération (échec du modèle) | À valider |
| 503 | Service TTS indisponible (GPU occupé, etc.) | À valider avec Backend |

## 4. Points de vigilance spécifiques au binôme TTS

- Le marquage `synthetic_flag` est un garde-fou du projet — ne doit jamais être omis, même en cas d'erreur partielle.
- `model_version` doit permettre de tracer précisément quel checkpoint (baseline, LoRA, etc.) a produit l'audio, utile pour la reproductibilité et le debug.
- Les corpus STT et TTS restent strictement séparés — ce contrat ne doit gérer que la synthèse, pas la transcription.
- Aligner le format des erreurs HTTP avec celui défini par le binôme Backend/MLOps (timeouts, identifiant de corrélation communs à STT/LLM/TTS).

## 5. Processus de relecture

- [ ] Relecture initiale par Mahefa + David.
- [ ] Partage avec le binôme Data/ML Platform (cohérence avec les manifestes TTS).
- [ ] Partage avec le binôme Backend/MLOps (cohérence avec l'orchestration audio → STT → LLM → TTS).
- [ ] Validation senior (le contrat touche une interface partagée).
- [ ] Version gelée committée dans ce fichier.

## Décisions actées (à remplir au fur et à mesure)

(à compléter après la relecture)

## Historique des révisions

| Date | Modification | Validé par |
|---|---|---|
| (à compléter) | Version initiale du brouillon | Mahefa + David |

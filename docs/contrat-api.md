# Contrat API — POST /v1/audio/speech

**A faire ensemble :** Mahefa + David, avec relecture Data et Backend
**Statut :** brouillon v2 — corrige suite a la decouverte de l'API reelle VoxCPM2, encore a relire avec Data/Backend

## Objectif

Definir un contrat stable pour l'endpoint de synthese vocale, utilise par le prototype Feogasy
(chaine Voix -> Whisper -> API LLM -> VoxCPM2). Ce contrat doit etre gele tot : toute modification
necessite une revue inter-binomes et l'accord du responsable technique.

## Interface attendue (base, d'apres le dossier projet)

POST /v1/audio/speech

Flux audio marque comme synthetique, avec la version du modele indiquee.

## Note importante — alignement avec l'API reelle VoxCPM2

La signature reelle de `generate()` (voxcpm 2.0.3, verifiee via `inspect.signature`) est :
generate(text: str, prompt_wav_path: str = None, prompt_text: str = None,
reference_wav_path: str = None, cfg_value: float = 2.0,
inference_timesteps: int = 10, min_len: int = 2, max_len: int = 4096,
normalize: bool = False, denoise: bool = False, retry_badcase: bool = True,
retry_badcase_max_times: int = 3, retry_badcase_ratio_threshold: float = 6.0,
streaming: bool = False)
Consequences sur le contrat :
- Pas de `speaker_id` catalogue : le clonage se fait via un fichier audio de reference
  (`reference_wav_path`) ou via clonage integral (`prompt_wav_path` + `prompt_text`).
- Pas de parametre `language` natif : la langue est inferee automatiquement du texte par le modele.
- Le style/controle (vitesse, emotion, ton) se pilote en integrant une description entre parentheses
  au debut du texte (ex: "(voix calme et posee) Bonjour"), pas via un champ separe au niveau modele.
- Le modele sort nativement en 48kHz : tout autre format necessite une conversion post-traitement
  cote API, pas un parametre du modele.

## 1. Requete — champs a definir ensemble

| Champ | Description | Statut |
|---|---|---|
| text | Texte a synthetiser (la description de style peut y etre integree entre parentheses au debut) | A valider |
| reference_audio | Fichier audio de reference pour clonage (mappe vers reference_wav_path ou prompt_wav_path) | A valider |
| reference_transcript | Transcript exact de l'audio de reference (requis pour Ultimate Cloning, mappe vers prompt_text) | A valider |
| style | Instructions de style en langage naturel — a concatener dans text entre parentheses cote API, avant appel au modele | A valider — decision : champ API distinct fusionne en interne, ou directement dans text ? |
| language | Langue cible declaree par le client (a des fins de validation/filtrage cote API uniquement — n'est PAS transmise au modele, qui infere automatiquement) | A valider — usage a clarifier avec Data (filtrage langues supportees) |
| format_sortie | Format audio de sortie souhaite (implique une conversion post-traitement depuis le 48kHz natif) | A valider |
| cfg_value | Intensite du guidage (defaut modele : 2.0) — exposer ou fixer en interne ? | A trancher |
| inference_timesteps | Nombre d'etapes de diffusion (defaut modele : 10) — impact direct sur le RTF, exposer ou fixer ? | A trancher |
| consentement_ref | Reference/preuve de consentement pour la voix utilisee en reference_audio | A valider avec Data (garde-fou consentement du dossier projet) |

## 2. Reponse — champs obligatoires a definir

| Champ | Description | Statut |
|---|---|---|
| audio | Flux ou fichier audio genere | Obligatoire |
| synthetic_flag | Marquage explicite "audio synthetique" | Obligatoire (garde-fou projet) |
| model_version | Version du modele VoxCPM2 utilisee (traçabilite checkpoint : baseline / LoRA) | Obligatoire |
| request_id | Identifiant de correlation (aligne avec Backend/MLOps) | A valider avec Backend |
| duration | Duree de l'audio genere | A valider |
| latency_ms | Latence absolue de generation mesuree (temps reel, en millisecondes) | A valider |
| rtf | Real-Time Factor mesure (latence generation / duree audio) — distinct de latency_ms, objectif projet < 0,5 sur RTX 4090 | A ajouter — metrique explicitement citee dans les criteres de validation du dossier |
| first_chunk_latency_ms | Latence avant la premiere portion audio (streaming) — objectif projet < 1,5 s sur RTX 4090 | A ajouter si le mode streaming (parametre modele disponible) est expose par l'API |

## 3. Erreurs HTTP a definir

| Code | Cas d'usage | Statut |
|---|---|---|
| 400 | Texte vide, parametres invalides | A valider |
| 401/403 | Authentification/autorisation manquante | A valider avec Backend |
| 404 | Voix de reference ou modele non trouve | A valider |
| 422 | Langue non supportee (parmi les 30 officielles) ou parametres incoherents | A valider |
| 429 | Trop de requetes simultanees (1-3 utilisateurs simultanes vises) — valeur exacte de rate-limit a definir | A valider avec Backend |
| 500 | Erreur interne de generation (echec du modele, ex: retry_badcase epuise) | A valider |
| 503 | Service TTS indisponible (GPU occupe, ex: entrainement STT/TTS en cours sur la RTX 4090 partagee) | A valider avec Backend |

## 4. Points de vigilance specifiques au binome TTS

- Le marquage `synthetic_flag` est un garde-fou du projet — ne doit jamais etre omis, meme en cas d'erreur partielle.
- `model_version` doit permettre de tracer precisement quel checkpoint (baseline, LoRA, etc.) a produit l'audio, utile pour la reproductibilite et le debug.
- Les corpus STT et TTS restent strictement separes — ce contrat ne doit gerer que la synthese, pas la transcription.
- Aligner le format des erreurs HTTP avec celui defini par le binome Backend/MLOps (timeouts, identifiant de correlation communs a STT/LLM/TTS).
- `rtf` et `latency_ms` sont deux metriques distinctes : ne pas les confondre dans l'implementation ou la documentation destinee a Backend.
- Le consentement de la voix de reference (garde-fou projet : "Consentements, pseudonymisation et stockage chiffre") doit etre verifie avant tout appel au modele avec `reference_audio` — a definir precisement avec le binome Data/ML Platform.
- Le GPU (RTX 4090) est partage avec le binome STT — le code 503 doit couvrir le cas de contention GPU.

## 5. Decisions techniques restant a trancher avant relecture externe

- [ ] `style` : champ API distinct fusionne en interne dans `text`, ou le client construit directement le texte avec parentheses ?
- [ ] `cfg_value` et `inference_timesteps` : exposes au client ou fixes en interne (valeurs par defaut du modele) ?
- [ ] `language` : simple filtre de validation cote API, ou supprime du contrat si redondant avec l'inference automatique du modele ?
- [ ] `format_sortie` : formats reellement necessaires pour le prototype (juste wav 48kHz natif, ou conversion requise) ?
- [ ] Mode streaming : prevu pour le prototype (latence <6s) ou hors scope mois 1 ?

## 6. Processus de relecture

- [x] Relecture initiale par Mahefa (corrections techniques suite a la decouverte de l'API reelle).
- [ ] Relecture par David.
- [ ] Partage avec le binome Data/ML Platform (cohérence avec les manifestes TTS, consentement).
- [ ] Partage avec le binome Backend/MLOps (cohérence avec l'orchestration audio -> STT -> LLM -> TTS).
- [ ] Validation senior (le contrat touche une interface partagee).
- [ ] Version gelee committee dans ce fichier.

## Decisions actees (a remplir au fur et a mesure)

(a completer apres la relecture)

## Historique des revisions

| Date | Modification | Valide par |
|---|---|---|
| (a completer) | Version initiale du brouillon | Mahefa + David |
| 07/08/2026 | v2 — corrections d'alignement avec l'API reelle VoxCPM2 (voice/speaker_id, style, language, format_sortie), ajout metriques rtf et first_chunk_latency_ms, ajout garde-fou consentement | Mahefa |

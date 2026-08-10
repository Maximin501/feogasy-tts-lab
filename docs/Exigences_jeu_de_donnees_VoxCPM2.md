# Exigences du jeu de données — VoxCPM2

**Feogasy · Binôme TTS — Données & Évaluation**

---

## 1. Format audio

| Critère | Exigence | Remarque |
|---|---|---|
| Conteneur | **WAV** recommandé | Format standard, sans perte |
| Encodage | PCM 16-bit recommandé | Compatible avec la majorité des pipelines TTS |
| Canaux | Mono | Évite l'ambiguïté de canal pour l'entraînement voix |

## 2. Fréquence d'échantillonnage

- **16 kHz** attendu pour VoxCPM2.
- Le dataloader effectue un **rééchantillonnage automatique** si les fichiers sont dans une autre fréquence — ce n'est donc pas strictement bloquant, mais il est préférable de livrer le corpus déjà à 16 kHz pour éviter toute perte de qualité liée au rééchantillonnage à la volée et pour garder un pipeline homogène.

## 3. Durée des clips

| Plage | Statut |
|---|---|
| 3 à 30 secondes | **Recommandé** |
| < 1 seconde | **Déconseillé** — génère des résultats instables à l'entraînement |
| Entre 1 et 3 secondes | Toléré mais hors plage optimale |
| > 30 secondes | **Déconseillé** — consommation mémoire élevée, filtrage possible en amont de l'entraînement |

## 4. Qualité du signal

Points de vigilance à contrôler avant intégration au corpus :

- **Niveau de pic** : ni saturé (clipping, proche de 0 dBFS) ni trop faible (signal noyé dans le bruit de fond).
- **Silence en bord de clip** : silence en tête/fin à minimiser — un clip doit démarrer et se terminer près du contenu vocal utile.
- **Absence de silence total** : un clip entièrement silencieux n'apporte aucune valeur d'entraînement et doit être écarté.
- **Bruit de fond** : à limiter autant que possible ; privilégier des enregistrements propres.

## 5. Transcription associée

- Chaque fichier audio doit être accompagné d'une **transcription textuelle exacte** du contenu prononcé.
- La transcription ne doit pas être vide.
- La correspondance audio ↔ texte doit être fiable (pas de décalage, pas de contenu tronqué).

## 6. Doublons

- Éviter les fichiers audio strictement identiques dans le corpus (même enregistrement dupliqué sous des noms différents) — cela biaiserait l'entraînement en sur-représentant certains échantillons.

## 7. Couverture linguistique

Conformément à l'objectif du prototype, le corpus doit couvrir :

- Malgache standard
- Français
- Phrases mixtes (code-switching)
- Nombres et noms propres, spécifiquement mentionnés comme catégories à évaluer

## 8. Garde-fous liés aux données (rappel du cadrage du stage)

- **Séparation stricte** des corpus STT et TTS.
- **Consentement** de la voix autorisée, **pseudonymisation** et **stockage chiffré**.
- **Jeux de test gelés** avant toute phase d'adaptation (LoRA) — ne pas les modifier une fois figés.
- **Aucun audio utilisateur** conservé par défaut dans le prototype final.
- Aucun secret ni corpus sensible ne doit être versionné dans Git.

## 9. Synthèse — critères de validation d'un fichier avant intégration

Un fichier est considéré prêt pour le corpus s'il respecte :

1. Format WAV, mono, 16-bit (recommandé)
2. 16 kHz (ou rééchantillonnable proprement)
3. Durée entre 3 et 30 secondes (idéalement)
4. Niveau sonore ni saturé ni trop faible
5. Peu ou pas de silence en bord de clip, pas de silence total
6. Transcription présente, non vide, fidèle au contenu
7. Pas de doublon exact dans le corpus
8. Respect des garde-fous consentement/pseudonymisation/stockage

Ces seuils sont des points de départ à confirmer avec l'équipe après les baselines des semaines 1-2, notamment pour les valeurs exactes de niveau sonore et la limite haute de durée "très longue".

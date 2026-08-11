# Grille d'écoute — Évaluation VoxCPM2 (v1)

**Feogasy · Binôme TTS — Données & Évaluation**

---

## Informations sur la session d'écoute

| Champ | Valeur |
|---|---|
| ID échantillon | ref_001_simple |
| Fichier | eval/reference_samples/ref_001_simple.wav |
| Texte source | "(voix neutre et posee) Bonjour, ceci est un test de synthese vocale." |
| Checkpoint / version du modele | openbmb/VoxCPM2 (baseline, sans fine-tuning) |
| Categorie | Francais |
| Evaluateur | Mahefa |
| Date | 07/08/2026 |
| Ecoute en aveugle (checkpoint masque) | Non — seul checkpoint disponible a ce stade (baseline) |

---

## Partie A — Notes qualitatives (echelle 1 a 5)

| Critere | Note | Commentaire |
|---|---|---|
| **Intelligibilite** | 5 | Contenu parfaitement comprehensible sans effort |
| **Naturalite** | 5 | Voix naturelle, aucun artefact robotique percu |
| **Fidelite** | 5 | Correspond exactement au texte source |
| **Similarite** | N/A | Non applicable — echantillon genere via Voice Design (description textuelle), aucune voix de reference fournie pour comparaison |

**Seuils cibles de reference** : intelligibilite >= 4/5, naturalite >= 3,8/5, similarite >= 4/5 (non applicable ici).
**Resultat : seuils atteints sur tous les criteres applicables.**

---

## Partie B — Detection de defauts

| Defaut | Present ? | Position / horodatage | Commentaire |
|---|---|---|---|
| **Repetition** | Non | — | — |
| **Omission** | Non | — | — |
| **Fin coupee** | Non | — | — |
| **Mot(s) hallucine(s)** | Non | — | — |

**Seuil cible** : aucun mot hallucine dans au moins 98% des phrases evaluees. **Resultat : conforme.**

---

## Commentaire libre de l'evaluateur

Premier echantillon de reference genere via Voice Design VoxCPM2 (voix synthetique,
aucune donnee humaine reelle). Resultat tres satisfaisant pour une baseline S1 :
audio clair, naturel, fidele au texte. Confirme que le pipeline modele -> generation
-> ecoute fonctionne de bout en bout. A relancer sur les 4 autres echantillons de
reference et idealement en double-ecoute avec David pour une premiere validation
croisee complete.

---

## Notes d'usage

Evaluation realisee selon la grille v1 de David (docs/Grille_ecoute_VoxCPM2_v1.md).
Premiere application concrete de la grille sur un echantillon reel du projet.

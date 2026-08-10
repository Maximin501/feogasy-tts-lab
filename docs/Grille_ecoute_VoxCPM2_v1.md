# Grille d'écoute — Évaluation VoxCPM2 (v1)

**Feogasy · Binôme TTS — Données & Évaluation**

---

## Informations sur la session d'écoute

| Champ | Valeur |
|---|---|
| ID échantillon | |
| Checkpoint / version du modèle | |
| Catégorie | ☐ Malgache ☐ Français ☐ Mixte (code-switching) ☐ Nombres ☐ Noms propres |
| Évaluateur | |
| Date | |
| Écoute en aveugle (checkpoint masqué) | ☐ Oui ☐ Non |

---

## Partie A — Notes qualitatives (échelle 1 à 5)

| Critère | Définition | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| **Intelligibilité** | Le contenu est compréhensible sans effort, chaque mot est reconnaissable | Incompréhensible | Difficile à suivre | Compréhensible avec effort | Clair, quelques hésitations | Parfaitement clair |
| **Naturalité** | La voix sonne humaine (prosodie, rythme, intonation) et non robotique | Très robotique | Artificiel | Correct mais mécanique | Naturel, quelques artefacts | Indiscernable d'une voix humaine |
| **Fidélité** | Le contenu prononcé correspond exactement au texte source | Contenu très différent | Plusieurs écarts | Quelques écarts mineurs | Fidèle, écart négligeable | Fidèle à 100% |
| **Similarité** | La voix générée ressemble à la voix autorisée de référence | Aucune ressemblance | Faible ressemblance | Ressemblance partielle | Bonne ressemblance | Très proche de la référence |

**Seuils cibles de référence** (à confirmer après baselines S1-S2) : intelligibilité ≥ 4/5, naturalité ≥ 3,8/5, similarité ≥ 4/5.

---

## Partie B — Détection de défauts

| Défaut | Définition | Présent ? | Position / horodatage | Commentaire |
|---|---|---|---|---|
| **Répétition** | Un mot, une syllabe ou un segment audio est répété de façon anormale | ☐ Oui ☐ Non | | |
| **Omission** | Un ou plusieurs mots du texte source sont absents de l'audio généré | ☐ Oui ☐ Non | | |
| **Fin coupée** | L'audio s'arrête avant la fin de la phrase ou du dernier mot | ☐ Oui ☐ Non | | |
| **Mot(s) halluciné(s)** | Un ou plusieurs mots absents du texte source apparaissent dans l'audio | ☐ Oui ☐ Non | | |

**Seuil cible de référence** : aucun mot halluciné dans au moins 98% des phrases évaluées.

---

## Commentaire libre de l'évaluateur

```



```

---

## Notes d'usage

- Une grille est remplie **par échantillon écouté**, pas par lot.
- Écoute en aveugle recommandée pour limiter les biais (checkpoint/version masqué à l'évaluateur).
- En cas de doute sur une note, ré-écouter le passage plutôt que d'estimer.
- Cette version (v1) couvre les 7 critères demandés ; elle pourra être affinée après les premières écoutes (ex. ajout d'une échelle de sévérité pour les défauts, ajout d'un accord inter-évaluateurs si plusieurs personnes notent le même échantillon).

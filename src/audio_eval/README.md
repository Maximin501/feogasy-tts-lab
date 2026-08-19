# Pipeline d'évaluation semi-automatisée — VoxCPM2

**Feogasy · Binôme TTS — Données & Évaluation**

Outil en ligne de commande pour faire écouter des échantillons audio générés
par un ou plusieurs checkpoints VoxCPM2 à un·e évaluateur·rice humain·e, et
enregistrer ses notes selon la grille d'écoute officielle
(`Grille_ecoute_VoxCPM2_v1.md`).

---

## 1. Structure du projet

```
feogasy-tts-lab/
├── src/
│   └── audio_eval/          <- main.py, grille.py, audio_io.py (ce pipeline)
└── eval/
    ├── reference_samples/   <- fichiers .wav à évaluer + manifest.json (optionnel)
    └── reports/             <- CSV de résultats généré ici par défaut
```

| Fichier | Responsabilité |
|---|---|
| `main.py` | Point d'entrée CLI : arguments, orchestration de la session, reprise, gestion de `Ctrl+C`. |
| `grille.py` | Logique métier : structure des échantillons, questions de la grille, lecture/écriture du CSV. |
| `audio_io.py` | E/S audio bas niveau : lecture bloquante du `.wav`, contrôle technique automatique. |

Les trois fichiers doivent rester dans le même dossier (`src/audio_eval/`).
Les chemins par défaut sont calculés par rapport à l'emplacement de
`main.py`, donc valables quel que soit le dossier depuis lequel la commande
est lancée.

---

## 2. Installation

```bash
pip install simpleaudio numpy   # tous deux optionnels mais recommandés
```

- **`simpleaudio`** : lecture audio bloquante en Python pur. À défaut, le
  script se replie automatiquement sur le lecteur système
  (`afplay` / `aplay` / `paplay` / PowerShell selon l'OS).
- **`numpy`** : active les contrôles de niveau (silence, clipping, RMS). À
  défaut, ces contrôles sont simplement ignorés — le reste du programme
  fonctionne quand même.

Aucune autre dépendance n'est requise (stdlib uniquement pour le cœur du
programme).

---

## 3. Utilisation

### Cas simple — sans aucun argument

```bash
python main.py
```

Le script demande le nom de l'évaluateur·rice de façon interactive, et
utilise les chemins par défaut :
- échantillons : `feogasy-tts-lab/eval/reference_samples/`
- sortie : `feogasy-tts-lab/eval/reports/resultats.csv`

C'est le mode à privilégier avec le bouton **Run** de PyCharm.

### Un seul checkpoint

```bash
python main.py --checkpoint "voxcpm2_baseline:../../EVAL/reference_samples" --evaluateur "David" --output "../../EVAL/reports/resultats_baseline.csv"
```

### Comparaison en aveugle de deux checkpoints

```bash
python main.py \
    --checkpoint "ckpt120:./audios/ckpt120" \
    --checkpoint "ckpt150:./audios/ckpt150" \
    --evaluateur "Rina" \
    --blind \
    --seed 42 \
    --output resultats_comparaison.csv
```

En mode `--blind` (avec ≥ 2 checkpoints) :
- le nom réel du checkpoint est masqué à l'écran (affiché comme `Modèle_1`,
  `Modèle_2`, ...) ;
- l'ordre de passage des échantillons est mélangé pour limiter les biais
  d'attente ;
- `--seed` rend ce mélange reproductible d'une exécution à l'autre.

### Avec un manifeste (catégorie + transcription connues à l'avance)

```bash
python main.py \
    --checkpoint "ckpt120:./audios/ckpt120" \
    --manifest ./manifest.json \
    --evaluateur "Rina" \
    --output resultats_ckpt120.csv
```

Si `--manifest` est omis, le script cherche automatiquement un fichier
`manifest.json` ou `manifest.csv` **dans le(s) dossier(s) passés à
`--checkpoint`** (pas ailleurs) et l'utilise s'il le trouve.

---

## 4. Format du manifeste

Le manifeste est optionnel. Il permet de préremplir la **catégorie** et
d'afficher la **transcription de référence** avant l'écoute de chaque
échantillon.

### Format JSON — liste d'objets

```json
[
  {
    "audio": "ref_001_simple.wav",
    "categorie": "Français",
    "text": "Bonjour, ceci est un test de synthèse vocale."
  }
]
```

### Format JSON — dictionnaire indexé par fichier

```json
{
  "ref_001_simple.wav": {
    "categorie": "Français",
    "text": "Bonjour, ceci est un test de synthèse vocale."
  }
}
```

### Format CSV

```csv
fichier,categorie,texte
ref_001_simple.wav,Français,"Bonjour, ceci est un test de synthèse vocale."
```

### Alias de colonnes/clés acceptés

| Champ | Alias reconnus (insensible à la casse) |
|---|---|
| Nom du fichier | `fichier`, `file`, `filename`, `audio` |
| Catégorie | `categorie`, `category` |
| Transcription | `texte`, `text`, `transcription` |
| Voix de référence | `reference_audio`, `audio_reference`, `ref_audio`, `reference` |

Le champ **voix de référence** est optionnel et sert uniquement à la note de
**Similarité**. Le chemin peut être relatif (résolu par rapport au dossier
`--checkpoint` correspondant) ou absolu. S'il est absent, vide, ou si le
fichier qu'il désigne n'existe pas au moment de l'évaluation, la Similarité
est simplement **laissée vide** dans le CSV — aucune écoute comparative
n'est proposée, et aucune note "à l'aveugle" sans point de comparaison
n'est demandée.

Les catégories doivent correspondre exactement à l'une des valeurs suivantes
(sinon le script avertit et redemande une saisie interactive) :
`Malgache`, `Français`, `Mixte (code-switching)`, `Nombres`, `Noms propres`.

Les champs `categorie`/`category` sont optionnels dans le manifeste : s'ils
sont absents ou vides, la catégorie est simplement demandée à l'écran.

---

## 5. Déroulé d'un échantillon

Pour chaque fichier `.wav` à évaluer, dans cet ordre — pensé pour limiter les
biais de jugement (le texte et la voix de référence ne sont montrés/joués
qu'au moment où ils sont réellement nécessaires à la note demandée) :

1. **Contrôle technique automatique** (durée, fréquence, canaux, silence,
   clipping — voir `Exigences_jeu_de_donnees_VoxCPM2.md`). Les alertes sont
   affichées mais **non bloquantes** : c'est à l'évaluateur·rice de les
   confirmer ou non à l'oreille.
2. **▶ Lecture de l'audio TTS** (bloquante).
3. **Catégorie** : reprise du manifeste (si valide) ou saisie interactive.
4. **Intelligibilité** (1-5) — jugée sans connaître le texte source.
5. **Naturalité** (1-5) — idem, à l'oreille seule.
6. **Affichage du texte source de référence** (si présent dans le
   manifeste).
7. **Fidélité** (1-5) — seule note qui nécessite le texte affiché.
8. **Référence disponible ?**
   - **Non** (champ absent du manifeste ou fichier introuvable) →
     Similarité laissée **vide**, pas d'écoute comparative.
   - **Oui** → **▶ Voix de référence**, puis **▶ Audio TTS** rejoués l'un
     après l'autre, puis **Similarité** (1-5) demandée sur cette base de
     comparaison directe.
9. **Partie B — détection de défauts** : Répétition, Omission, Fin coupée,
   Hallucination. Pour chaque défaut signalé "Oui", une position/horodatage
   et un commentaire bref sont demandés séparément.
10. **Commentaire libre** sur l'échantillon.
11. La ligne est **immédiatement écrite et flushée sur disque** (voir §6).

Pour toutes les notes, taper `r` au moment de répondre rejoue le ou les
fichiers audio concernés avant de redemander la note (pour la Similarité,
`r` rejoue la référence puis le TTS, dans cet ordre).

---

## 6. Sauvegarde et reprise de session

- Chaque échantillon évalué est écrit **ligne par ligne** dans le CSV, avec
  `flush()` + `os.fsync()` — aucune perte de données en cas de coupure.
- `Ctrl+C` interrompt proprement la session : les échantillons déjà notés
  restent sauvegardés, un message invite à relancer la même commande pour
  reprendre là où on s'est arrêté.
- La reprise se base sur le triplet **(fichier, checkpoint réel,
  évaluateur)** déjà présent dans le CSV de sortie : un même fichier peut
  donc être évalué par plusieurs personnes différentes dans le même CSV,
  sans que la reprise de l'une saute les échantillons de l'autre.

---

## 7. Colonnes du CSV de sortie

| Colonne | Description |
|---|---|
| `Ordre`, `Fichier`, `Echantillon_ID` | Identification de l'échantillon |
| `Categorie` | Manifeste ou saisie interactive |
| `Checkpoint_reel`, `Evaluateur`, `Date_heure`, `Ecoute_aveugle` | Métadonnées de session |
| `Duree_s`, `Frequence_Hz`, `Canaux`, `Alerte_technique` | Contrôle technique automatique |
| `Intelligibilite`, `Naturalite`, `Fidelite`, `Similarite` | Partie A (notes 1-5) |
| `Repetition`, `Repetition_position`, `Repetition_commentaire` | Partie B |
| `Omission`, `Omission_position`, `Omission_commentaire` | Partie B |
| `FinCoupee`, `FinCoupee_position`, `FinCoupee_commentaire` | Partie B |
| `Hallucination`, `Hallucination_position`, `Hallucination_commentaire` | Partie B |
| `Commentaire_libre` | Commentaire libre final |

---

## 8. Seuils cibles de référence (grille v1)

À confirmer après les baselines S1-S2 :

- Intelligibilité ≥ 4/5
- Naturalité ≥ 3,8/5
- Similarité ≥ 4/5
- Aucun mot halluciné dans ≥ 98 % des phrases évaluées

Ces seuils ne sont pas exploités automatiquement par ce pipeline (qui ne
fait que la **collecte**) — l'analyse comparative (Pandas, graphiques,
comparaison aux seuils) fait l'objet d'un script séparé à venir.

---

## 9. Limites connues / points de vigilance

- **Multi-checkpoints avec manifeste** : la détection automatique du
  manifeste ne cherche que dans le(s) dossier(s) `--checkpoint`, dans
  l'ordre où ils sont passés — le premier `manifest.json`/`manifest.csv`
  trouvé est utilisé pour **tous** les checkpoints.
- **`--blind` + `--seed`** : si une session interrompue est relancée sans
  repasser le même `--seed`, l'ordre mélangé et le mapping
  `Modèle_1`/`Modèle_2` peuvent changer entre deux lancements — à
  documenter si plusieurs personnes reprennent la même session en aveugle.
- **Lecture audio sans `simpleaudio` ni lecteur système disponible** : le
  script demande une écoute manuelle du fichier et attend une touche
  Entrée avant de continuer.

---

## 10. Dépendances

- Python ≥ 3.10 (utilisation de `list[tuple[str, Path]]` en annotation).
- stdlib uniquement pour le cœur du programme.
- `simpleaudio` (optionnel, lecture audio propre).
- `numpy` (optionnel, contrôles de niveau/silence).

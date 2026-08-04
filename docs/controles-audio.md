# Contrôles audio et protocole d'évaluation TTS

**Responsable :** David
**Composant :** Binôme TTS — VoxCPM2

## Objectif

Définir et implémenter les contrôles de qualité audio à appliquer à tout fichier avant intégration au pipeline, ainsi qu'une grille d'écoute pour l'évaluation humaine. Aucune promesse de qualité malgache à ce stade — l'objectif est la reproductibilité et la détection fiable des rejets.

## 1. Contrôles automatiques à implémenter

| Contrôle | Description | Critère de rejet (exemple à ajuster) |
|---|---|---|
| Format | Extension et encodage du fichier | Format non autorisé (ex: autre que .wav) |
| Fréquence d'échantillonnage | Sample rate du fichier | Hors plage attendue (ex: différent de 48kHz pour la sortie VoxCPM2) |
| Canaux | Mono ou stéréo | Nombre de canaux inattendu |
| Durée | Longueur totale du fichier audio | Trop court ou trop long |
| Niveau de pic (peak level) | Amplitude maximale du signal | Saturation (clipping) ou niveau trop faible |
| Silence | Portions de silence anormales | Silence en début/fin ou au milieu au-delà d'un seuil |
| Doublons | Fichiers identiques ou quasi identiques | Hash ou similarité audio au-dessus d'un seuil |
| Transcription manquante | Présence du texte associé à l'audio | Absence de transcription liée |

## 2. Fichiers factices à préparer

- [ ] 1 fichier **valide** respectant tous les contrôles ci-dessus.
- [ ] 1 fichier rejeté pour **mauvais format**.
- [ ] 1 fichier rejeté pour **fréquence d'échantillonnage incorrecte**.
- [ ] 1 fichier rejeté pour **mauvais nombre de canaux**.
- [ ] 1 fichier rejeté pour **durée hors limites** (trop court / trop long).
- [ ] 1 fichier rejeté pour **niveau de pic anormal** (saturé ou trop faible).
- [ ] 1 fichier rejeté pour **silence excessif**.
- [ ] 1 fichier rejeté pour **doublon** d'un autre fichier du jeu de test.
- [ ] 1 fichier rejeté pour **transcription manquante**.

Tous ces fichiers doivent être des données factices ou explicitement autorisées — aucune donnée sensible ni voix réelle non consentie.

## 3. Grille d'écoute (évaluation humaine)

Chaque échantillon audio synthétisé est noté sur les critères suivants (échelle à définir, ex: 1 à 5) :

| Critère | Description |
|---|---|
| Intelligibilité | Le texte est-il compréhensible sans effort ? |
| Naturalité | La voix sonne-t-elle naturelle, sans artefacts robotiques ? |
| Fidélité | Le contenu correspond-il exactement au texte source (pas d'ajout/omission) ? |
| Similarité | La voix ressemble-t-elle à la voix de référence (si clonage) ? |
| Répétition | Y a-t-il des répétitions anormales de mots ou syllabes ? |
| Omission | Des mots ou parties du texte sont-ils manquants ? |
| Fin coupée | L'audio s'arrête-t-il prématurément avant la fin du texte ? |

### Format de la grille (exemple de structure de données)
## 4. Points d'attention pour limiter les biais d'évaluation

- Définir si l'évaluateur connaît le texte source à l'avance ou évalue à l'aveugle.
- Prévoir plusieurs évaluateurs si possible, pour croiser les résultats.
- Randomiser l'ordre des échantillons pour éviter les effets de fatigue ou d'ordre.
- Séparer clairement les échantillons de test gelés des échantillons utilisés pendant l'adaptation LoRA.

## 5. Lien avec le contrat API

Le contrat `POST /v1/audio/speech` doit définir :
- le marquage explicite "audio synthétique" dans la réponse,
- la version du modèle utilisée,
- les erreurs HTTP en cas d'échec de synthèse ou de contrôle audio invalide.

## État actuel (à compléter par David)

- [ ] Contrôles automatiques définis : oui / non
- [ ] Fichiers factices créés (1 valide + rejets) : oui / non
- [ ] Grille d'écoute rédigée (version 1) : oui / non
- [ ] Contrat `POST /v1/audio/speech` relu avec Data et Backend : oui / non

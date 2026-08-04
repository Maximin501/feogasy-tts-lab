# Rapport de blocage — VoxCPM2

**Rempli par :** (Mahefa / David)
**Date :** (jj/mm/aaaa)
**Statut :** bloqué pour une cause identifiée

Ce gabarit sert à documenter précisément un blocage lors de l'installation ou de l'inférence VoxCPM2, conformément au critère de passage de la semaine 1 : une décision explicite "baseline exécutable" ou "bloquée pour une cause identifiée", sans promesse de qualité malgache.

## 1. Résumé du blocage

**Étape concernée :** (installation / chargement du modèle / inférence / fine-tuning / autre)

**Description en une phrase :**
(ex: "L'installation échoue lors du chargement du modèle VoxCPM2 par manque de VRAM disponible.")

## 2. Environnement

| Élément | Valeur |
|---|---|
| OS | Kali Linux (version : ___) |
| Python | (résultat de `python3 --version`) |
| PyTorch | (résultat de `python3 -c "import torch; print(torch.__version__)"`) |
| CUDA (driver) | (résultat de `nvidia-smi` — version en haut à droite) |
| CUDA (toolkit) | (résultat de `nvcc --version` si installé) |
| GPU | (modèle, ex: RTX 4090 24 Go) |
| VRAM disponible au moment du blocage | (résultat de `nvidia-smi` — colonne memory-usage) |
| Version voxcpm | (résultat de `pip show voxcpm`) |

## 3. Commande exacte exécutée
## 4. Message d'erreur complet
## 5. Ce qui a déjà été tenté

- [ ] Vérification de la version CUDA/PyTorch compatible avec les prérequis (Python >= 3.10 <3.13, PyTorch >= 2.5.0, CUDA >= 12.0).
- [ ] Vérification de la VRAM disponible avant lancement (`nvidia-smi`).
- [ ] Redémarrage de l'environnement / du processus GPU.
- [ ] Réinstallation dans un environnement virtuel propre.
- [ ] Test avec un batch/paramètre réduit (si erreur de type "out of memory").
- [ ] Recherche du message d'erreur dans la FAQ officielle (https://voxcpm.readthedocs.io/en/latest/faq.html) ou les issues GitHub du dépôt OpenBMB/VoxCPM.
- [ ] Autre : ___

## 6. Hypothèse de cause probable

(ex: "VRAM insuffisante au moment du chargement car un autre processus GPU tourne en parallèle" / "Version CUDA du driver incompatible avec PyTorch installé" / "Dépendance manquante ou conflit de version")

## 7. Impact sur le planning

- [ ] Bloque uniquement l'inférence de test (baseline reportée).
- [ ] Bloque tout le composant TTS (risque sur le critère de passage semaine 1).
- [ ] Nécessite une intervention GPU/infra (validation senior requise, cf. règle du contrat GPU).

## 8. Action demandée / next step

(ex: "Besoin d'une validation senior pour libérer de la VRAM sur le serveur partagé" / "Besoin d'un accès pour mettre à jour le driver CUDA")

## 9. Reproductibilité

Un autre binôme peut-il reproduire ce blocage en suivant `docs/installation.md` sans aide orale ?

- [ ] Oui
- [ ] Non — précisez ce qui manque : ___

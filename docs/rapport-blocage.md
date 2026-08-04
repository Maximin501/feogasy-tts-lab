# Rapport de blocage — VoxCPM2

**Rempli par :** Mahefa
**Date :** 04/08/2026
**Statut :** bloqué pour une cause identifiée (installation locale) — contournement en cours

Ce gabarit sert à documenter précisément un blocage lors de l'installation ou de l'inférence VoxCPM2, conformément au critère de passage de la semaine 1.

## 1. Résumé du blocage

**Étape concernée :** installation (environnement, avant même le `pip install voxcpm`)

**Description en une phrase :**
La machine de développement locale (Kali Linux) ne dispose d'aucun GPU NVIDIA et a un Python système (3.13.14) incompatible avec les prérequis VoxCPM2 (< 3.13) ; la tentative de compilation d'un Python 3.11 via pyenv a échoué à cause d'une incompatibilité entre GCC et l'assembleur de Kali Rolling.

## 2. Environnement

| Élément | Valeur |
|---|---|
| OS | Kali GNU/Linux Rolling 2024.1 |
| Python (système) | 3.13.14 |
| pip | 26.0.1 |
| CUDA (driver) | Non applicable — pas de GPU NVIDIA détecté |
| CUDA (toolkit) | Non applicable |
| GPU | Aucun (lspci ne retourne aucune carte NVIDIA) |
| VRAM disponible | Non applicable |
| Version voxcpm | Non installée à ce stade |

## 3. Commande exacte exécutée
pyenv install 3.11.9
## 4. Message d'erreur complet
gcc -c -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall -std=c11 -Wextra -Wno-unused-parameter -Wno-missing-field-initializers -Wstrict-prototypes -Werror=implicit-function-declaration -fvisibility=hidden -I./Include/internal -I. -I./Include -I/home/maximin/.pyenv/versions/3.11.9/include -I/home/maximin/.pyenv/versions/3.11.9/include -fPIC -DPy_BUILD_CORE -o Objects/bytearrayobject.o Objects/bytearrayobject.c
/tmp/cczfj76H.s: Messages de l'assembleur:
/tmp/cczfj76H.s:9105: Erreur: pseudo-op inconnu: « .base64 »
make: *** [Makefile:2521: Objects/bytearrayobject.o] Error 1
/tmp/ccbGhAHR.s: Messages de l'assembleur:
/tmp/ccbGhAHR.s:22036: Erreur: pseudo-op inconnu: « .base64 »
make: *** [Makefile:2521: Objects/codeobject.o] Error 1
pyenv: version `3.11.9' not installed
## 5. Ce qui a déjà été tenté

- [x] Vérification de la version CUDA/PyTorch compatible avec les prérequis.
- [x] Vérification de la présence d'un GPU NVIDIA (`lspci | grep -i nvidia` — aucun résultat).
- [x] Tentative d'installation d'un Python compatible via pyenv (compilation depuis les sources) — échec.
- [ ] Réinstallation dans un environnement virtuel propre — en cours via apt (python3.11 précompilé).
- [ ] Recherche du message d'erreur dans la FAQ officielle ou les issues GitHub.

## 6. Hypothèse de cause probable

1. Absence de GPU NVIDIA sur la machine de développement locale — attendu, le GPU réel (RTX 4090) est sur le serveur distant mentionné dans le dossier projet.
2. La compilation Python depuis les sources échoue car la version de GCC/binutils de Kali Rolling (rolling release, très à jour) génère du code assembleur non reconnu par l'assembleur système — incompatibilité d'outillage, non liée à VoxCPM2 lui-même.

## 7. Impact sur le planning

- [ ] Bloque uniquement l'inférence de test (baseline reportée).
- [x] N'empêche pas l'exploration du code et de la documentation en local (Option B : Python 3.11 via apt, CPU uniquement).
- [x] Nécessite un accès au serveur GPU distant (RTX 4090) pour toute inférence réelle et validation VRAM/CUDA — accès à demander au responsable technique.

## 8. Action demandée / next step

Demander l'accès SSH au serveur GPU (RTX 4090) mentionné dans le dossier projet, pour exécuter les vérifications d'environnement réelles (nvidia-smi, CUDA) et l'installation définitive de VoxCPM2. En attendant, poursuite de l'exploration du dépôt/documentation en local via Python 3.11 installé par apt (sans compilation).

## 9. Reproductibilité

Un autre binôme peut-il reproduire ce blocage en suivant `docs/installation.md` sans aide orale ?

- [x] Oui — le blocage est reproductible sur toute machine Kali Rolling sans GPU NVIDIA tentant une compilation Python via pyenv.

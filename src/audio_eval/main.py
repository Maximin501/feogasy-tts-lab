#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import grille

# ----------------------------------------------------------------------------
# Emplacements par défaut, calculés par rapport à l'emplacement de CE fichier
# (donc valables quel que soit le dossier depuis lequel la commande est lancée).
#
# Arborescence attendue (feogasy-tts-lab/) :
#   feogasy-tts-lab/
#     src/
#       audio_eval/            <- main.py, grille.py, audio_io.py (ce dossier)
#     eval/
#       reference_samples/     <- fichiers .wav + manifest.json (optionnel)
#       reports/                <- CSV de résultats généré ici
# ----------------------------------------------------------------------------

DOSSIER_SCRIPT = Path(__file__).resolve().parent       # .../src/audio_eval
RACINE_PROJET = DOSSIER_SCRIPT.parent.parent            # .../feogasy-tts-lab
EVAL_ROOT = RACINE_PROJET / "eval"                       # .../feogasy-tts-lab/eval

DEFAULT_SAMPLES_DIR = EVAL_ROOT / "reference_samples"
DEFAULT_OUTPUT_CSV = EVAL_ROOT / "reports" / "resultats_eval.csv"
DEFAULT_CHECKPOINT_NOM = "voxcpm2_baseline"



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Semi-automatisation de la grille d'écoute VoxCPM2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--checkpoint", action="append", default=None, type=grille.parser_checkpoint_arg,
        metavar="NOM:DOSSIER",
        help="Un checkpoint à évaluer, format 'nom:dossier_contenant_les_wav'. "
             "Répétable pour comparer plusieurs checkpoints. "
             f"Si omis, utilise par défaut '{DEFAULT_CHECKPOINT_NOM}:{DEFAULT_SAMPLES_DIR}' "
             "s'il existe.",
    )
    parser.add_argument(
        "--evaluateur", default=None,
        help="Nom de l'évaluateur·rice. Si omis, demandé de façon interactive au démarrage "
             "(utile en lançant le script directement, ex. bouton Run de PyCharm).",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Chemin du CSV de sortie (créé s'il n'existe pas, complété sinon). "
             f"Par défaut : {DEFAULT_OUTPUT_CSV}",
    )
    parser.add_argument(
        "--manifest", type=Path, default=None,
        help="CSV ou JSON optionnel (colonnes/clés fichier/file/filename/audio, "
             "categorie/category, texte/text/transcription) pour préremplir la "
             "catégorie et afficher la transcription de référence. "
             "Si omis, un fichier 'manifest.json' ou 'manifest.csv' présent dans "
             "le(s) dossier(s) --checkpoint est utilisé automatiquement s'il existe.",
    )
    parser.add_argument(
        "--no-manifest", action="store_true",
        help="Désactive l'auto-détection du manifest.json par défaut.",
    )
    parser.add_argument(
        "--blind", action="store_true",
        help="Active l'écoute en aveugle : masque le nom réel du checkpoint à "
             "l'écran (utile uniquement si plusieurs --checkpoint sont fournis) "
             "et mélange l'ordre de passage des échantillons.",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Graine aléatoire pour rendre le mélange (mode aveugle) reproductible.",
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # --- Résolution de l'évaluateur·rice : argument CLI sinon saisie interactive ---
    # (permet de lancer le script directement, ex. bouton Run de PyCharm, sans
    # avoir à configurer de paramètres de ligne de commande)
    if not args.evaluateur:
        while not args.evaluateur:
            args.evaluateur = input("Nom de l'évaluateur·rice : ").strip()
            if not args.evaluateur:
                print("  -> Ce champ ne peut pas être vide.")

    # --- Résolution du/des dossier(s) de checkpoint(s) ---
    if args.checkpoint is None:
        if DEFAULT_SAMPLES_DIR.is_dir():
            args.checkpoint = [(DEFAULT_CHECKPOINT_NOM, DEFAULT_SAMPLES_DIR)]
            print(f"[info] --checkpoint non fourni, utilisation par défaut : "
                  f"{DEFAULT_CHECKPOINT_NOM}:{DEFAULT_SAMPLES_DIR}")
        else:
            print(f"[info] Dossier par défaut introuvable : {DEFAULT_SAMPLES_DIR}")
            while args.checkpoint is None:
                reponse = input(
                    "Chemin du dossier contenant les fichiers .wav à évaluer : "
                ).strip()
                chemin = Path(reponse).expanduser()
                if chemin.is_dir():
                    args.checkpoint = [(DEFAULT_CHECKPOINT_NOM, chemin)]
                else:
                    print(f"  -> Dossier introuvable : {chemin}")

    if args.blind and len(args.checkpoint) < 2:
        print("[avertissement] --blind n'a d'effet que si au moins 2 --checkpoint sont fournis.")

    # --- Résolution du fichier de sortie ---
    if args.output is None:
        args.output = DEFAULT_OUTPUT_CSV
        args.output.parent.mkdir(parents=True, exist_ok=True)
        print(f"[info] --output non fourni, utilisation par défaut : {args.output}")

    # --- Résolution du manifeste (CSV ou JSON) ---
    # Recherche dans le(s) dossier(s) de checkpoint réellement résolus (défaut
    # OU saisi interactivement OU passé via --checkpoint), pas uniquement dans
    # DEFAULT_SAMPLES_DIR : sinon, dès que l'utilisateur pointe vers un autre
    # dossier que celui par défaut, le manifest.json qu'il contient n'est
    # jamais détecté et manifest reste vide silencieusement.
    if args.manifest is None and not args.no_manifest:
        for _, dossier in args.checkpoint:
            for nom_candidat in ("manifest.json", "manifest.csv"):
                candidat = dossier / nom_candidat
                if candidat.is_file():
                    args.manifest = candidat
                    print(f"[info] Manifeste détecté automatiquement : {args.manifest}")
                    break
            if args.manifest is not None:
                break

    manifest = grille.charger_manifest(args.manifest) if args.manifest else {}
    if args.manifest and not manifest:
        print(
            f"[avertissement] Le manifeste '{args.manifest}' a été chargé mais ne "
            f"contient aucune entrée exploitable — vérifiez son format."
        )

    echantillons = grille.construire_echantillons(args.checkpoint, manifest, args.blind)
    if not echantillons:
        print("Aucun fichier .wav trouvé dans le(s) dossier(s) indiqué(s). Arrêt.")
        sys.exit(1)

    grille.initialiser_csv(args.output)
    deja_evalues = grille.charger_dejas_evalues(args.output)

    a_faire = [
        ech for ech in echantillons
        if (str(ech.fichier), ech.checkpoint_reel, args.evaluateur) not in deja_evalues
    ]
    total_global = len(echantillons)
    deja_count = total_global - len(a_faire)

    print(f"Session d'écoute — {total_global} échantillon(s) au total.")
    if deja_count:
        print(f"{deja_count} échantillon(s) déjà évalué(s) dans '{args.output}', ils seront sautés.")
    if not a_faire:
        print("Tous les échantillons ont déjà été évalués. Rien à faire.")
        return

    ordre = deja_count
    try:
        for ech in a_faire:
            ordre += 1
            ligne = grille.evaluer_echantillon(
                ech, ordre=ordre, total=total_global,
                evaluateur=args.evaluateur, blind=args.blind,
            )
            grille.enregistrer_ligne(args.output, ligne)
            print(f"  [enregistré dans {args.output}]")
    except KeyboardInterrupt:
        print(
            "\n\nSession interrompue par l'utilisateur. "
            "Les échantillons déjà notés sont sauvegardés.\n"
            f"Relancez la même commande pour reprendre là où vous vous êtes arrêté·e."
        )
        sys.exit(0)

    print(f"\nSession terminée. Résultats complets dans : {args.output}")


if __name__ == "__main__":
    main()
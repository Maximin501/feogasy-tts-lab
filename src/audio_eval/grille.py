#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import audio_io

# ----------------------------------------------------------------------------
# Constantes de la grille
# ----------------------------------------------------------------------------

CATEGORIES_VALIDES = [
    "Malgache", "Français", "Mixte (code-switching)", "Nombres", "Noms propres",
]

CSV_FIELDNAMES = [
    "Ordre", "Fichier", "Echantillon_ID", "Categorie",
    "Checkpoint_reel", "Evaluateur", "Date_heure", "Ecoute_aveugle",
    "Duree_s", "Frequence_Hz", "Canaux", "Alerte_technique",
    "Intelligibilite", "Naturalite", "Fidelite", "Similarite",
    "Repetition", "Repetition_position", "Repetition_commentaire",
    "Omission", "Omission_position", "Omission_commentaire",
    "FinCoupee", "FinCoupee_position", "FinCoupee_commentaire",
    "Hallucination", "Hallucination_position", "Hallucination_commentaire",
    "Commentaire_libre",
]


# ----------------------------------------------------------------------------
# Structure de données
# ----------------------------------------------------------------------------

@dataclass
class Echantillon:
    fichier: Path
    checkpoint_reel: str
    checkpoint_affiche: str  # nom réel ou code anonymisé si mode aveugle
    echantillon_id: str
    categorie: str = ""
    texte_reference: str = ""
    reference_audio: Optional[Path] = None  # voix de référence pour la similarité (optionnel)


# ----------------------------------------------------------------------------
# Saisie utilisateur avec validation stricte
# ----------------------------------------------------------------------------

def demander_note(question: str, wav_paths) -> int:
    """Demande une note 1-5. Tape 'r' pour ré-écouter avant de répondre.

    wav_paths peut être un seul chemin (cas courant : ré-écoute du TTS) ou une
    liste de chemins joués dans l'ordre (ex. [référence, TTS] pour la
    comparaison de similarité).
    """
    if isinstance(wav_paths, (str, Path)):
        wav_paths = [wav_paths]
    while True:
        reponse = input(f"  {question} [1-5, ou 'r' pour réécouter] : ").strip().lower()
        if reponse == "r":
            for p in wav_paths:
                audio_io.lire_audio(p)
            continue
        if reponse.isdigit() and 1 <= int(reponse) <= 5:
            return int(reponse)
        print("    -> Valeur invalide. Entrez un entier entre 1 et 5 (ou 'r' pour réécouter).")


def demander_oui_non(question: str) -> str:
    while True:
        reponse = input(f"  {question} [o/n] : ").strip().lower()
        if reponse in ("o", "oui", "y", "yes"):
            return "Oui"
        if reponse in ("n", "non", "no"):
            return "Non"
        print("    -> Réponse invalide. Tapez 'o' (oui) ou 'n' (non).")


def demander_texte(question: str, optionnel: bool = True) -> str:
    reponse = input(f"  {question}{' (Entrée pour passer)' if optionnel else ''} : ").strip()
    return reponse


def demander_categorie() -> str:
    print("  Catégories disponibles :")
    for i, c in enumerate(CATEGORIES_VALIDES, start=1):
        print(f"    {i}. {c}")
    while True:
        reponse = input(f"  Choisissez une catégorie [1-{len(CATEGORIES_VALIDES)}] : ").strip()
        if reponse.isdigit() and 1 <= int(reponse) <= len(CATEGORIES_VALIDES):
            return CATEGORIES_VALIDES[int(reponse) - 1]
        print("    -> Choix invalide.")


def resoudre_categorie(categorie_manifeste: str) -> str:
    """Valide la catégorie issue du manifeste (alias/coquille -> re-saisie interactive).

    Retourne la catégorie du manifeste si elle est reconnue, sinon avertit et
    demande une saisie interactive parmi CATEGORIES_VALIDES.
    """
    if not categorie_manifeste:
        return demander_categorie()
    if categorie_manifeste in CATEGORIES_VALIDES:
        print(f"Catégorie (manifeste) : {categorie_manifeste}")
        return categorie_manifeste
    print(f"[avertissement] Catégorie manifeste inconnue : '{categorie_manifeste}'")
    return demander_categorie()


# ----------------------------------------------------------------------------
# Constitution de la liste des échantillons à évaluer
# ----------------------------------------------------------------------------

def parser_checkpoint_arg(valeur: str) -> tuple[str, Path]:
    """Parse un argument --checkpoint 'nom:chemin' (utilisé par argparse dans main.py)."""
    if ":" not in valeur:
        raise argparse.ArgumentTypeError(
            f"Format attendu 'nom_checkpoint:chemin_dossier', reçu : '{valeur}'"
        )
    nom, chemin = valeur.split(":", 1)
    nom = nom.strip()
    chemin_path = Path(chemin.strip()).expanduser()
    if not chemin_path.is_dir():
        raise argparse.ArgumentTypeError(f"Dossier introuvable : {chemin_path}")
    return nom, chemin_path


def _cle_flexible(d: dict, *noms: str) -> str:
    """Récupère la première clé existante parmi plusieurs alias possibles (insensible à la casse)."""
    d_lower = {str(k).lower(): v for k, v in d.items()}
    for nom in noms:
        if nom.lower() in d_lower:
            valeur = d_lower[nom.lower()]
            return str(valeur).strip() if valeur is not None else ""
    return ""


def charger_manifest(manifest_path: Path) -> dict:
    """Charge un manifeste optionnel (CSV ou JSON) -> dict indexé par nom de fichier.

    Formats supportés :
      - CSV avec colonnes fichier,categorie,texte,reference_audio (alias acceptés :
        file/filename/audio, category, texte/text/transcription,
        audio_reference/ref_audio/reference) ;
      - JSON sous forme de liste d'objets :
          [{"fichier": "001.wav", "categorie": "Français", "texte": "...",
            "reference_audio": "voix_ref/001.wav"}, ...]
      - JSON sous forme de dictionnaire indexé par nom de fichier :
          {"001.wav": {"categorie": "Français", "texte": "...",
                       "reference_audio": "voix_ref/001.wav"}, ...}

    Le champ reference_audio est optionnel : s'il est absent ou vide, ou si le
    fichier qu'il désigne est introuvable au moment de l'évaluation, la note de
    similarité est simplement laissée vide (pas d'écoute comparative).
    """
    manifest: dict = {}
    suffixe = manifest_path.suffix.lower()

    if suffixe == ".json":
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            entrees = data
            ignorees = 0
            for entree in entrees:
                if not isinstance(entree, dict):
                    ignorees += 1
                    continue
                cle = _cle_flexible(entree, "fichier", "file", "filename", "audio")
                if not cle:
                    ignorees += 1
                    continue
                manifest[cle] = {
                    "categorie": _cle_flexible(entree, "categorie", "category"),
                    "texte": _cle_flexible(entree, "texte", "text", "transcription"),
                    "reference_audio": _cle_flexible(
                        entree, "reference_audio", "audio_reference", "ref_audio", "reference"
                    ),
                }
            if ignorees:
                print(
                    f"[avertissement] {ignorees} entrée(s) du manifeste JSON ignorée(s) "
                    f"(clé de nom de fichier non reconnue parmi fichier/file/filename/audio)."
                )
        elif isinstance(data, dict):
            for cle, valeur in data.items():
                cle = str(cle).strip()
                if not cle or not isinstance(valeur, dict):
                    continue
                manifest[cle] = {
                    "categorie": _cle_flexible(valeur, "categorie", "category"),
                    "texte": _cle_flexible(valeur, "texte", "text", "transcription"),
                    "reference_audio": _cle_flexible(
                        valeur, "reference_audio", "audio_reference", "ref_audio", "reference"
                    ),
                }
        else:
            raise ValueError(
                f"Format JSON de manifeste non reconnu dans {manifest_path} "
                f"(attendu : liste d'objets ou dictionnaire indexé par fichier)."
            )
    else:
        with open(manifest_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ignorees = 0
            for row in reader:
                cle = _cle_flexible(row, "fichier", "file", "filename", "audio")
                if not cle:
                    ignorees += 1
                    continue
                manifest[cle] = {
                    "categorie": _cle_flexible(row, "categorie", "category"),
                    "texte": _cle_flexible(row, "texte", "text", "transcription"),
                    "reference_audio": _cle_flexible(
                        row, "reference_audio", "audio_reference", "ref_audio", "reference"
                    ),
                }
            if ignorees:
                print(
                    f"[avertissement] {ignorees} ligne(s) du manifeste CSV ignorée(s) "
                    f"(colonne de nom de fichier non reconnue parmi fichier/file/filename/audio)."
                )

    return manifest


def construire_echantillons(
    checkpoints: list[tuple[str, Path]],
    manifest: dict,
    blind: bool,
) -> list[Echantillon]:
    echantillons: list[Echantillon] = []

    # Mode aveugle : on attribue un code anonyme (stable) à chaque checkpoint
    noms_reels = [nom for nom, _ in checkpoints]
    if blind and len(checkpoints) > 1:
        codes = [f"Modèle_{i+1}" for i in range(len(checkpoints))]
        ordre_codes = codes[:]
        random.shuffle(ordre_codes)
        mapping_affichage = dict(zip(noms_reels, ordre_codes))
    else:
        mapping_affichage = {nom: nom for nom in noms_reels}

    for nom_reel, dossier in checkpoints:
        for wav_path in sorted(dossier.glob("*.wav")):
            info_manifest = manifest.get(wav_path.name, {})

            ref_audio_str = info_manifest.get("reference_audio", "")
            reference_audio = None
            if ref_audio_str:
                p = Path(ref_audio_str).expanduser()
                if not p.is_absolute():
                    p = dossier / p
                reference_audio = p  # existence vérifiée à l'évaluation (fichier optionnel)

            echantillons.append(
                Echantillon(
                    fichier=wav_path,
                    checkpoint_reel=nom_reel,
                    checkpoint_affiche=mapping_affichage[nom_reel],
                    echantillon_id=wav_path.stem,
                    categorie=info_manifest.get("categorie", ""),
                    texte_reference=info_manifest.get("texte", ""),
                    reference_audio=reference_audio,
                )
            )

    if blind:
        random.shuffle(echantillons)  # ordre mélangé pour limiter les biais d'attente

    return echantillons


# ----------------------------------------------------------------------------
# Sauvegarde incrémentale + reprise de session
# ----------------------------------------------------------------------------

def charger_dejas_evalues(csv_path: Path) -> set:
    """Retourne l'ensemble des (fichier, checkpoint_reel, evaluateur) déjà présents
    dans le CSV de sortie.

    L'évaluateur fait partie de la clé : sans ça, un·e second·e évaluateur·rice
    utilisant le même fichier --output se voit sauter des échantillons déjà
    notés par quelqu'un d'autre, ce qui rend impossible tout calcul d'accord
    inter-évaluateurs (cf. notes d'usage de la grille v1).
    """
    deja = set()
    if not csv_path.exists():
        return deja
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            deja.add((
                row.get("Fichier", ""),
                row.get("Checkpoint_reel", ""),
                row.get("Evaluateur", ""),
            ))
    return deja


def initialiser_csv(csv_path: Path) -> None:
    nouveau = not csv_path.exists()
    if nouveau:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()


def enregistrer_ligne(csv_path: Path, ligne: dict) -> None:
    """Ajoute une ligne au CSV et force l'écriture sur disque immédiatement."""
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writerow(ligne)
        f.flush()
        os.fsync(f.fileno())


# ----------------------------------------------------------------------------
# Évaluation d'un échantillon (orchestration Partie A + Partie B)
# ----------------------------------------------------------------------------

def evaluer_echantillon(
    ech: Echantillon,
    ordre: int,
    total: int,
    evaluateur: str,
    blind: bool,
) -> dict:
    print("\n" + "=" * 70)
    print(f"Échantillon {ordre}/{total} — ID : {ech.echantillon_id}")
    print(f"Checkpoint : {ech.checkpoint_affiche}" + ("  (masqué)" if blind else ""))

    ct = audio_io.controle_technique(ech.fichier)
    print(
        f"[Contrôle technique auto] durée={ct.duree_s}s | "
        f"fréq={ct.frequence_hz}Hz | canaux={ct.canaux} | {ct.resume_alertes()}"
    )
    if ct.alertes:
        print("  -> Anomalie(s) détectée(s) automatiquement, à confirmer à l'écoute.")

    print("\n▶ Lecture de l'audio TTS...")
    audio_io.lire_audio(ech.fichier)

    # La catégorie est demandée après écoute : l'évaluateur·rice peut ainsi
    # se fier à ce qu'iel a réellement entendu (utile en cas de code-switching
    # ambigu ou d'erreur de manifeste), plutôt que de se faire une idée avant
    # même d'écouter l'échantillon.
    categorie = resoudre_categorie(ech.categorie)

    print("\n-- Partie A : notes qualitatives (1 = très faible, 5 = excellent) --")

    # Intelligibilité et Naturalité sont jugées avant l'affichage du texte,
    # pour éviter que la lecture du texte source n'influence la perception
    # de la clarté ou du naturel de l'audio (biais d'ancrage).
    intelligibilite = demander_note("Intelligibilité", ech.fichier)
    naturalite = demander_note("Naturalité", ech.fichier)

    # Le texte n'est affiché qu'à partir d'ici, juste avant la Fidélité,
    # qui est justement la seule note qui a besoin du texte pour être jugée.
    if ech.texte_reference:
        print(f"\nTexte source de référence : « {ech.texte_reference} »")
    fidelite = demander_note("Fidélité (correspondance au texte source)", ech.fichier)

    # Similarité : uniquement si une voix de référence est renseignée dans le
    # manifeste ET que le fichier correspondant existe réellement sur le
    # disque. Sinon la note reste vide (pas de note "à l'aveugle" sans point
    # de comparaison).
    if ech.reference_audio and ech.reference_audio.is_file():
        print("\nÉcoute comparative pour la similarité de voix :")
        print("  ▶ Voix de référence...")
        audio_io.lire_audio(ech.reference_audio)
        print("  ▶ Audio TTS...")
        audio_io.lire_audio(ech.fichier)
        similarite = demander_note(
            "Similarité (ressemblance à la voix de référence)",
            [ech.reference_audio, ech.fichier],
        )
    else:
        if ech.reference_audio:
            print(
                f"[avertissement] Voix de référence introuvable "
                f"({ech.reference_audio}) — Similarité non notée."
            )
        else:
            print("Aucune voix de référence disponible pour cet échantillon — Similarité non notée.")
        similarite = ""

    print("\n-- Partie B : détection de défauts --")
    defauts = {}
    for question, cle in [
        ("Répétition détectée ?", "Repetition"),
        ("Omission détectée ?", "Omission"),
        ("Fin coupée détectée ?", "FinCoupee"),
        ("Mot(s) halluciné(s) détecté(s) ?", "Hallucination"),
    ]:
        present = demander_oui_non(question)
        position = ""
        commentaire = ""
        if present == "Oui":
            position = demander_texte("  Position / horodatage (ex. 00:04)")
            commentaire = demander_texte("  Commentaire bref")
        defauts[cle] = present
        defauts[f"{cle}_position"] = position
        defauts[f"{cle}_commentaire"] = commentaire

    commentaire_libre = demander_texte("\nCommentaire libre sur l'échantillon")

    return {
        "Ordre": ordre,
        "Fichier": str(ech.fichier),
        "Echantillon_ID": ech.echantillon_id,
        "Categorie": categorie,
        "Checkpoint_reel": ech.checkpoint_reel,
        "Evaluateur": evaluateur,
        "Date_heure": dt.datetime.now().isoformat(timespec="seconds"),
        "Ecoute_aveugle": "Oui" if blind else "Non",
        "Duree_s": ct.duree_s,
        "Frequence_Hz": ct.frequence_hz,
        "Canaux": ct.canaux,
        "Alerte_technique": ct.resume_alertes(),
        "Intelligibilite": intelligibilite,
        "Naturalite": naturalite,
        "Fidelite": fidelite,
        "Similarite": similarite,
        "Repetition": defauts["Repetition"],
        "Repetition_position": defauts["Repetition_position"],
        "Repetition_commentaire": defauts["Repetition_commentaire"],
        "Omission": defauts["Omission"],
        "Omission_position": defauts["Omission_position"],
        "Omission_commentaire": defauts["Omission_commentaire"],
        "FinCoupee": defauts["FinCoupee"],
        "FinCoupee_position": defauts["FinCoupee_position"],
        "FinCoupee_commentaire": defauts["FinCoupee_commentaire"],
        "Hallucination": defauts["Hallucination"],
        "Hallucination_position": defauts["Hallucination_position"],
        "Hallucination_commentaire": defauts["Hallucination_commentaire"],
        "Commentaire_libre": commentaire_libre,
    }
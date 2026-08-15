#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import shutil
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ----------------------------------------------------------------------------
# Constantes issues de Exigences_jeu_de_donnees_VoxCPM2.md
# ----------------------------------------------------------------------------

FREQ_ATTENDUE_HZ = 16000
DUREE_MIN_RECOMMANDEE_S = 3.0
DUREE_MAX_RECOMMANDEE_S = 30.0
DUREE_ABS_MIN_S = 1.0  # en dessous : "déconseillé, résultats instables"


@dataclass
class ControleTechnique:
    duree_s: Optional[float] = None
    frequence_hz: Optional[int] = None
    canaux: Optional[int] = None
    alertes: list = field(default_factory=list)

    def resume_alertes(self) -> str:
        return " | ".join(self.alertes) if self.alertes else "OK"


# ----------------------------------------------------------------------------
# Vérifications techniques automatiques
# ----------------------------------------------------------------------------

def controle_technique(wav_path: Path) -> ControleTechnique:
    """Analyse automatique du fichier .wav selon Exigences_jeu_de_donnees_VoxCPM2.md.

    Vérifie : fréquence d'échantillonnage, durée, silence total, et (si numpy est
    disponible) le niveau de crête et le silence en bord de clip.
    """
    ct = ControleTechnique()
    try:
        with wave.open(str(wav_path), "rb") as wf:
            n_frames = wf.getnframes()
            framerate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            duree = n_frames / float(framerate) if framerate else 0.0

            ct.duree_s = round(duree, 3)
            ct.frequence_hz = framerate
            ct.canaux = channels

            if framerate != FREQ_ATTENDUE_HZ:
                ct.alertes.append(
                    f"Fréquence {framerate} Hz != {FREQ_ATTENDUE_HZ} Hz attendu "
                    f"(rééchantillonnage auto par le dataloader, non bloquant)"
                )
            if channels != 1:
                ct.alertes.append(f"{channels} canaux détectés (mono attendu)")
            if duree < DUREE_ABS_MIN_S:
                ct.alertes.append(f"Clip très court ({duree:.2f}s < {DUREE_ABS_MIN_S}s) — déconseillé")
            elif duree < DUREE_MIN_RECOMMANDEE_S:
                ct.alertes.append(f"Durée {duree:.2f}s hors plage optimale [3-30s]")
            elif duree > DUREE_MAX_RECOMMANDEE_S:
                ct.alertes.append(f"Clip long ({duree:.2f}s > {DUREE_MAX_RECOMMANDEE_S}s) — déconseillé")

            # Contrôles de niveau / silence : nécessitent numpy et PCM 16-bit.
            try:
                import numpy as np  # import local, optionnel
                if sampwidth == 2:
                    raw = wf.readframes(n_frames)
                    data = np.frombuffer(raw, dtype=np.int16)
                    if channels > 1:
                        data = data.reshape(-1, channels).mean(axis=1)
                    if data.size == 0:
                        ct.alertes.append("Fichier vide (0 échantillon)")
                    else:
                        peak = float(np.max(np.abs(data))) / 32768.0
                        rms = float(np.sqrt(np.mean(data.astype(np.float64) ** 2))) / 32768.0
                        if peak < 1e-6:
                            ct.alertes.append("Silence total détecté — à écarter du corpus")
                        else:
                            if peak >= 0.995:
                                ct.alertes.append("Niveau de pic proche de 0 dBFS — clipping possible")
                            if rms < 0.003:
                                ct.alertes.append("Niveau RMS très faible — signal potentiellement noyé dans le bruit")

                            # Silence en bord de clip (seuil simple à 2% du pic, fenêtre 50ms)
                            seuil = max(peak * 0.02, 1e-4)
                            fenetre = max(int(framerate * 0.05), 1)
                            debut = data[:fenetre]
                            fin = data[-fenetre:]
                            if np.max(np.abs(debut)) < seuil * 32768.0:
                                ct.alertes.append("Silence important en début de clip")
                            if np.max(np.abs(fin)) < seuil * 32768.0:
                                ct.alertes.append("Silence important en fin de clip")
            except ImportError:
                pass  # numpy non installé : on garde uniquement les contrôles de base

    except (wave.Error, EOFError, FileNotFoundError) as e:
        ct.alertes.append(f"Fichier illisible ou non conforme WAV/PCM : {e}")

    return ct


# ----------------------------------------------------------------------------
# Lecture audio bloquante
# ----------------------------------------------------------------------------

def lire_audio(wav_path: Path) -> None:
    """Joue le fichier et bloque jusqu'à la fin de la lecture."""
    # 1) Tentative avec simpleaudio (pur Python, multiplateforme, bloquant propre)
    try:
        import simpleaudio as sa
        wave_obj = sa.WaveObject.from_wave_file(str(wav_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()
        return
    except ImportError:
        pass
    except Exception as e:
        print(f"  [avertissement] échec lecture via simpleaudio ({e}), repli sur le lecteur système...")

    # 2) Repli sur le lecteur système, appelé de façon bloquante
    system = sys.platform
    cmd = None
    if system == "darwin" and shutil.which("afplay"):
        cmd = ["afplay", str(wav_path)]
    elif system.startswith("linux"):
        if shutil.which("paplay"):
            cmd = ["paplay", str(wav_path)]
        elif shutil.which("aplay"):
            cmd = ["aplay", "-q", str(wav_path)]
    elif system == "win32":
        cmd = [
            "powershell", "-c",
            f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync();",
        ]

    if cmd is None:
        print("  [ERREUR] Aucun lecteur audio disponible sur ce système.")
        print("  Installez 'simpleaudio' (pip install simpleaudio) ou écoutez le fichier manuellement :")
        print(f"    {wav_path}")
        input("  Appuyez sur Entrée une fois l'écoute manuelle terminée pour continuer...")
        return

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  [ERREUR] Échec de la lecture automatique ({e}).")
        print(f"  Écoutez le fichier manuellement : {wav_path}")
        input("  Appuyez sur Entrée une fois l'écoute manuelle terminée pour continuer...")
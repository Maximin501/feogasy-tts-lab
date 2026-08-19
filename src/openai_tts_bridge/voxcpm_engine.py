"""
Wrapper autour de VoxCPM2 - charge le modele une seule fois (singleton) et
expose une methode de generation simple, decouplee du format OpenAI.
"""

import io
import logging
import os
import threading

import numpy as np
import soundfile as sf

logger = logging.getLogger("openai_tts_bridge.engine")

_MODEL_ID = os.environ.get("VOXCPM_MODEL_ID", "openbmb/VoxCPM2")
_CFG_VALUE = float(os.environ.get("VOXCPM_CFG_VALUE", "2.0"))
_INFERENCE_TIMESTEPS = int(os.environ.get("VOXCPM_INFERENCE_TIMESTEPS", "10"))


class VoxCPMEngine:
    """Charge VoxCPM2 une seule fois et sert les generations suivantes."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._model = None
        self._model_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "VoxCPMEngine":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self):
        if self._model is not None:
            return
        with self._model_lock:
            if self._model is not None:
                return
            logger.info("Chargement de VoxCPM2 (%s)...", _MODEL_ID)
            from voxcpm import VoxCPM

            self._model = VoxCPM.from_pretrained(_MODEL_ID, load_denoiser=False)
            logger.info("VoxCPM2 charge avec succes.")

    def is_loaded(self) -> bool:
        return self._model is not None

    def generate_wav_bytes(self, text: str, style: str | None = None) -> bytes:
        """
        Genere l'audio pour le texte donne et retourne des octets WAV.

        Le style (Voice Design) est prefixe entre parentheses, convention
        VoxCPM2. Pas de parametre 'seed' - absent de l'API reelle installee
        (cf. docs/installation.md du depot feogasy-tts-lab).
        """
        self._ensure_loaded()

        full_text = f"({style}) {text}" if style else text

        wav = self._model.generate(
            text=full_text,
            cfg_value=_CFG_VALUE,
            inference_timesteps=_INFERENCE_TIMESTEPS,
        )

        sample_rate = self._model.tts_model.sample_rate

        buffer = io.BytesIO()
        sf.write(buffer, wav, sample_rate, format="WAV")
        buffer.seek(0)
        return buffer.read()


class MockEngine(VoxCPMEngine):
    """
    Moteur factice pour tester le contrat HTTP sans charger VoxCPM2.
    Genere un simple bip sinusoidal de duree proportionnelle au texte.
    Active via la variable d'environnement MOCK_ENGINE=1.
    """

    def is_loaded(self) -> bool:
        return True

    def generate_wav_bytes(self, text: str, style: str | None = None) -> bytes:
        duration_s = max(0.5, min(len(text) * 0.05, 5.0))
        sample_rate = 24000
        t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
        wav = 0.1 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        buffer = io.BytesIO()
        sf.write(buffer, wav, sample_rate, format="WAV")
        buffer.seek(0)
        return buffer.read()

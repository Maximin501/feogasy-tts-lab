"""
Serveur frontal compatible OpenAI pour VoxCPM2 - Feogasy / integration Haiko.

Expose POST /v1/audio/speech avec le contrat OpenAI attendu par le proxy
existant du depot haiko-io-team-a-ai-rag (gateway/http/routers/audio.py) :
    { "model": "...", "input": "texte", "voice": "alloy" }
-> renvoie un flux audio (WAV)

Lancement :
    uvicorn src.openai_tts_bridge.main:app --host 0.0.0.0 --port 8000

Variables d'environnement :
    VOXCPM_MODEL_ID          (defaut: openbmb/VoxCPM2)
    VOXCPM_CFG_VALUE         (defaut: 2.0)
    VOXCPM_INFERENCE_TIMESTEPS (defaut: 10)
"""

import logging

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from .voice_mapping import list_voices, resolve_style
import os

from .voxcpm_engine import VoxCPMEngine, MockEngine

_USE_MOCK = os.environ.get("MOCK_ENGINE", "0") == "1"
_EngineClass = MockEngine if _USE_MOCK else VoxCPMEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openai_tts_bridge")

app = FastAPI(
    title="Feogasy VoxCPM2 - OpenAI-compatible TTS bridge",
    description="Serveur frontal exposant VoxCPM2 via un contrat compatible OpenAI, pour integration Haiko.",
    version="0.1.0",
)


class SpeechRequest(BaseModel):
    """Contrat OpenAI /v1/audio/speech - champs consommes par le proxy Haiko."""

    model: str = Field(default="tts-1", description="Ignore pour l'instant, VoxCPM2 est le seul moteur.")
    input: str = Field(..., min_length=1, description="Texte a synthetiser.")
    voice: str = Field(default="alloy", description="Voix OpenAI, mappee vers un style VoxCPM2 Voice Design.")
    response_format: str = Field(default="wav", description="Seul 'wav' est supporte pour l'instant.")


@app.get("/health")
def health():
    engine = _EngineClass.get_instance()
    return {
        "status": "ok",
        "model_loaded": engine.is_loaded(),
    }


@app.get("/v1/audio/voices")
def get_voices():
    """Liste des voix exposees - format compatible avec le proxy Haiko existant."""
    return list_voices()


@app.post("/v1/audio/speech")
def synthesize_speech(body: SpeechRequest):
    if body.response_format != "wav":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seul response_format='wav' est supporte actuellement.",
        )

    style = resolve_style(body.voice)
    logger.info("Generation demandee - voice=%s -> style='%s', longueur texte=%d",
                body.voice, style, len(body.input))

    try:
        engine = _EngineClass.get_instance()
        wav_bytes = engine.generate_wav_bytes(text=body.input, style=style)
    except Exception as exc:
        logger.exception("Echec de generation VoxCPM2")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de generation: {exc}",
        ) from exc

    return Response(content=wav_bytes, media_type="audio/wav")


@app.post("/v1/audio/transcriptions")
def transcribe_stub():
    """
    STT hors perimetre de ce composant (equipe TTS uniquement).
    Route presente pour eviter un 404 silencieux cote proxy Haiko.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="STT non implemente dans ce composant - hors perimetre binome TTS.",
    )

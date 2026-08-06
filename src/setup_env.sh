#!/bin/bash
# Script d'installation de l'environnement TTS Feogasy
# Usage: bash src/setup_env.sh [cpu|gpu]

set -e

MODE=${1:-cpu}
VENV_DIR="$HOME/venv-voxcpm"

echo "=== Création de l'environnement virtuel ($VENV_DIR) ==="
if [ ! -d "$VENV_DIR" ]; then
    virtualenv -p python3.11 "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip

if [ "$MODE" == "cpu" ]; then
    echo "=== Installation en mode CPU (dev local, pas de GPU) ==="
    pip install torch torchaudio torchcodec --index-url https://download.pytorch.org/whl/cpu
elif [ "$MODE" == "gpu" ]; then
    echo "=== Installation en mode GPU (serveur RTX 4090) ==="
    pip install torch torchaudio torchcodec
else
    echo "Mode inconnu : $MODE (utiliser 'cpu' ou 'gpu')"
    exit 1
fi

echo "=== Installation de voxcpm et dépendances ==="
pip install voxcpm --no-deps
pip install addict argbind "datasets<4,>=3" einops funasr "gradio<7,>=6" \
    huggingface-hub inflect librosa matplotlib pydantic safetensors \
    simplejson sortedcontainers spaces transformers wetext soundfile modelscope

echo "=== Vérification ==="
python3 -c "import torch, voxcpm; print('PyTorch:', torch.__version__); print('CUDA dispo:', torch.cuda.is_available()); print('voxcpm: OK')"

echo "=== Installation terminée ==="

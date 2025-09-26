import os
from pathlib import Path

# Chemins de base
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
CONFIG_DIR = ROOT_DIR / "config"

# Données
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# Modèles
MODELS_DIR = PROCESSED_DATA_DIR / "models" # SRC_DIR / "models/trained"

TEMP_DIR = Path(os.environ.get("TEMP_DIR", "/tmp/cats_dogs"))

# Configuration du modèle
MODEL_CONFIG = {
    "image_size": (128, 128), # Optimized for speed-up
    "batch_size": 64,
    "epochs": 3, #10, # Optimized for speed-up
    "learning_rate": 0.001,
}

# Configuration API
API_CONFIG = {
    "host": "127.0.0.1",
    "port": 8000,
    "token": os.environ.get("API_TOKEN", "?C@TS&D0GS!"),
    "model_path": MODELS_DIR / "cats_dogs_model.keras",
}

# Configuration Base de Données (PostgreSQL)
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "computer-vision-cats-dogs"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
}

# URLs de données
DATA_URLS = {
    "kaggle_cats_dogs": "https://download.microsoft.com/download/3/E/1/3E1C3F21-ECDB-4869-8368-6DEBA77B919F/kagglecatsanddogs_5340.zip"
}

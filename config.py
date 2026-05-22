from pathlib import Path


# Dossier racine du projet.
# __file__ correspond au fichier config.py.
BASE_DIR = Path(__file__).resolve().parent

# Dossier contenant les fichiers JSON de corpus.
CORPUS_DIR = BASE_DIR / "corpus"

# Dossier dans lequel les vidéos seront enregistrées.
DATA_DIR = BASE_DIR / "data"

# Nombre total de phrases à lire pendant une session.
SENTENCE_NUMBER = 20

# Bitrate audio utilisé pour l'enregistrement AAC.
AUDIO_BITRATE = 128_000

# Bitrates vidéo selon la résolution.
VIDEO_BITRATE_LOW = 8_000_000
VIDEO_BITRATE_MEDIUM = 12_000_000
VIDEO_BITRATE_HIGH = 20_000_000
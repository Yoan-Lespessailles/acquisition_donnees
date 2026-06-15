import json

import shutil

from pathlib import Path


def write_whisper_json(pair_results_dir, whisper_result):
    """
    Écrit le résultat complet retourné par Whisper dans un fichier JSON.
    """

    # Construit le chemin complet du fichier JSON à créer
    whisper_json_path = Path(pair_results_dir) / "whisper_result.json"

    # Écrit le résultat Whisper dans le fichier JSON
    with whisper_json_path.open("w", encoding="utf-8") as json_file:
        json.dump(
            whisper_result,
            json_file,
            ensure_ascii=False,
            indent=4,
        )

def create_pair_results_dir(results_dir, language_code, media_path):
    """
    Crée le dossier de résultats associé à une paire vidéo/métadonnées.

    Exemple :
        results/fr/pairs/fr_20260602_092105/
    """

    # Récupère le nom du fichier vidéo sans extension
    file_stem = Path(media_path).stem

    # Crée le dossier spécifique à cette paire
    pair_results_dir = results_dir / language_code / "pairs" / file_stem

    # Crée le dossier s'il n'existe pas
    pair_results_dir.mkdir(parents=True, exist_ok=True)

    return pair_results_dir


def copy_source_files(pair_results_dir, media_path, metadata_path):
    """
    Copie la vidéo et le fichier metadata dans le dossier de résultats.

    Les fichiers originaux dans data/ ne sont pas modifiés.
    """

    # Convertit les chemins en objets Path.
    pair_results_dir = Path(pair_results_dir)
    media_path = Path(media_path)
    metadata_path = Path(metadata_path)

    # Crée un sous-dossier pour garder les fichiers d'origine.
    source_dir = pair_results_dir / "source_files"
    source_dir.mkdir(parents=True, exist_ok=True)

    # Copie la vidéo dans le dossier de résultats.
    shutil.copy2(
        media_path,
        source_dir / media_path.name,
    )

    # Copie le fichier metadata dans le dossier de résultats.
    shutil.copy2(
        metadata_path,
        source_dir / metadata_path.name,
    )
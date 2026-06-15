import json
import shutil

from pathlib import Path


def write_whisper_json(pair_results_dir, whisper_result):
    """
    Écrit le résultat complet retourné par Whisper dans un fichier JSON.

    Le fichier généré contient notamment :
        - le texte transcrit ;
        - les segments reconnus ;
        - les timestamps ;
        - les informations détaillées retournées par Whisper.

    Paramètres :
        pair_results_dir (Path | str) : dossier de résultats associé à une paire vidéo/métadonnées.
        whisper_result (dict) : résultat complet retourné par Whisper.

    Retourne :
        None
    """

    # Convertit le dossier de résultats en objet Path pour sécuriser la construction du chemin.
    pair_results_dir = Path(pair_results_dir)

    # Construit le chemin complet du fichier JSON à créer.
    whisper_json_path = pair_results_dir / "whisper_result.json"

    # Écrit le résultat Whisper dans le fichier JSON.
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

    Le dossier est construit à partir :
        - du dossier racine des résultats ;
        - du code langue ;
        - du nom du fichier vidéo sans extension.

    Exemple :
        results/fr/pairs/fr_20260602_092105/

    Paramètres :
        results_dir (Path | str) : dossier racine des résultats.
        language_code (str) : code de la langue traitée.
        media_path (Path | str) : chemin du fichier vidéo traité.

    Retourne :
        Path : chemin du dossier de résultats créé pour la paire.
    """

    # Convertit les chemins en objets Path pour sécuriser leur manipulation.
    results_dir = Path(results_dir)
    media_path = Path(media_path)

    # Récupère le nom du fichier vidéo sans extension.
    # Exemple : fr_20260602_092105.mp4 devient fr_20260602_092105.
    file_stem = media_path.stem

    # Crée le chemin du dossier spécifique à cette paire vidéo/métadonnées.
    pair_results_dir = results_dir / language_code / "pairs" / file_stem

    # Crée le dossier s'il n'existe pas déjà.
    pair_results_dir.mkdir(parents=True, exist_ok=True)

    return pair_results_dir


def copy_source_files(pair_results_dir, media_path, metadata_path):
    """
    Copie la vidéo et le fichier metadata dans le dossier de résultats.

    Les fichiers originaux situés dans le dossier data/ ne sont pas modifiés.
    La copie permet de conserver, avec le résultat Whisper, les fichiers sources
    utilisés pour produire ce résultat.

    Paramètres :
        pair_results_dir (Path | str) : dossier de résultats associé à une paire vidéo/métadonnées.
        media_path (Path | str) : chemin du fichier vidéo source.
        metadata_path (Path | str) : chemin du fichier metadata source.

    Retourne :
        None
    """

    # Convertit les chemins en objets Path pour sécuriser leur manipulation.
    pair_results_dir = Path(pair_results_dir)
    media_path = Path(media_path)
    metadata_path = Path(metadata_path)

    # Crée un sous-dossier pour conserver les fichiers d'origine.
    source_dir = pair_results_dir / "source_files"
    source_dir.mkdir(parents=True, exist_ok=True)

    # Copie la vidéo dans le dossier source_files.
    shutil.copy2(
        media_path,
        source_dir / media_path.name,
    )

    # Copie le fichier metadata dans le dossier source_files.
    shutil.copy2(
        metadata_path,
        source_dir / metadata_path.name,
    )
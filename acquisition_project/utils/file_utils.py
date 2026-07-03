from datetime import datetime
from pathlib import Path

def build_recording_filepaths(data_dir: Path, data_dir_rel: Path, language_code: str):
    """
    Construit les chemins de sauvegarde d'un enregistrement.

    Un enregistrement correspond à :
        - une vidéo .mp4 ;
        - un fichier de métadonnées .csv portant le même nom.

    Exemple :
        data/fr/videos/fr_20260522_143012.mp4
        data/fr/metadata/fr_20260522_143012.csv

    Retourne :
        - le nom de base sans extension ;
        - le chemin complet de la vidéo ;
        - le chemin complet des métadonnés.
    """

    # Dossier de la langue
    language_dir = data_dir / language_code
    language_dir_rel = data_dir_rel / language_code

    # Sous-dossier des vidéos
    video_dir = language_dir / "videos"
    video_dir_rel = language_dir_rel / "videos"

    # Sous-dossier des métadonnées
    metadata_dir = language_dir / "metadata"
    metadata_dir_rel = language_dir_rel / "metadata"

    # Crée les dossiers nécessaires
    video_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # Génère un nom de base commun à la vidéo et aux métadonnés
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{language_code}_{timestamp}"

    # Construit les chemins complets
    video_filepath = video_dir / f"{file_name}.mp4"
    metadata_filepath = metadata_dir / f"{file_name}.csv"

    video_filepath_rel = video_dir_rel / f"{file_name}.mp4"
    metadata_filepath_rel = metadata_dir_rel / f"{file_name}.csv"


    return file_name, video_filepath, metadata_filepath, video_filepath_rel, metadata_filepath_rel
from datetime import datetime
from pathlib import Path

def build_recording_filepaths(data_dir: Path, language_code: str):
    """
    Construit les chemins de sauvegarde d'un enregistrement.

    Un enregistrement correspond à :
        - une vidéo .mp4 ;
        - un fichier d'annotation .csv portant le même nom.

    Exemple :
        data/fr/videos/fr_20260522_143012.mp4
        data/fr/annotations/fr_20260522_143012.csv

    Retourne :
        - le nom de base sans extension ;
        - le chemin complet de la vidéo ;
        - le chemin complet de l'annotation.
    """

    # Dossier de la langue.
    language_dir = data_dir / language_code

    # Sous-dossier des vidéos.
    video_dir = language_dir / "videos"

    # Sous-dossier des annotations.
    annotation_dir = language_dir / "annotations"

    # Crée les dossiers nécessaires.
    video_dir.mkdir(parents=True, exist_ok=True)
    annotation_dir.mkdir(parents=True, exist_ok=True)

    # Génère un nom de base commun à la vidéo et à l'annotation.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{language_code}_{timestamp}"

    # Construit les chemins complets.
    video_filepath = video_dir / f"{file_name}.mp4"
    annotation_filepath = annotation_dir / f"{file_name}.csv"

    return file_name, video_filepath, annotation_filepath
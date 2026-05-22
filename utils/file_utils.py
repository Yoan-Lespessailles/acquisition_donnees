from datetime import datetime
from pathlib import Path

def build_video_filepath(data_dir: Path, language_code: str) -> tuple[str, Path]:
    """
    Construit le nom de fichier et le chemin complet d'une vidéo.

    La vidéo est enregistrée dans un sous-dossier correspondant à la langue.

    Exemple :
        data/fr/fr_20260521_101530.mp4
        data/en/en_20260521_101530.mp4

    Paramètres :
        data_dir : dossier racine de sauvegarde des vidéos.
        language_code : code de la langue sélectionnée, par exemple "fr" ou "en".

    Retourne :
        - le nom de fichier sans extension ;
        - le chemin complet du fichier vidéo avec extension .mp4.
    """

    # Crée le dossier racine data s'il n'existe pas déjà.
    data_dir.mkdir(parents=True, exist_ok=True)

    # Construit le sous-dossier correspondant à la langue.
    language_dir = data_dir / language_code

    # Crée le dossier de langue s'il n'existe pas déjà.
    language_dir.mkdir(parents=True, exist_ok=True)

    # Génère un timestamp pour obtenir un nom de fichier unique.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Construit le nom de base du fichier.
    file_base_name = f"{language_code}_{timestamp}"

    # Ajoute l'extension .mp4 et construit le chemin complet.
    video_filepath = language_dir / f"{file_base_name}.mp4"

    return file_base_name, video_filepath
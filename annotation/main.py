import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from annotation.annotation_context import AnnotationContext
from annotation.file_pairing import match_video_and_metadata_files

def parse_arguments():
    """
    Analyse les arguments fournis en ligne de commande.

    Retourne :
        un objet contenant les arguments récupérés.
    """

    # Création du parseur principal.
    parser = argparse.ArgumentParser(
        description="Annotation automatique des vidéos avec Whisper."
    )

    # Code de la langue à traiter.
    # Exemple :
    # python -m annotation.main --language fr
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        help="Code de la langue à traiter, par exemple : fr, en, it."
    )

    # Dossier racine contenant les données.
    # Par défaut, le programme utilise le dossier data/ du projet.
    # Cet argument reste optionnel pour garder un lancement simple.
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Dossier racine des données. Par défaut : data."
    )

    # Modèle Whisper à utiliser.
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Modèle Whisper à utiliser."
    )

    # Mode simulation.
    # Si cette option est présente, le programme affiche ce qu'il ferait,
    # mais ne lance pas réellement Whisper.
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les fichiers qui seraient traités sans lancer Whisper."
    )

    # Analyse les arguments saisis dans le terminal.
    return parser.parse_args()

if __name__ == "__main__":
    # Lit les arguments de la ligne de commande.
    args = parse_arguments()
    
    annotation_context = AnnotationContext (args.language, args.data_dir, args.model)

    annotation_context.validate_paths()

    annotation_context.load_file_list()

    if args.dry_run:
        annotation_context.display_files()
    
    valid_pairs, videos_without_metadata, metadatas_without_video = match_video_and_metadata_files(annotation_context.video_files, annotation_context.metadata_files, annotation_context.videos_dir, annotation_context.metadatas_dir)

    

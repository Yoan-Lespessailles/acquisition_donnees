import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from annotation.annotation_context import AnnotationContext
from annotation.whisper_manager import WhisperManager
from annotation.file_pairing import match_video_and_metadata_files
from annotation.file_isolation_manager import move_unmatched_files, move_pair_to_human_review

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
        default="small",
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
    
    annotation_context = AnnotationContext (args.language, args.data_dir)

    annotation_context.validate_paths()

    annotation_context.load_file_list()

    if args.dry_run:
        annotation_context.display_files()
    
    valid_pairs, videos_without_metadata, metadatas_without_video = match_video_and_metadata_files(annotation_context.video_files, annotation_context.metadata_files, annotation_context.videos_dir, annotation_context.metadatas_dir)

    move_videos_cpt, move_metadatas_cpt = move_unmatched_files (annotation_context.language_dir, videos_without_metadata, metadatas_without_video)

    if move_videos_cpt > 0 or move_metadatas_cpt > 0 :
        print(f"{move_videos_cpt} fichiers vidéos déplacés")
        print(f"{move_metadatas_cpt} fichiers de métadonnées déplacés")
    else:
        print("Aucun fichier à déplacer")

    whisper_manager = WhisperManager(args.model, valid_pairs)

    whisper_manager.oral_transcription()

    move_files_cpt = move_pair_to_human_review (annotation_context.language_dir, whisper_manager.non_compliant_pairs)

    if move_files_cpt > 0 :
        print(f"{move_files_cpt} fichiers déplacés")
    else:
        print("Aucun fichier à déplacer")
import argparse
import sys

from pathlib import Path

# Récupère la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Permet d'exécuter le fichier directement avec : python annotation_project/annotation/main.py
# Sans cette condition, les imports absolus peuvent échouer si Python ne trouve pas correctement la racine du projet
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from annotation.annotation_context import AnnotationContext
from annotation.file_pairing import match_video_and_metadata_files
from annotation.mfa_manager import MfaManager
from annotation.subtitle_manager import SubtitleManager


def parse_arguments():
    """
    Analyse les arguments fournis en ligne de commande.

    Cette fonction définit les options disponibles pour lancer le programme :
        - la langue à traiter ;
        - le dossier contenant les données ;
        - le mode dry-run.

    Retourne :
        argparse.Namespace : objet contenant les arguments récupérés.
    """

    # Crée le parseur principal de la commande
    parser = argparse.ArgumentParser(
        description="Annotation automatique des mots et des phones avec MFA."
    )

    # Ajoute l'argument obligatoire correspondant au code langue
    # Exemple : python -m annotation.main --language fr
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        help="Code de la langue à traiter, par exemple : fr, en, it."
    )

    # Ajoute l'argument permettant de préciser le dossier racine des données
    # Par défaut, le programme utilise le dossier data/ situé à la racine du projet
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "data",
        help="Dossier racine des données. Par défaut : dossier data à la racine du projet."
    )

    # Ajoute le mode simulation
    # Si cette option est présente, le programme affiche les fichiers trouvés sans lancer MFA
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les fichiers qui seraient traités sans lancer MFA."
    )

    # Analyse les arguments saisis dans le terminal
    return parser.parse_args()


if __name__ == "__main__":
    # Récupère les arguments fournis en ligne de commande
    args = parse_arguments()

    # Crée le contexte d'annotation à partir de la langue et du dossier de données
    annotation_context = AnnotationContext(args.language, args.data_dir)

    # Vérifie que les dossiers attendus existent
    annotation_context.validate_paths()

    # Charge les listes de fichiers vidéo et metadata disponibles
    annotation_context.load_file_list()

    # En mode dry-run, le programme affiche simplement les fichiers trouvés
    if args.dry_run:
        annotation_context.display_files()

    else:
        # Associe les vidéos et les fichiers metadata ayant le même nom de base
        valid_pairs, _, _ = match_video_and_metadata_files(
            annotation_context.video_files,
            annotation_context.metadata_files,
            annotation_context.videos_dir,
            annotation_context.metadata_dir
        )

        # Récupère le modèle MFA depuis les métadonnées chargées
        annotation_context.load_mfa_model_name()

        # MFA produit directement les annotations de mots et de phones
        mfa_manager = MfaManager(
            valid_pairs=valid_pairs,
            results_dir=PROJECT_ROOT / "results",
            language_code=args.language,
            acoustic_model=annotation_context.mfa_model_name,
            project_root=PROJECT_ROOT,
        )

        mfa_manager.prepare_validate_and_align()

        subtitle_manager = SubtitleManager(
            valid_pairs=valid_pairs,
            results_dir=PROJECT_ROOT / "results",
            language_code=args.language,
        )

        subtitle_manager.generate_subtitled_videos()

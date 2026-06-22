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


def resolve_mfa_settings(language_code):
    """
    Détermine automatiquement les ressources MFA à utiliser
    à partir du code langue.

    Paramètre :
        language_code (str) : code de la langue à traiter, par exemple "fr".

    Retourne :
        tuple[Path, str] : chemin du dictionnaire personnalisé et nom du modèle acoustique.
    """

    # Associe chaque code langue au modèle acoustique MFA correspondant
    acoustic_models = {
        "fr": "french_mfa",
        "en": "english_mfa",
        "it": "italian_mfa",
        "es": "spanish_mfa",
        "de": "german_mfa",
    }

    # Normalise le code langue pour éviter les différences du type "FR" / "fr"
    language_code = language_code.lower()

    # Construit automatiquement le chemin du dictionnaire personnalisé
    dictionary_path = (
        PROJECT_ROOT
        / "mfa"
        / "dictionaries"
        / f"{language_code}_custom.dict"
    )

    # Récupère le modèle acoustique associé à la langue
    acoustic_model = acoustic_models.get(language_code)

    # Si aucun modèle n'est défini, on bloque avec un message explicite
    if acoustic_model is None:
        raise ValueError(
            f"Aucun modèle acoustique MFA n'est défini pour la langue : {language_code}"
        )

    # Si le dictionnaire personnalisé n'existe pas, on bloque aussi clairement
    if not dictionary_path.exists():
        raise FileNotFoundError(
            f"Dictionnaire MFA personnalisé introuvable : {dictionary_path}"
        )

    return dictionary_path, acoustic_model


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

        # Récupère automatiquement le dictionnaire et le modèle MFA selon la langue
        mfa_dictionary_path, mfa_acoustic_model = resolve_mfa_settings(args.language)

        # MFA produit directement les annotations de mots et de phones
        mfa_manager = MfaManager(
            valid_pairs=valid_pairs,
            results_dir=PROJECT_ROOT / "results",
            language_code=args.language,
            dictionary_path=mfa_dictionary_path,
            acoustic_model=mfa_acoustic_model,
        )

        mfa_manager.prepare_validate_and_align()

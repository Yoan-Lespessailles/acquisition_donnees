import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def parse_arguments():
    """
    Lit les arguments passés en ligne de commande.

    Retourne :
        un objet contenant les arguments récupérés.
    """

    # Crée le parseur d'arguments.
    parser = argparse.ArgumentParser(
        description="Annotation automatique des vidéos avec Whisper."
    )

    # Option permettant de traiter toutes les vidéos d'une langue donnée.
    parser.add_argument(
        "--language",
        type=str,
        help="Code de la langue à traiter, par exemple : fr, en, it."
    )

    # Option permettant de traiter une seule vidéo précise.
    parser.add_argument(
        "--video",
        type=str,
        help="Chemin vers une vidéo précise à transcrire."
    )

    # Option permettant de choisir le modèle Whisper à utiliser.
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Modèle Whisper à utiliser."
    )

    # Option booléenne permettant de simuler le traitement.
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les fichiers qui seraient traités sans lancer Whisper."
    )

    # Analyse les arguments reçus.
    return parser.parse_args()
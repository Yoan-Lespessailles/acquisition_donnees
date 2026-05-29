# Important :
# PyAV doit être importé avant PySide6.QtMultimedia.
# Sinon, certaines bibliothèques natives multimédia peuvent être chargées
# dans un ordre qui provoque une erreur libgobject / glib.
import av

import sys, argparse

from PySide6.QtWidgets import QApplication

from main_window import MyWindow


def parse_arguments():
    """
    Lit les arguments passés en ligne de commande.

    Retourne :
        un objet contenant les arguments récupérés.
    """

    # Crée le parseur d'arguments.
    parser = argparse.ArgumentParser(
        description="Application d'acquisition de données audio/vidéo."
    )

    # Argument optionnel permettant de fournir le prénom sans ouvrir la fenêtre de dialogue.
    parser.add_argument(
        "--firstname",
        "-u",
        type=str,
        default=None,
        help="Prénom de l'utilisateur enregistré. Si absent, une fenêtre de saisie est affichée."
    )

    # Analyse les arguments reçus.
    return parser.parse_args()


# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    # Lit les arguments de la ligne de commande.
    args = parse_arguments()

    # création de l’application Qt
    app = QApplication(sys.argv)
    
    # Crée la fenêtre principale en lui transmettant le prénom éventuel.
    window = MyWindow(user_firstname=args.firstname)

    # Affiche la fenêtre principale.
    window.show()

    # Lance la boucle d'événements Qt.
    sys.exit(app.exec())
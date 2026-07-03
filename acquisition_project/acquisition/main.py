# Important :
# PyAV doit être importé avant PySide6.QtMultimedia
# Sinon, certaines bibliothèques natives multimédia peuvent être chargées dans un ordre qui provoque une erreur libgobject / glib
import av

import argparse
import sys
from pathlib import Path

# Quand ce fichier est lancé directement avec :
#     python acquisition/main.py
# Python ne connaît pas automatiquement le dossier racine du projet
# On l'ajoute donc au PYTHONPATH pour que les imports de package comme "from acquisition.main_window import MyWindow" fonctionnent aussi bien en lancement direct qu'avec "python -m acquisition.main"
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from acquisition.main_window import MyWindow


def get_asset_path(relative_path):
    """
    Retourne le chemin d'un fichier asset en mode développement ou après
    compilation avec PyInstaller.
    """
    # En version compilée, PyInstaller expose les fichiers embarqués via _MEIPASS.
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path # type: ignore

    # En mode développement, les assets sont à côté du package acquisition.
    return Path(__file__).resolve().parents[1] / relative_path


APP_ICON_PATH = get_asset_path(Path("acquisition") / "assets" / "AVDataCollector.png")


def configure_windows_app_id():
    """
    Déclare un identifiant d'application Windows explicite pour que la barre
    des tâches utilise l'icône de l'application au lieu d'une icône générique.
    """
    # Cette configuration est propre à Windows.
    if sys.platform != "win32":
        return

    try:
        # ctypes permet d'appeler l'API Windows sans dépendance supplémentaire.
        import ctypes

        # L'identifiant doit être défini avant la création de QApplication.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "AVDataCollector.Acquisition"
        )
    except Exception:
        # L'icône Qt reste configurée même si l'appel Windows échoue.
        pass


def parse_arguments():
    """
    Lit les arguments passés en ligne de commande.

    Retourne :
        un objet contenant les arguments récupérés.
    """

    # Crée le parseur d'arguments
    parser = argparse.ArgumentParser(
        description="Application d'acquisition de données audio/vidéo."
    )

    # Argument optionnel permettant de fournir le prénom sans ouvrir la fenêtre de dialogue
    parser.add_argument(
        "--firstname",
        "-u",
        type=str,
        default=None,
        help="Prénom de l'utilisateur enregistré. Si absent, une fenêtre de saisie est affichée."
    )

    # Analyse les arguments reçus
    return parser.parse_args()


# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    # Lit les arguments de la ligne de commande
    args = parse_arguments()

    configure_windows_app_id()

    # création de l’application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("AVDataCollector")
    app.setApplicationDisplayName("AVDataCollector")
    app_icon = QIcon(str(APP_ICON_PATH))
    app.setWindowIcon(app_icon)
    
    # Crée la fenêtre principale en lui transmettant le prénom éventuel
    window = MyWindow(user_firstname=args.firstname)
    window.setWindowIcon(app_icon)

    # Affiche la fenêtre principale
    window.show()

    # Lance la boucle d'événements Qt
    sys.exit(app.exec())

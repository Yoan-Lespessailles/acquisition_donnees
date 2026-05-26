# Important :
# PyAV doit être importé avant PySide6.QtMultimedia.
# Sinon, certaines bibliothèques natives multimédia peuvent être chargées
# dans un ordre qui provoque une erreur libgobject / glib.
import av

import sys

from PySide6.QtWidgets import QApplication

from main_window import MyWindow

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    # création de l’application Qt
    app = QApplication(sys.argv)
    
    window = MyWindow()
    window.show()

    sys.exit(app.exec())
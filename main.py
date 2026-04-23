import sys
# importe le module système de python

from PySide6.QtWidgets import QApplication
# gère la boucle d’événements (clics, clavier, affichage…)

from PySide6.QtUiTools import QUiLoader
# sert à charger un fichier .ui créé avec Qt Designer

from PySide6.QtCore import QFile
# permet de lire un fichier au format Qt

app = QApplication(sys.argv)
# création de l’application Qt

loader = QUiLoader()
# création d'un “chargeur” d’interface qui va lire le fichier .ui et créer les widgets.

ui_file = QFile("test_pyside6.ui")
# indique le fichier à ouvrir

ui_file.open(QFile.ReadOnly)
# ouverture du fichier en lecture seule (obligatoire pour la lecture)

window = loader.load(ui_file)
# lecture du fichier .ui + création des les widgets + retourne la fenêtre principale

ui_file.close()
# fermeture du fichier

window.show()
# Affiche la fenêtre
# showFullScreen pour ouvrir la fenêtre en grand

app.exec()
# lancement de la boucle Qt permettant de cliquer, d'interagir, de garder la fenêtre ouverte
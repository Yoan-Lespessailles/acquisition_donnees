import sys
# importe le module système de python

from PySide6.QtCore import Slot

from PySide6.QtWidgets import QApplication
# gère la boucle d’événements (clics, clavier, affichage…)

from PySide6.QtMultimedia import QMediaDevices
# permet d'accéder aux périphériques multimédias : micros, caméras...

from PySide6.QtWidgets import QMainWindow, QWidget
from ui_main_pyside6 import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototype Application")
        self.resize(600, 400)

        # Charge l'interface créée avec Qt Designer
        self.setupUi(self)

        # Remplit la liste des micros disponibles
        self.load_microphones()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        self.select_micro.currentIndexChanged.connect(self.micro_changed)

        # Détecte quand l'utilisateur change de caméra
        self.select_micro.currentIndexChanged.connect(self.camera_changed)
    
    def load_microphones(self):
        # Récupère la liste des micros détectés par Qt
        microphones = QMediaDevices.audioInputs()
        
        # Vide la ComboBox au cas où elle contient déjà des éléments
        self.select_micro.clear()

        # Pour chaque micro trouvé
        for micro in microphones:
            # description() = nom lisible affiché à l'utilisateur
            # micro = objet technique stocké en donnée cachée
            self.select_micro.addItem(micro.description(), micro)
    

    @Slot(int)
    def micro_changed(self, index):
        # Récupère le micro associé à l'index sélectionné
        selected_micro = self.select_micro.itemData(index)
        # itemData() -> donnée technique, itemText() -> texte visible

        if selected_micro is not None:
            print("Changement de micro :", selected_micro.description())


    def load_cameras(self):
        # Récupère la liste des caméras détectées par Qt
        cameras = QMediaDevices.videoInputs()

        # Vide la ComboBox au cas où elle contient déjà des élements
        self.select_camera.clear()

        # Pour chaque caméra trouvée
        for camera in cameras:
            self.select_camera.addItem(camera.description(), camera)    


    @Slot(int)
    def camera_changed(self, index):
        # Récupère la caméra associée à l'index sélectionné
        selected_camera = self.select_micro.itemData(index)
        
        if selected_camera is not None:
            print("Changement de caméra : ", selected_camera.description())

    
    @Slot()
    def button_record_clicked(self):
        # Récupère le micro actuellement sélectionné
        selected_micro = self.select_micro.currentData()
        if selected_micro is None:
            print("Aucun micro sélectionné")
            return
    
        selected_camera = self.select_camera.currentData()
        if selected_camera is None:
            print("Aucune caméra sélectionnée")
            return

        print("Micro sélectionné : ", selected_micro.description())
        print("Caméra sélectionnée : ", selected_camera.description())


# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())
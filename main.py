import sys
# importe le module système de python

from PySide6.QtCore import Slot

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
# gère la boucle d’événements (clics, clavier, affichage…)

from PySide6.QtMultimedia import QMediaDevices, QCamera, QMediaCaptureSession
# QMediaDevices permet d'accéder aux périphériques multimédias : micros, caméras...

from PySide6.QtMultimediaWidgets import QVideoWidget

from ui_main_pyside6 import Ui_MainWindow

class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototype Application")
        self.resize(600, 400)

        # Charge l'interface créée avec Qt Designer
        self.setupUi(self)

        self.setStyleSheet("""
                           
            #button_record {   
                background-color: #B8B8B8;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
            }

            #button_record:hover {
                background-color: #ABABAB;
            }

            #button_record:pressed {
                background-color: #919191;
            }

            #button_record[recording="false"] {
                background-color: #B8B8B8;
            }

            #button_record[recording="true"] {
                background-color: 870101;
            }
        """)

        # Remplit la liste des micros disponibles
        self.load_microphones()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        self.select_micro.currentIndexChanged.connect(self.micro_changed)

        # Détecte quand l'utilisateur change de caméra
        self.select_camera.currentIndexChanged.connect(self.camera_changed)

        # Prépare la zone vidéo
        self.setup_camera_preview()
    
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
        selected_camera = self.select_camera.itemData(index)
        
        if selected_camera is not None:
            print("Changement de caméra : ", selected_camera.description())

    
    @Slot()
    def button_record_clicked(self):
        # Récupère le micro actuellement sélectionné
        selected_micro = self.select_micro.currentData()
        if selected_micro is None:
            print("Aucun micro sélectionné")
            #return
    
        selected_camera = self.select_camera.currentData()
        if selected_camera is None:
            print("Aucune caméra sélectionnée")
            #return
        
        print("=== DEBUG DEVICES ===")
        print("MICRO OBJECT :", selected_micro)
        if selected_micro:
            print("MICRO DESCRIPTION :", selected_micro.description())
            print("MICRO ID :", selected_micro.id())

        # print("CAMERA OBJECT :", selected_camera)
        # if selected_camera:
        #     print("CAMERA DESCRIPTION :", selected_camera.description())
        #     print("CAMERA ID :", selected_camera.id())
        # print("======================")

        print("Micro sélectionné : ", selected_micro.description())
        # print("Caméra sélectionnée : ", selected_camera.description())

        if self.button_record.text() == "Record":
            self.button_record.setText("Stop Record")
            self.button_record.setProperty("recording", True)
        else:
            self.button_record.setText("Record")
            self.button_record.setProperty("recording", False)

        # Refresh du style
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

    def setup_camera_preview(self):
        # Crée le widget vidéo qui affichera le retour caméra
        self.video_widget = QVideoWidget()

        # Crée un layout dans le QWidget vide créé dans Designer
        layout = QVBoxLayout(self.widget_camera)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)

        # Crée la session de capture Qt
        self.capture_session = QMediaCaptureSession()

        # Récupère les caméras détectées par Qt
        cameras = QMediaDevices.videoInputs()

        if not cameras:
            print("Aucune caméra détectée")
            return

        # Prend la première caméra pour le test
        self.camera = QCamera(cameras[0])

        # Branche la caméra à la session
        self.capture_session.setCamera(self.camera)

        # Branche la sortie vidéo au QVideoWidget
        self.capture_session.setVideoOutput(self.video_widget)

        # Lance le retour caméra
        self.camera.start()

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())
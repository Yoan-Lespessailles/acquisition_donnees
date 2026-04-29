import sys
# Importe le module système de python

import subprocess
# Permet de lancer des programmes externes (ici FFmpeg)

from datetime import datetime
# Permet générer un nom de fichier avec la date/heure

from PySide6.QtCore import Slot

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
# Gère la boucle d’événements (clics, clavier, affichage…)

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
                           
            #button_record[recording="false"], #button_record[recording="true"]{   
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
            }

            #button_record[recording="false"]:hover {
                background-color: #ABABAB;
            }

            #button_record[recording="true"]:hover {
                background-color: #C70000;
            }

            #button_record[recording="false"]:pressed {
                background-color: #919191;
            }
                           
            #button_record[recording="true"]:pressed {
                background-color: #A60303;
            }
                           
            #button_record[recording="false"] {
                background-color: #B8B8B8;
            }

            #button_record[recording="true"] {
                background-color: #D10000 ;
            }
        """)

        # Active le QSS
        self.button_record.setProperty("recording", False)

        # Remplit la liste des micros disponibles
        self.load_microphones()

        # Remplit la liste des caméras disponibles
        self.load_cameras()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        self.select_micro.currentIndexChanged.connect(self.micro_changed)
        # Quand on sélectionne un micro, on appelle la fonction micro_changed

        # Détecte quand l'utilisateur change de caméra
        self.select_camera.currentIndexChanged.connect(self.camera_changed)

        # Prépare la zone vidéo
        self.setup_camera_preview()

        self.ffmpeg_process = None
        # Contient le processus FFmpeg en cours (si enregistrement actif)

        self.is_recording = False
        # Permet de savoir si on est en train d’enregistrer ou non

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

    def get_micro_id(self) :
        selected_micro = self.select_micro.currentData()
        # id() renvoie un QByteArray Qt, c'est-à-dire des données binaires.
        # On le convertit en str Python pour pouvoir l'utiliser facilement
        # avec startswith() et dans la commande FFmpeg.
        return bytes(selected_micro.id()).decode()

    def get_camera_id(self) :
        selected_camera = self.select_camera.currentData()
        # Même logique que pour le micro : Qt donne un QByteArray,
        # FFmpeg attend une chaîne Python dans la liste de commande.
        return bytes(selected_camera.id()).decode()

    # ========== BLOC TEST ==========

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

    # AFFICHAGE CONSOLE CHANGEMENT DE CAMERA
    @Slot(int)
    def camera_changed(self, index):
        # Récupère la caméra associée à l'index sélectionné
        selected_camera = self.select_camera.itemData(index)
        
        if selected_camera is not None:
            print("Changement de caméra : ", selected_camera.description())

            # Changement du flux vidéo
            if hasattr(self, "camera"):
                self.camera.stop()
            self.camera = QCamera(selected_camera)
            self.capture_session.setCamera(self.camera)
            self.camera.start()

    # ========== BLOC TEST ==========

    
    @Slot()
    def button_record_clicked(self):

        # ========== BLOC TEST INFOS MICRO + CAMERA ==========

        # Récupère les données du micro et de la caméra actuellement sélectionné
        selected_micro = self.select_micro.currentData()
        selected_camera = self.select_camera.currentData()
        
        print("MICRO OBJECT :", selected_micro)
        print("MICRO DESCRIPTION :", selected_micro.description())
        print("MICRO ID :", selected_micro.id(), "\n")

        print("CAMERA OBJECT :", selected_camera)
        print("CAMERA DESCRIPTION :", selected_camera.description())
        print("CAMERA ID :", selected_camera.id())

        # ========== FIN BLOC TEST ==========

        # ========== BLOC STYLE DU BOUTON RECORD ==========

        if self.button_record.text() == "Record":
            self.button_record.setText("Stop Record")
            self.button_record.setProperty("recording", True)
        else:
            self.button_record.setText("Record")
            self.button_record.setProperty("recording", False)

        # Refresh du style
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # ========== BLOC STYLE DU BOUTON RECORD ==========

        if not self.is_recording :
            self.start_recording()
        else :
            self.stop_recording()

        self.is_recording = not self.is_recording

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

    def start_recording(self):
        micro_id = self.get_micro_id()
        camera_id = self.get_camera_id()

        if micro_id is None:
            print("Aucun micro sélectionné")
            return False

        if camera_id is None:
            print("Aucune caméra sélectionnée")
            return False

        audio_format = self.get_audio_format(micro_id)

        output_file = datetime.now().strftime("record_%Y%m%d_%H%M%S.mp4")

        # Format : ffmpeg -f v4l2 -i /dev/video1 -f pulse -i alsa_input.pci-0000_00_1f.3.analog-stereo output.mp4
        command = [
            "ffmpeg",
            "-f", "v4l2",
            "-i", camera_id,
            "-f", audio_format,
            "-i", micro_id,
            output_file
        ]

        print("Commande FFmpeg :", " ".join(command))

        # Création du fichier et écriture en continue
        self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)

        print("Enregistrement démarré :", output_file)
        return True

    def stop_recording(self):
        self.ffmpeg_process.stdin.write(b"q")
        self.ffmpeg_process.stdin.flush()
        self.ffmpeg_process.wait()

    def get_audio_format(self, micro_id):
        # Ici micro_id est déjà une str Python grâce à get_micro_id().
        # On utilise donc startswith(), et non startsWith() qui est une méthode Qt prévue pour les QByteArray.
        if micro_id.startswith("alsa_input"):
            return "pulse"
        elif micro_id.startswith("hw:"):
            return "alsa"
        else:
            return "pulse"
    # Pas nécessaire de faire une méthode car pour la vidéo ce sera toujours v4l2

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())

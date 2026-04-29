import platform

import sys
# Importe le module système de python

import subprocess
# Permet de lancer des programmes externes (ici FFmpeg)

from datetime import datetime
# Permet générer un nom de fichier avec la date/heure

from PySide6.QtCore import Slot, QTimer

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

        # Contient la caméra Qt utilisée pour l'aperçu
        self.camera = None

        # Contient la session de capture Qt
        self.capture_session = None

        # Contient le widget vidéo Qt
        self.video_widget = None

        # Contient le processus FFmpeg en cours
        self.ffmpeg_process = None

        # Permet de savoir si on est en train d’enregistrer ou non
        self.is_recording = False

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
    

    def get_micro_id(self) :
        selected_micro = self.select_micro.currentData()
        # id() renvoie un QByteArray Qt, c'est-à-dire des données binaires.
        # On le convertit en str Python pour pouvoir l'utiliser facilement
        # avec startswith() et dans la commande FFmpeg.
        return bytes(selected_micro.id()).decode()


    # AFFICHAGE CONSOLE
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

        
    def get_camera_id(self) :
        selected_camera = self.select_camera.currentData()
        # Même logique que pour le micro : Qt donne un QByteArray,
        # FFmpeg attend une chaîne Python dans la liste de commande.
        return bytes(selected_camera.id()).decode()


    # AFFICHAGE CONSOLE
    @Slot(int)
    def camera_changed(self, index):
        # Récupère la caméra associée à l'index sélectionné
        selected_camera = self.select_camera.itemData(index)
        
        if selected_camera is not None:
            print("Changement de caméra : ", selected_camera.description())

            if self.capture_session is None:
                return

            if self.camera is not None:
                self.camera.stop()

            self.camera = QCamera(selected_camera)
            self.capture_session.setCamera(self.camera)
            self.camera.start()
    
    @Slot()
    def button_record_clicked(self):

        selected_micro = self.select_micro.currentData()
        selected_camera = self.select_camera.currentData()

        if selected_micro is None:
            print("Aucun micro sélectionné")
            return

        if selected_camera is None:
            print("Aucune caméra sélectionnée")
            return

        # ========== AFFICHAGE INFOS MICRO ET CAMERA ==========
        # Récupère le micro actuellement sélectionné
        selected_micro = self.select_micro.currentData()
        selected_camera = self.select_camera.currentData()
        
        print("MICRO OBJECT :", selected_micro)
        print("MICRO DESCRIPTION :", selected_micro.description())
        print("MICRO ID :", selected_micro.id(), "\n")

        print("CAMERA OBJECT :", selected_camera)
        print("CAMERA DESCRIPTION :", selected_camera.description())
        print("CAMERA ID :", selected_camera.id())
        # ========== FIN AFFICHAGE INFOS MICRO ET CAMERA ==========

        # Si on n'enregistre pas encore, on démarre
        if not self.is_recording:
            success = self.start_recording()

            if success:
                self.is_recording = True

                self.select_micro.setEnabled(False)
                self.select_camera.setEnabled(False)

                self.button_record.setText("Stop Record")
                self.button_record.setProperty("recording", True)

        # Si on enregistre déjà, on arrête
        else:
            self.stop_recording()

            self.is_recording = False

            self.select_micro.setEnabled(True)
            self.select_camera.setEnabled(True)

            self.button_record.setText("Record")
            self.button_record.setProperty("recording", False)

        # Refresh du style QSS
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


    # ========== START AND STOP AFFICHAGE CAMERA ==========
    def start_camera_preview(self):
        selected_camera = self.select_camera.currentData()

        if selected_camera is not None and self.capture_session is not None:
            self.camera = QCamera(selected_camera)
            self.capture_session.setCamera(self.camera)
            self.camera.start()
            print("Aperçu caméra Qt relancé")

    def stop_camera_preview(self):
        if self.camera is not None:
            self.camera.stop()

            if self.capture_session is not None:
                self.capture_session.setCamera(None)

            self.camera = None

            print("Aperçu caméra Qt arrêté et caméra libérée")
    # ========== START AND STOP AFFICHAGE CAMERA ==========


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

        # Format : ffmpeg -f v4l2 -i /dev/video1 -f pulse -i alsa_input.pci-0000_00_1f.3.analog-stereo output.mp4 -> sous linux
        command = [
            "ffmpeg",
            "-y",
            "-f", "v4l2",
            "-i", camera_id,
            "-f", audio_format,
            "-i", micro_id,
            output_file
        ]

        print("Commande FFmpeg :", " ".join(command))

        # Arrêt de l'aperçu Qt pour libérer la caméra
        self.stop_camera_preview()

        # On attend 500 ms avant de lancer FFmpeg
        QTimer.singleShot(500, lambda: self.launch_ffmpeg(command, output_file))

        return True


    def launch_ffmpeg(self, command, output_file):
        self.ffmpeg_process = subprocess.Popen(command,stdin=subprocess.PIPE)

        print("Enregistrement démarré :", output_file)


    def get_audio_format(self, micro_id):
        if micro_id.startswith("alsa_input"):
            return "pulse"
        elif micro_id.startswith("hw:"):
            return "alsa"
        else:
            return "pulse"
    # Pas nécessaire de faire une méthode car pour la vidéo ce sera toujours v4l2

    def stop_recording(self):
        if self.ffmpeg_process is not None:

            # Vérifie si FFmpeg est encore en cours d'exécution
            if self.ffmpeg_process.poll() is None:
                try:
                    self.ffmpeg_process.stdin.write(b"q")
                    self.ffmpeg_process.stdin.flush()
                    self.ffmpeg_process.wait()
                    print("Enregistrement arrêté")
                except BrokenPipeError:
                    print("FFmpeg était déjà arrêté")
            else:
                print("FFmpeg était déjà terminé")

            self.ffmpeg_process = None

        # Rebranche la caméra Qt à la session avant de relancer l'aperçu
        self.start_camera_preview()

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())

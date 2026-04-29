import sys
# Importe le module système de python

import subprocess
# Permet de lancer des programmes externes (ici FFmpeg)

from datetime import datetime
# Permet générer un nom de fichier avec la date/heure

from PySide6.QtCore import Slot, QThread, Signal
# Slot permet de déclarer des méthodes connectées aux signaux Qt
# QThread permet de lancer la lecture FFmpeg dans un thread séparé
# Signal permet d'envoyer une image du thread vers l'interface graphique

from PySide6.QtGui import QPixmap
# QImage représente une image en mémoire
# QPixmap permet d'afficher cette image dans un QLabel

from PySide6.QtWidgets import QApplication, QMainWindow
# Gère la boucle d’événements (clics, clavier, affichage…)

from PySide6.QtMultimedia import QMediaDevices
# QMediaDevices permet d'accéder aux périphériques multimédias : micros, caméras...

from ui_main_pyside6 import Ui_MainWindow
# Importe l'interface générée à partir du fichier .ui créé avec Qt Designer

from ffmpeg_preview_thread import FFmpegPreviewThread
# Thread chargé de lancer FFmpeg pour l'aperçu caméra

class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototype Application")
        self.preview_width = 640
        self.preview_height = 480
        self.resize(self.preview_width, self.preview_height)

        # Contiendra le thread qui gère l'aperçu caméra avec FFmpeg.
        # Au démarrage, aucun aperçu n'est encore lancé.
        self.preview_thread = None

        # Charge l'interface créée avec Qt Designer
        self.setupUi(self)

        # Contient le processus FFmpeg en cours (si enregistrement actif), au lancement non
        self.ffmpeg_process = None

        # Permet de savoir si on est en train d’enregistrer ou non
        self.is_recording = False

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
        self.button_record.setProperty("recording", "false")

        # Remplit la ComboBox avec la liste des micros disponibles
        self.load_microphones()

        # Remplit la ComboBox avec la liste des caméras disponibles
        self.load_cameras()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        self.select_micro.currentIndexChanged.connect(self.micro_changed)
        # Quand on sélectionne un micro, on appelle la fonction micro_changed

        # Détecte quand l'utilisateur change de caméra
        self.select_camera.currentIndexChanged.connect(self.camera_changed)

        # Lance l'aperçu caméra via FFmpeg
        self.start_preview()

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

    # ========== AFFICHAGE CONSOLE CHANGEMENT DU MICRO ==========

    @Slot(int)
    def micro_changed(self, index):
        # Récupère le micro associé à l'index sélectionné
        selected_micro = self.select_micro.itemData(index)
        # itemData() -> donnée technique, itemText() -> texte visible

        if selected_micro is not None:
            print("Changement de micro :", selected_micro.description())

    # ========== FIN AFFICHAGE CONSOLE CHANGEMENT DU MICRO ==========

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

    # ========== AFFICHAGE CONSOLE CHANGEMENT DE LA CAMERA ==========

    @Slot(int)
    def camera_changed(self, index):
        # Récupère la caméra associée à l'index sélectionné
        selected_camera = self.select_camera.itemData(index)
        
        if selected_camera is not None:
            print("Changement de caméra : ", selected_camera.description())

    # ========== FIN AFFICHAGE CONSOLE CHANGEMENT DE LA CAMERA ==========

    def update_preview_frame(self, image):
        # Convertit l'image reçue depuis le thread FFmpeg en QPixmap.
        # QLabel affiche plus facilement un QPixmap qu'une QImage.
        pixmap = QPixmap.fromImage(image)

        # Redimensionne l'image pour l'adapter à la taille du QLabel.
        # Pour l'instant, cette version peut déformer légèrement l'image
        # si le QLabel n'a pas le même ratio que la caméra.
        pixmap = pixmap.scaled(self.label_camera_preview.size())

        # Affiche l'image dans le QLabel créé avec Qt Designer.
        self.label_camera_preview.setPixmap(pixmap)


    def start_preview(self):
        # Récupère l'identifiant de la caméra sélectionnée
        camera_id = self.get_camera_id()

        # Vérifie qu'une caméra est bien sélectionnée
        if camera_id is None:
            print("Aucune caméra sélectionnée")
            return False

        # Vérifie qu'un aperçu n'est pas déjà en cours
        if self.preview_thread is not None:
            print("Aperçu déjà en cours")
            return True

        # Crée le thread FFmpeg avec la caméra sélectionnée
        self.preview_thread = FFmpegPreviewThread(camera_id, self.preview_width, self.preview_height)

        # Connecte le signal du thread à la méthode qui affichera l'image dans le QLabel
        self.preview_thread.frame_ready.connect(self.update_preview_frame)

        # Lance le thread, donc FFmpeg
        self.preview_thread.start()

        print("Aperçu caméra démarré")
        return True


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

        # ========== FIN BLOC TEST INFOS MICRO + CAMERA ==========

        # ========== BLOC STYLE DU BOUTON RECORD ==========

        if self.button_record.text() == "Record":
            self.button_record.setText("Stop Record")
            self.button_record.setProperty("recording", "true")
        else:
            self.button_record.setText("Record")
            self.button_record.setProperty("recording", "false")

        # Refresh du style
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # ========== BLOC STYLE DU BOUTON RECORD ==========

        if not self.is_recording :
            self.start_recording()
        else :
            self.stop_recording()

        self.is_recording = not self.is_recording

# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())

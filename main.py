import sys
# Importe le module système de Python

from datetime import datetime
# Permet de générer un nom de fichier avec la date/heure

from pathlib import Path
# Path permet de définir le dossier où enregistrer les vidéos

from PySide6.QtCore import Slot, QTimer, QUrl
# Slot permet de connecter proprement les boutons aux méthodes
# QTimer pourra servir pour un compte à rebours, un voyant rouge clignotant, etc.
# QUrl permet d’indiquer à Qt l’emplacement du fichier vidéo à enregistrer

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
# QApplication gère la boucle d’événements
# QMainWindow est la fenêtre principale
# QVBoxLayout peut servir à placer dynamiquement le widget vidéo

from PySide6.QtMultimedia import (
    QMediaDevices,
    QCamera,
    QMediaCaptureSession,
    QMediaRecorder,
    QAudioInput,
    QMediaFormat,
)
# QMediaDevices permet d'accéder aux périphériques multimédias : caméras, micros...
# QCamera gère la caméra
# QMediaCaptureSession relie caméra, micro, preview et enregistreur
# QMediaRecorder permet d'enregistrer la vidéo
# QAudioInput permet de connecter un micro à la session
# QMediaFormat permet de choisir le format d'enregistrement

from PySide6.QtMultimediaWidgets import QVideoWidget
# QVideoWidget permet d'afficher le retour vidéo dans l'interface

from ui_main_pyside6 import Ui_MainWindow
# Interface générée depuis Qt Designer

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


        # ========== ATTRIBUTS RELATIF A LA VISUALISATION ET L'ENREGISTREMENT ==========
        # Contient la caméra Qt utilisée pour l'aperçu et l'enregistrement
        self.camera = None

        # Contient le micro Qt utilisée pour l'enregistrement
        self.audioInput = None

        # Contient la session de capture Qt
        self.capture_session = None

        # Contient le widget vidéo Qt
        self.video_widget = None

        # Contient l’objet responsable de l’enregistrement Qt
        self.recorder = None

        # Permet de savoir si on est en train d’enregistrer ou non
        self.is_recording = False
        #---------------------------------------------------------------------------

        # Remplit la liste des micros disponibles
        self.load_microphones()

        # Remplit la liste des caméras disponibles
        self.load_cameras()

        # Prépare la zone vidéo
        self.setup_camera_preview()

        # Lance la preview si une caméra existe
        self.start_camera_preview()

        # Prépare le record
        self.setup_recording()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        # Quand on sélectionne un micro, on appelle la fonction micro_changed
        self.select_micro.currentIndexChanged.connect(self.micro_changed)

        # Détecte quand l'utilisateur change de caméra
        self.select_camera.currentIndexChanged.connect(self.camera_changed)

    # ========== AFFICHAGE DE LA LISTE DEROULANTE DES MICROS ET CAMERAS SUR L'INTERFACE ==========
    def load_microphones(self):
        # Vide la ComboBox au cas où elle contient déjà des éléments
        self.select_micro.clear()

        # Récupère la liste des micros détectés par Qt
        microphones = QMediaDevices.audioInputs()
        
        # On vérifie que la liste n'est pas vide
        if microphones :
            # Crée un objet QAudioInput à partir du premier micro détecté
            self.audioInput = QAudioInput(microphones[0])
        else :
            print("Aucun micro détecté")

        # Pour chaque micro trouvé
        for micro in microphones:
            # description() = nom lisible affiché à l'utilisateur
            # micro = objet technique stocké en donnée cachée
            self.select_micro.addItem(micro.description(), micro)
    

    def load_cameras(self):
        # Vide la ComboBox au cas où elle contient déjà des élements
        self.select_camera.clear()

        # Récupère la liste des caméras détectées par Qt
        cameras = QMediaDevices.videoInputs()

        # On vérifie que la liste n'est pas vide
        if cameras :
            # Crée un objet QCamera à partir de la première caméra détectée
            self.camera = QCamera(cameras[0])
        else :
            print("Aucune caméra détectée")

        # Pour chaque caméra trouvée
        for camera in cameras:
            self.select_camera.addItem(camera.description(), camera)
    


    # ========== RECUPERATION DES DONNES DU MICRO ET DE LA CAMERA SELECTIONEE ==========
    def get_data_micro(self) :
        return self.select_micro.currentData()
    
    def get_data_camera(self) :
        return self.select_camera.currentData()



    # ========== PREVIEW CAMERA ==========
    def setup_camera_preview(self):

        # Crée le widget vidéo qui affichera le retour caméra
        self.video_widget = QVideoWidget()

        # Crée un layout dans le QWidget vide créé dans Designer
        layout = QVBoxLayout(self.widget_camera)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)

        # Cette session servira à relier la caméra, le micro, la preview et le recorder
        self.capture_session = QMediaCaptureSession()

        # Branche la sortie vidéo au QVideoWidget
        self.capture_session.setVideoOutput(self.video_widget)


    def start_camera_preview(self):
        # Si aucune caméra n'est disponible, on ne peut pas lancer la preview
        if self.camera is None:
            print("Aucune caméra disponible pour la preview")
            return

        # Branche la caméra à la session de capture
        self.capture_session.setCamera(self.camera)

        # Lance le retour caméra (flux vidéo)
        self.camera.start()


    def setup_recording(self) :
        # Création de l’objet responsable de l’enregistrement
        self.recorder = QMediaRecorder()

        # Création d'un format d'enregistrement explicite
        media_format = QMediaFormat()

        # Définit le conteneur vidéo : fichier .mp4
        media_format.setFileFormat(QMediaFormat.MPEG4)

        # Définit le codec vidéo : MPEG4, souvent plus simple à encoder que H264/H265
        media_format.setVideoCodec(QMediaFormat.VideoCodec.MPEG4)

        # Définit le codec audio : AAC, adapté au MP4
        media_format.setAudioCodec(QMediaFormat.AudioCodec.AAC)

        # Applique le format au recorder
        self.recorder.setMediaFormat(media_format)

        # Branche le recorder à la session multimédia.
        self.capture_session.setRecorder(self.recorder)

        # Si un micro existe, on le branche à la session
        if self.audioInput is not None:
            self.capture_session.setAudioInput(self.audioInput)
        else:
            print("Aucun micro disponible")      


    # ========== CHANGEMENT DES PERIPHERIQUES ==========
    @Slot(int)
    # Le _ signifie : que la méthode reçoit la valeur, mais je ne s’en sert pas.
    def micro_changed(self, _):

        if self.get_data_micro() is not None:
            print("Changement de micro :", self.get_data_micro().description())
            self.audioInput = QAudioInput(self.get_data_micro())
            self.capture_session.setAudioInput(self.audioInput)

    @Slot(int)
    def camera_changed(self, _):
        
        # S'il y a une caméra alors on met à jour la visualisation du flux vidéo
        if self.get_data_camera() is not None:
            print("Changement de caméra : ", self.get_data_camera().description())

            # ========== MISE A JOUR DU PREVIEW VIDEO ==========
            if self.camera is not None:
                self.camera.stop()

            self.camera = QCamera(self.get_data_camera())
            self.start_camera_preview()



    # ========== ENREGISTREMENT DE LA VIDEO ========== 
    def start_recording(self):
        
        # Dossier de destination : /home/dossier_utilisateur/Documents
        documents_dir = Path.home() / "Documents"
        
        # Génère un nom de fichier unique avec la date et l'heure
        filename = datetime.now().strftime("video_%Y%m%d_%H%M%S.mp4")

        # Construit le chemin complet du fichier vidéo
        filepath = documents_dir / filename

        # Affiche le chemin pour vérifier où la vidéo sera enregistrée
        print("Enregistrement dans :", filepath)

        # Indique la destination de l'enregistrement de la vidéo
        self.recorder.setOutputLocation(QUrl.fromLocalFile(str(filepath)))
        
        # Démarre l’enregistrement
        self.recorder.record()

        return True



    # ========== STOPPER ENREGISTREMENT DE LA VIDEO ========== 
    def stop_recording(self):
        self.recorder.stop()



    @Slot()
    def button_record_clicked(self):

        if self.get_data_micro() is None:
            print("Aucun micro sélectionné")
            return

        if self.get_data_camera() is None:
            print("Aucune caméra sélectionnée")
            return

        # Si on enregistre pas encore, on démarre
        if not self.is_recording:
            success = self.start_recording()

            # ========== AFFICHAGE INFOS MICRO ET CAMERA ==========
       
            print("MICRO OBJECT :", self.get_data_micro())
            print("MICRO DESCRIPTION :", self.get_data_micro().description())
            print("MICRO ID :", self.get_data_micro().id(), "\n")

            print("CAMERA OBJECT :", self.get_data_camera())
            print("CAMERA DESCRIPTION :", self.get_data_camera().description())
            print("CAMERA ID :", self.get_data_camera().id())

            if success:
                self.is_recording = True

                # Empêche l'utilisateur de changer les périphériques pendant l'enregistrement
                self.select_micro.setEnabled(False)
                self.select_camera.setEnabled(False)

                # Modifie le texte du bouton et l'aspect QSS
                self.button_record.setText("Stop Record")
                self.button_record.setProperty("recording", True)

        # Si on enregistre déjà, on arrête
        else:
            self.stop_recording()

            self.is_recording = False

            # Débloque le changement des périphériques
            self.select_micro.setEnabled(True)
            self.select_camera.setEnabled(True)

            # Modifie le texte du bouton et l'aspect QSS
            self.button_record.setText("Record")
            self.button_record.setProperty("recording", False)

        # Refresh du style QSS
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)


# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())

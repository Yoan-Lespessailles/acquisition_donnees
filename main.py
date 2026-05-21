# Importe le module système de Python
import sys, random, json

# Permet de générer un nom de fichier avec la date/heure
from datetime import datetime

# Path permet de définir le dossier où enregistrer les vidéos
from pathlib import Path

# Slot permet de connecter proprement les boutons aux méthodes
# QTimer pourra servir pour un compte à rebours, un voyant rouge clignotant, etc.
# QUrl permet d’indiquer à Qt l’emplacement du fichier vidéo à enregistrer
from PySide6.QtCore import Slot, QTimer, QUrl, Qt

# QApplication gère la boucle d’événements
# QMainWindow est la fenêtre principale
# QVBoxLayout peut servir à placer dynamiquement le widget vidéo
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

# QMediaDevices permet d'accéder aux périphériques multimédias : caméras, micros...
# QCamera gère la caméra
# QMediaCaptureSession relie caméra, micro, preview et enregistreur
# QMediaRecorder permet d'enregistrer la vidéo
# QAudioInput permet de connecter un micro à la session
# QMediaFormat permet de connaître et choisir les formats, codecs vidéo et codecs audio disponibles
from PySide6.QtMultimedia import (
    QMediaDevices,
    QCamera,
    QMediaCaptureSession,
    QMediaRecorder,
    QAudioInput,
    QMediaFormat,
)

from PySide6.QtMultimediaWidgets import QVideoWidget
# QVideoWidget permet d'afficher le retour vidéo dans l'interface

from ui.ui_main_pyside6 import Ui_MainWindow
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

        # Surveille les changements de périphériques audio/vidéo
        self.media_devices = QMediaDevices()

        # Débit vidéo utilisé par l'enregistreur.
        # La valeur sera ajustée automatiquement selon la résolution de la caméra.
        self.video_bitrate = 12_000_000

        # Emplacement du fichier en cours d'enregistrement.
        # Il sert à relancer automatiquement l'enregistrement si H264 échoue.
        self.recording_output_location = QUrl()

        # Indique si on a déjà tenté le fallback H264 -> MPEG4 pour l'enregistrement courant.
        # Cela évite une boucle infinie si MPEG4 échoue aussi.
        self.h264_fallback_tried = False

        # Permet de savoir si on est en train d’enregistrer ou non
        self.is_recording = False

        # Le rond rouge est actuellement masqué
        self.blink_visible = False

        # Timer du clignotement du rond rouge
        self.blink_timer = QTimer()

        # Le clignotement est paramétré sur 500ms 
        self.blink_timer.setInterval(500)

        # Toutes les 500ms la méthode blink_dot est appelée
        self.blink_timer.timeout.connect(self.blink_dot)

        # Temps écoulé en secondes
        self.record_seconds = 0

        # Timer du chrono
        self.record_timer = QTimer()

        # Mise à jour du timer paramétré toutes les secondes 
        self.record_timer.setInterval(1000)

        # Toutes les secondes la méthode update_record_timer est appelée
        self.record_timer.timeout.connect(self.update_record_timer) 

        #---------------------------------------------------------------------------

        # ========== ATTRIBUTS RELATIF AU TEXTE ==========
        # Dossier contenant les fichiers JSON de corpus
        self.corpus_dir = Path("corpus")

        # Contient la langue sélectionnée 
        self.language_selected = None

        # Lise des langues disponibles    
        self.languages = []

        self.sentence_num = 20

        self.sentence_cpt = 0

        # Appel de la fonction pour affiche le compteur
        self.update_sentence_counter()

        # Récupère le dossier dans lequel se trouve le fichier Python actuel.
        # Exemple : /home/ylespessailles/stage/projet_stage/data
        self.data_dir = Path(__file__).resolve().parent / Path("data")

        #---------------------------------------------------------------------------

        # Remplit la liste des micros disponibles
        self.load_microphones()

        # Remplit la liste des caméras disponibles
        self.load_cameras()

        # Remplit la liste des langues disponibles
        self.load_language()

        # Prépare la zone vidéo
        self.setup_camera_preview()

        # Lance la preview si une caméra existe
        self.start_camera_preview()

        # Prépare le record
        self.setup_recording()

        # Récupère la liste des templates correspondant à la langue sélectionnée
        self.collect_template()

        # Affiche la première phrase
        self.display_text()

        # Connecte le bouton Record à une méthode
        self.button_record.clicked.connect(self.button_record_clicked)
       
        # Détecte quand l'utilisateur change de micro
        # Quand on sélectionne un micro, on appelle la fonction micro_changed
        self.select_micro.currentIndexChanged.connect(self.micro_changed)

        # Détecte quand l'utilisateur change de caméra
        self.select_camera.currentIndexChanged.connect(self.camera_changed)

        # Détecte quand l'utilisateur change de langue
        self.select_language.currentIndexChanged.connect(self.language_changed)

        # Détecte quand un micro est branché ou débranché
        self.media_devices.audioInputsChanged.connect(self.refresh_micro)

        # Détecte quand une caméra est branchée ou débranchée
        self.media_devices.videoInputsChanged.connect(self.refresh_camera)


    # ========== AFFICHAGE DE LA LISTE DEROULANTE DES MICROS ET CAMERAS SUR L'INTERFACE ==========
    def load_microphones(self):
        # Vide la ComboBox au cas où elle contient déjà des éléments
        self.select_micro.clear()

        # Récupère la liste des micros détectés par Qt
        microphones = QMediaDevices.audioInputs()
        
        # On vérifie que la liste n'est pas vide
        if microphones :
            # Vérification de audioInput
            if self.audioInput is None :
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
            if self.camera is None :
                # Crée un objet QCamera à partir de la première caméra détectée
                self.camera = QCamera(cameras[0])
                self.configure_camera_format(cameras[0])
        else :
            print("Aucune caméra détectée")

        # Pour chaque caméra trouvée
        for camera in cameras:
            self.select_camera.addItem(camera.description(), camera)
    


    # ========== REFRESH DE LA LISTE DES MICROS ET CAMERAS ==========
    def refresh_micro(self):
        # Bloque temporairement les signaux pour éviter de déclencher micro_changed()
        # pendant le clear(), les addItem() et le setCurrentIndex().
        self.select_micro.blockSignals(True)

        # Valeur par défaut si aucun micro n'était sélectionné avant le refresh.
        current_micro_id = None

        # Récupère le micro actuellement sélectionné avant de recharger la liste.
        current_micro = self.get_data_micro()

        # Si un micro était sélectionné, on mémorise son identifiant technique.
        if current_micro is not None:
            current_micro_id = current_micro.id()

        # Recharge la ComboBox avec la nouvelle liste des micros détectés.
        self.load_microphones()

        # Indique si l'ancien micro a été retrouvé après le refresh.
        found = False

        # Parcourt tous les micros affichés dans la ComboBox.
        for index in range(self.select_micro.count()):
            # Récupère l'objet micro stocké dans l'élément courant.
            micro = self.select_micro.itemData(index)

            # Si le micro existe et correspond à l'ancien micro, on le resélectionne.
            if micro is not None and micro.id() == current_micro_id:
                self.select_micro.setCurrentIndex(index)
                found = True
                break

        # Si l'ancien micro n'a pas été retrouvé, on sélectionne le premier micro disponible.
        if not found and self.select_micro.count() > 0:
            self.select_micro.setCurrentIndex(0)

            # Comme les signaux sont bloqués, micro_changed() ne sera pas appelé.
            # Il faut donc mettre à jour manuellement l'objet audio utilisé par Qt.
            selected_micro = self.select_micro.currentData()

            # Si un micro est bien sélectionné, on crée le nouvel objet QAudioInput.
            if selected_micro is not None:
                self.audioInput = QAudioInput(selected_micro)
                self.capture_session.setAudioInput(self.audioInput)

        # S'il n'y a plus aucun micro disponible, on vide l'objet audio.
        elif self.select_micro.count() == 0:
            self.audioInput = None

        # Réactive les signaux après la mise à jour automatique.
        self.select_micro.blockSignals(False)


    def refresh_camera(self):
        # Bloque temporairement les signaux pour éviter de déclencher camera_changed()
        # pendant le clear(), les addItem() et le setCurrentIndex().
        self.select_camera.blockSignals(True)

        # Valeur par défaut si aucune caméra n'était sélectionnée avant le refresh.
        current_camera_id = None

        # Récupère la caméra actuellement sélectionnée avant de recharger la liste.
        current_camera = self.get_data_camera()

        # Si une caméra était sélectionnée, on mémorise son identifiant technique.
        if current_camera is not None:
            current_camera_id = current_camera.id()

        # Recharge la ComboBox avec la nouvelle liste des caméras détectées.
        self.load_cameras()

        # Indique si l'ancienne caméra a été retrouvée après le refresh.
        found = False

        # Parcourt toutes les caméras affichées dans la ComboBox.
        for index in range(self.select_camera.count()):
            # Récupère l'objet caméra stocké dans l'élément courant.
            camera = self.select_camera.itemData(index)

            # Si la caméra existe et correspond à l'ancienne caméra, on la resélectionne.
            if camera is not None and camera.id() == current_camera_id:
                self.select_camera.setCurrentIndex(index)
                found = True
                break

        # Si l'ancienne caméra n'a pas été retrouvée, on sélectionne la première caméra disponible.
        if not found and self.select_camera.count() > 0:
            self.select_camera.setCurrentIndex(0)

            # Comme les signaux sont bloqués, camera_changed() ne sera pas appelé.
            # Il faut donc mettre à jour manuellement la caméra utilisée par Qt.
            selected_camera = self.select_camera.currentData()

            # Si une caméra est bien sélectionnée, on remplace la caméra active.
            if selected_camera is not None:
                if self.camera is not None:
                    self.camera.stop()

                self.camera = QCamera(selected_camera)
                self.configure_camera_format(selected_camera)
                self.start_camera_preview()

        # S'il n'y a plus aucune caméra disponible, on arrête et vide la caméra active.
        elif self.select_camera.count() == 0:
            if self.camera is not None:
                self.camera.stop()

            self.camera = None

        # Réactive les signaux après la mise à jour automatique.
        self.select_camera.blockSignals(False)


    # ========== RECUPERATION DES DONNES DU MICRO ET DE LA CAMERA SELECTIONEE ==========
    def get_data_micro(self) :
        return self.select_micro.currentData()
    
    def get_data_camera(self) :
        return self.select_camera.currentData()



    # ========== CHOIX AUTOMATIQUE DE LA QUALITE CAMERA ==========
    def configure_camera_format(self, camera_device):
        # Si aucune caméra n'est disponible, on ne peut pas choisir de format.
        if self.camera is None or camera_device is None:
            return

        # Récupère les formats supportés par la caméra sélectionnée.
        # Chaque format contient notamment une résolution et un nombre d'images par seconde.
        formats = camera_device.videoFormats()

        # Si Qt ne donne aucun format précis, on garde les réglages automatiques de la caméra.
        if not formats:
            print("Aucun format caméra détaillé disponible")
            return

        # Pour la lecture labiale, on cherche un bon compromis :
        # - d'abord au moins 30 FPS si possible, car les mouvements de lèvres sont rapides
        # - ensuite la meilleure résolution, car les détails autour de la bouche sont importants
        # - enfin le FPS le plus élevé si plusieurs formats ont une résolution proche
        def format_score(camera_format):
            resolution = camera_format.resolution()
            width = resolution.width()
            height = resolution.height()
            pixels = width * height
            max_fps = camera_format.maxFrameRate()
            has_good_fps = max_fps >= 30

            return (has_good_fps, pixels, max_fps)

        # Sélectionne le format ayant le meilleur score selon les critères ci-dessus.
        best_format = max(formats, key=format_score)
        best_resolution = best_format.resolution()
        best_width = best_resolution.width()
        best_height = best_resolution.height()
        best_fps = best_format.maxFrameRate()

        # Applique le format choisi à la caméra avant de lancer la preview/l'enregistrement.
        self.camera.setCameraFormat(best_format)

        # Ajuste le débit vidéo selon la résolution choisie.
        # Plus la résolution est haute, plus il faut de débit pour éviter la pixellisation.
        pixels = best_width * best_height
        if pixels >= 1920 * 1080:
            self.video_bitrate = 20_000_000
        elif pixels >= 1280 * 720:
            self.video_bitrate = 12_000_000
        else:
            self.video_bitrate = 8_000_000

        print(
            "Format caméra choisi :",
            f"{best_width}x{best_height}",
            f"à {best_fps:.0f} FPS",
            "- bitrate vidéo :",
            f"{self.video_bitrate / 1_000_000:.0f} Mbit/s",
        )

        # Si le recorder existe déjà, on met aussi à jour son débit vidéo.
        if self.recorder is not None:
            self.recorder.setVideoBitRate(self.video_bitrate)



    # ========== PREVIEW CAMERA ==========
    def setup_camera_preview(self):

        # Crée le widget vidéo qui affichera le retour caméra
        self.video_widget = QVideoWidget()

        # Remplit la zone de preview en elevant les bandes noires
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)

        # Crée un layout dans le QWidget vide créé dans Designer
        layout = QVBoxLayout(self.area_preview)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Ajoute le widget vidéo dans le layout
        layout.addWidget(self.video_widget)
        
        # Cache le point rouge et le timer (visibles uniquement lors de l'enregistrement)
        self.label_record_timer.hide()
        self.label_record_dot.hide()

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



    # ========== SIGNES DE RECORD ==========
    def show_recording(self):

        # Le timer et le point rouges sont rendus visibles
        self.label_record_timer.show()
        self.label_record_dot.show()

        # Déclenchement du clignotement
        self.blink_visible = True

        # Le timer est mis en marche
        self.blink_timer.start()


    def hide_recording(self):
        # Le timer est stoppé
        self.blink_timer.stop()

        # Le timer et le point rouges sont masqués
        self.label_record_timer.hide()
        self.label_record_dot.hide()


    def set_timer_text(self, text):
        # Met à jour le timer affiché
        self.label_record_timer.setText(text)
        

    def blink_dot(self):
        # Inversion de l'état de l'attribut pour le clignotement 
        self.blink_visible = not self.blink_visible
        # Alterne entre visible et non visible en fonction de l'état de l'attribut blink_visible
        self.label_record_dot.setVisible(self.blink_visible)


    def update_record_timer(self):
        # A chaque appel de la méthode, on rajoute une seconde au compteur
        self.record_seconds+=1

        # Convertit en minutes / secondes
        minutes = self.record_seconds // 60
        seconds = self.record_seconds % 60

        # Formatage du texte à afficher
        timer_text = f"REC. {minutes:02}:{seconds:02}"

        # Mise à jour du timer vidéo 
        self.set_timer_text(timer_text)



    # ========== FORMAT ET PARAMETRES D'ENREGISTREMENT ==========
    def create_recording_media_format(self, preferred_video_codec):
        # Création d'un format d'enregistrement explicite.
        media_format = QMediaFormat()

        # Définit le conteneur vidéo : fichier .mp4.
        # Ici MPEG4 signifie "conteneur MP4", pas "codec vidéo MPEG4".
        media_format.setFileFormat(QMediaFormat.MPEG4)

        # Vérifie les codecs réellement disponibles pour encoder dans un MP4.
        supported_video_codecs = media_format.supportedVideoCodecs(QMediaFormat.ConversionMode.Encode)
        print(
            "Codecs vidéo supportés en encodage MP4 :",
            [codec.name for codec in supported_video_codecs],
        )

        # On tente d'abord le codec demandé.
        # Dans notre cas, ce sera H264 au premier essai.
        if preferred_video_codec in supported_video_codecs:
            media_format.setVideoCodec(preferred_video_codec)

        # Si le codec demandé n'est pas disponible, on bascule vers MPEG4.
        elif QMediaFormat.VideoCodec.MPEG4 in supported_video_codecs:
            print("Codec demandé non disponible, fallback vers MPEG4")
            media_format.setVideoCodec(QMediaFormat.VideoCodec.MPEG4)

        # Dernier recours : MotionJPEG, souvent disponible mais plus lourd.
        else:
            print("Encodeur MPEG4 non disponible, fallback vers MotionJPEG")
            media_format.setVideoCodec(QMediaFormat.VideoCodec.MotionJPEG)

        # Définit le codec audio : AAC, adapté au conteneur MP4.
        media_format.setAudioCodec(QMediaFormat.AudioCodec.AAC)

        return media_format


    def apply_recorder_bitrates(self):
        # On force un encodage piloté par le débit avant de définir le bitrate.
        self.recorder.setEncodingMode(QMediaRecorder.EncodingMode.ConstantBitRateEncoding)

        # Pour éviter que Qt choisisse automatiquement un débit trop faible,
        # on utilise le débit calculé selon la résolution de la caméra.
        self.recorder.setVideoBitRate(self.video_bitrate)

        # Définit le débit audio AAC.
        self.recorder.setAudioBitRate(128_000)


    def setup_recording(self) :
        # Création de l’objet responsable de l’enregistrement
        self.recorder = QMediaRecorder()

        # Premier choix : H264, car il est plus adapté au MP4 et plus efficace que MPEG4.
        media_format = self.create_recording_media_format(QMediaFormat.VideoCodec.H264)
        self.recorder.setMediaFormat(media_format)
        print("Codec vidéo demandé :", self.recorder.mediaFormat().videoCodec().name)

        # Applique les bitrates vidéo/audio.
        self.apply_recorder_bitrates()

        # Surveille les erreurs d'encodage.
        # Si H264 échoue au moment de record(), on relancera automatiquement en MPEG4.
        self.recorder.errorOccurred.connect(self.recorder_error_occurred)

        # Branche le recorder à la session multimédia.
        self.capture_session.setRecorder(self.recorder)

        # Si un micro existe, on le branche à la session
        if self.audioInput is not None:
            self.capture_session.setAudioInput(self.audioInput)
        else:
            print("Aucun micro disponible")      


    # ========== CHANGEMENT DES PERIPHERIQUES ==========
    @Slot(int)
    # Le _ signifie : que la méthode reçoit la valeur, mais ne s’en sert pas.
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
            self.configure_camera_format(self.get_data_camera())
            self.start_camera_preview()



    # ========== ENREGISTREMENT DE LA VIDEO ========== 
    def start_recording(self):
        
        # Crée le dossier "data" s'il n'existe pas déjà.
        # Si le dossier existe déjà, aucune erreur n'est déclenchée.
        self.data_dir.mkdir(exist_ok=True)

        # Le dossier de langue est le dossier de stockage
        file_register = self.data_dir / Path(self.language_selected[1])

        # Crée le dossier code_langue de la langue dans le dossier data s'il n'existe pas déjà.
        file_register.mkdir(exist_ok=True)

        # Crée le nom du fichier
        self.file_name=f"{self.language_selected[1]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}"

        # Génère un nom de fichier unique avec la date et l'heure
        filename = f"{self.file_name}.mp4"

        # Construit le chemin complet du fichier vidéo
        filepath = file_register / filename

        # Affiche le chemin pour vérifier où la vidéo sera enregistrée
        print("Enregistrement dans :", filepath)

        # Indique la destination de l'enregistrement de la vidéo.
        self.recording_output_location = QUrl.fromLocalFile(str(filepath))
        self.recorder.setOutputLocation(self.recording_output_location)

        # Réinitialise le fallback pour ce nouvel enregistrement.
        self.h264_fallback_tried = False
        
        # Démarre l’enregistrement
        self.recorder.record()

        # Montre que l'enregistrement a commencé
        self.show_recording()

        # Compteur de secondes mis à 0
        self.record_seconds = 0

        # Affichage du timer et mise à 0
        self.set_timer_text("REC. 00:00")

        # Lancement du timer
        self.record_timer.start()

        return True



    # ========== STOPPER ENREGISTREMENT DE LA VIDEO ========== 
    def stop_recording(self):
        # Record stoppé
        self.recorder.stop()

        # Affichage masqué
        self.hide_recording()

        # Timer stoppé
        self.record_timer.stop()


    def recorder_error_occurred(self, error, error_string):
        # Affiche l'erreur remontée par Qt/FFmpeg.
        print("Erreur enregistrement :", error, error_string)

        # Si H264 échoue au démarrage, Qt peut remonter une erreur du type h264_vaapi.
        # Dans ce cas, on bascule automatiquement vers MPEG4 et on relance l'enregistrement.
        current_codec = self.recorder.mediaFormat().videoCodec()
        if current_codec == QMediaFormat.VideoCodec.H264 and not self.h264_fallback_tried:
            print("H264 a échoué, relance automatique en MPEG4")

            # Marque le fallback comme déjà tenté pour éviter une boucle infinie.
            self.h264_fallback_tried = True

            # Stoppe proprement le recorder avant de changer son format.
            self.recorder.stop()

            # Laisse un court délai à Qt pour libérer le fichier H264 raté.
            # Ensuite seulement, on supprime ce fichier et on relance en MPEG4.
            QTimer.singleShot(300, self.restart_recording_with_mpeg4)


    def restart_recording_with_mpeg4(self):
        # Récupère le chemin du fichier créé par la tentative H264.
        failed_filepath = Path(self.recording_output_location.toLocalFile())

        # Supprime le fichier H264 invalide avant de relancer l'enregistrement.
        # Si le fichier n'existe pas encore, missing_ok=True évite une erreur inutile.
        failed_filepath.unlink(missing_ok=True)
        print("Fichier H264 invalide supprimé :", failed_filepath)

        # Remplace le format H264 par un format MPEG4.
        media_format = self.create_recording_media_format(QMediaFormat.VideoCodec.MPEG4)
        self.recorder.setMediaFormat(media_format)
        print("Codec vidéo demandé après fallback :", self.recorder.mediaFormat().videoCodec().name)

        # Réapplique les bitrates après le changement de format.
        self.apply_recorder_bitrates()

        # Relance l'enregistrement vers le même chemin, maintenant propre.
        self.recorder.setOutputLocation(self.recording_output_location)
        self.recorder.record()



    # ========== DECLENCHEMENT DE L'ENREGISTREMENT VIDEO ========== 
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
            print("CAMERA ID :", self.get_data_camera().id(), "\n")

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
            
            # On supprime la phrase utilisées
            self.consume_words()
            # On affiche une nouvelle phrase
            self.display_text()

            if self.sentence_cpt < self.sentence_num :
                # On met à jours le compteur de phrases si on ne dépasse pas le nombre de phrases
                self.update_sentence_counter()

            # Débloque le changement des périphériques
            self.select_micro.setEnabled(True)
            self.select_camera.setEnabled(True)

            # Modifie le texte du bouton et l'aspect QSS
            self.button_record.setText("Record")
            self.button_record.setProperty("recording", False)

        # Refresh du style QSS
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)




    # ========== GESTION DU TEXTE AFFICHE ==========
    def load_language(self):
        # Vide la ComboBox au cas où elle contient déjà des élements
        self.select_language.clear()

        # Parcourt tous les fichiers .json du dossier corpus
        for json_file in self.corpus_dir.glob("*.json"):
            try:
                # Ouvre le fichier JSON en lecture avec l'encodage UTF-8 (pour la prise en charge des accents)
                with open(json_file, "r", encoding="utf-8") as file:
                    data = json.load(file)

                # Récupère la valeur de la clé voulue, s'il n'existe pas renvoie None
                language_name = data.get("language_name")
                language_code = data.get("language_code")
                language_data = (language_name,language_code)

                # Si la clé existe, on l'ajoute à la liste
                if language_name:
                    self.languages.append(language_data)
            
            except json.JSONDecodeError:
                # Cette erreur arrive si le fichier existe mais que son contenu
                # n'est pas un JSON valide.
                print(f"Erreur JSON dans le fichier : {json_file}")

            except Exception as e:
                # Cette sécurité permet d'afficher les autres erreurs possibles
                # sans faire planter toute l'application.
                print(f"Erreur lors de la lecture de {json_file} : {e}")

        # On vérifie que la liste n'est pas vide
        if self.languages :
            if self.language_selected is None :
                # On sélectionne la première langue
                self.language_selected = self.languages[0]
                print(f"load_language() -> Langue sélectionnée : {self.language_selected}")

        else :
            print ("Problème avec la liste des langues")

        # Pour chaque langue dans la liste, on les affiche dans la ComboBox
        for language in self.languages:
            self.select_language.addItem(language[0])
    

    @Slot(int)
    def language_changed(self, index):
        # Changement de langue
        self.language_selected = self.languages[index]
        print(f"language_changed -> langue sélectionnée : {self.language_selected}")

        # Mise à jours des phrases
        self.collect_template()

        # Affiche de la phrase
        self.display_text()


    # Prépare les données de travail (copies + mélange) en fonction du choix de langue
    def collect_template(self):
        print(f"collect_template() -> langue sélectionnée : {self.language_selected}")
        code_language = self.language_selected[1]

        for json_file in self.corpus_dir.glob(f"*{code_language}.json"):
            try:
                # Ouvre le fichier JSON en lecture avec l'encodage UTF-8 (pour la prise en charge des accents)
                with open(json_file, "r", encoding="utf-8") as file:
                    self.corpus_data = json.load(file)
            
            except json.JSONDecodeError:
                # Cette erreur arrive si le fichier existe mais que son contenu
                # n'est pas un JSON valide.
                print(f"Erreur JSON dans le fichier : {json_file}")

            except Exception as e:
                # Cette sécurité permet d'afficher les autres erreurs possibles
                # sans faire planter toute l'application.
                print(f"Erreur lors de la lecture de {json_file} : {e}")

        # Copie des listes du template 1
        # self.t1_sujet = corpus_data[code_language]["template1"]["sujet"].copy()
        # self.t1_verbe = corpus_data[code_language]["template1"]["verbe"].copy()
        # self.t1_nombre = corpus_data[code_language]["template1"]["nombre"].copy()
        # self.t1_groupe_nominal = corpus_data[code_language]["template1"]["groupe_nominal"].copy()

        # # Copie du template 2
        # self.t2 = corpus_data[code_language]["template2"].copy()

        # # Mélange pour créer des phrases aléatoire (mais avec la même structure)
        random.shuffle(self.corpus_data["template_1"]["subject"])
        random.shuffle(self.corpus_data["template_1"]["verb"])
        random.shuffle(self.corpus_data["template_1"]["number"])
        random.shuffle(self.corpus_data["template_1"]["nominal_group"])
        random.shuffle(self.corpus_data["template_2"]["sentences"])

        # Remise du cpt de phrases à 0 puis appel de la fonction dédiée
        self.sentence_cpt = 0
        self.update_sentence_counter()

        # Réactivation du bouton record (dans le cas où toutes les phrases ont déjà été enregistrées dans une langue)
        self.button_record.setEnabled(True)


    # Affiche la phrase à lire
    def display_text(self):
        # Tant qu'il reste des éléments dans le Template 1
        if self.corpus_data["template_1"]["subject"]:
            # Appel de la fonction pour prendre en compte l'ordre syntaxique (ex : SVO)
            self.template_1_order()

        # Sinon, on passe au Template 2
        elif self.corpus_data["template_2"]["sentences"]:
            self.sentence = self.corpus_data["template_2"]["sentences"][-1]
        
        # Fin du corpus
        else:
            self.sentence = "Fin de la session d'enregistrement"

            # Désactivation du bouton record
            self.button_record.setEnabled(False)
        
        self.label_sentence.setText(self.sentence)
    

    def template_1_order(self):
        self.sentence=""
        for list in self.corpus_data["template_1"]["structure"] :
            self.sentence += self.corpus_data["template_1"][list][-1]
            self.sentence += " "
        
        self.sentence.strip()


    # Consomme les mots/phrases utilisées
    def consume_words(self):
        # Consommation du Template 1 en priorité
        if self.corpus_data["template_1"]["subject"]:
            for list in self.corpus_data["template_1"]["structure"]:
                self.corpus_data["template_1"][list].pop()
        # Puis consommation du Template 2
        elif self.corpus_data["template_2"]["sentences"]:
            self.corpus_data["template_2"]["sentences"].pop()
        # Lorsque tout est consommé
        else:
            print("Toutes les phrases ont été lues")
            return



    # ========== GESTION DU COMPTEUR ==========
    def update_sentence_counter(self):
        # Incrémentation du compteur
        self.sentence_cpt+=1

        self.label_cpt_sentence.setText(f"{self.sentence_cpt}/{self.sentence_num}")



# Exécute le bloc uniquement si ce fichier est lancé directement, pas s’il est importé
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # création de l’application Qt
    
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec())

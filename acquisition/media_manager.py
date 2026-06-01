# math sert au calcul RMS du niveau sonore.
# struct sert à convertir les données audio brutes en échantillons numériques.
import math
import struct

# QObject permet à MediaManager d'utiliser les signaux Qt.
# QTimer permet d'exécuter régulièrement certaines actions, comme :
# - lire le niveau du micro toutes les 50 ms ;
# - gérer le fallback H264 -> MPEG4 après un court délai.
# QUrl permet de convertir un chemin local en format accepté par Qt.
# Qt sert à configurer certains comportements d'affichage.
# Signal permet à MediaManager d'envoyer des informations à l'interface sans dépendre directement des widgets.
from PySide6.QtCore import QObject, QTimer, QUrl, Qt, Signal

# QVBoxLayout permet d'insérer dynamiquement le widget vidéo dans la zone prévue par Qt Designer.
from PySide6.QtWidgets import QVBoxLayout

# Classes Qt Multimedia utilisées pour :
# - lister les périphériques audio/vidéo ;
# - gérer la caméra ;
# - gérer le micro ;
# - connecter caméra, micro, preview et enregistreur ;
# - enregistrer les vidéos ;
# - tester le niveau sonore du micro.
from PySide6.QtMultimedia import (
    QMediaDevices,
    QCamera,
    QMediaCaptureSession,
    QMediaRecorder,
    QAudioInput,
    QMediaFormat,
    QAudioFormat,
    QAudioSource
)

# QVideoWidget affiche le retour caméra dans l'interface.
from PySide6.QtMultimediaWidgets import QVideoWidget

# Charge la configuration globale du projet : chemins, bitrates, paramètres vidéo, etc.
from acquisition.config_loader import load_config

CONFIG = load_config()

# Crée les chemins de sauvegarde des fichiers générés pendant l'enregistrement.
from utils.file_utils import build_recording_filepaths

# Fonctions utilitaires liées aux formats vidéo :
# - choix du meilleur format caméra ;
# - création du format d'enregistrement.
from utils.media_utils import (
    get_camera_format_score,
    create_recording_media_format,
)


class MediaManager(QObject):
    """
    Gère la partie multimédia de l'application :
    - liste des micros ;
    - liste des caméras ;
    - preview vidéo ;
    - session de capture Qt ;
    - enregistrement audio/vidéo ;
    - test du niveau sonore du micro ;
    - fallback codec H264 vers MPEG4.
    """

    # Signal envoyé à l'interface quand un nouveau niveau micro est calculé.
    # La valeur envoyée est un entier compris entre 0 et 100.
    micro_level_changed = Signal(int)

    def __init__(self, select_micro, select_camera, area_preview):
        """
        Initialise le gestionnaire multimédia.

        Paramètres :
            select_micro : ComboBox contenant la liste des micros disponibles.
            select_camera : ComboBox contenant la liste des caméras disponibles.
            area_preview : QWidget dans lequel afficher la preview vidéo.
        """

        super().__init__()

        # ComboBox de sélection du micro.
        self.select_micro = select_micro

        # ComboBox de sélection de la caméra.
        self.select_camera = select_camera

        # Zone Qt qui recevra le QVideoWidget.
        self.area_preview = area_preview

        # Caméra Qt active.
        self.camera = None

        # Micro Qt actif.
        self.audio_input = None

        # Contient la session de capture Qt
        self.capture_session = None

        # Widget vidéo utilisé pour afficher le retour caméra.
        self.video_widget = None

        # Contient l’objet responsable de l’enregistrement Qt
        self.recorder = None

        # Surveille les changements de périphériques audio/vidéo
        self.media_devices = QMediaDevices()

        # Débit vidéo courant.
        self.video_bitrate = CONFIG["recording"]["video_bitrate_medium"]

        # Débit audio courant
        self.audio_bitrate = CONFIG["recording"]["audio_bitrate"]

        # Emplacement du fichier vidéo en cours d'enregistrement.
        self.recording_output_location = QUrl()

        # Indique si le fallback H264 -> MPEG4 a déjà été tenté.
        self.h264_fallback_tried = False

        # Nom de base du fichier courant, sans extension.
        self.file_name = ""

        # Chemin absolu d'enregistrement du fichier vidéo
        self.video_filepath = None

        # Chemin relatif d'enregistrement du fichier vidéo
        self.video_filepath_rel = None

        # Chemin absolu d'enregistrement du fichier d'annotation
        self.annotation_filepath = None

        # Chemin relatif d'enregistrement du fichier d'annotation
        self.annotation_filepath_rel = None

        # Largeur de la vidéo choisie.
        self.video_width = None

        # Hauteur de la vidéo choisie.
        self.video_height = None

        # FPS du format caméra choisi.
        self.video_fps = None

          # Indique si le test micro est actuellement actif.
        self.micro_test_is_running = False

        # Source audio Qt utilisée pour lire le flux du micro.
        self.audio_source = None

        # Flux de lecture retourné par QAudioSource.start().
        self.audio_io_device = None

        # Format audio réellement utilisé pendant le test.
        self.audio_format = None

        # Timer qui permet de lire régulièrement le niveau du micro.
        self.micro_level_timer = QTimer()
        self.micro_level_timer.setInterval(50)
        self.micro_level_timer.timeout.connect(self.process_micro_level)


    def setup(self):
        """
        Prépare toute la partie multimédia.

        Cette méthode permet à MyWindow d'appeler une seule méthode
        au lieu d'appeler séparément toutes les étapes.
        """

        # Charge la liste des micros.
        self.load_microphones()

        # Charge la liste des caméras.
        self.load_cameras()

        # Prépare la zone de preview vidéo.
        self.setup_camera_preview()

        # Lance la preview si une caméra est disponible.
        self.start_camera_preview()

        # Prépare l'enregistrement.
        self.setup_recording()


    # ========== CHARGEMENT DES PERIPHERIQUES ==========

    def load_microphones(self):
        """
        Charge les micros disponibles dans la ComboBox.
        """

        # Vide la ComboBox au cas où elle contient déjà des éléments
        self.select_micro.clear()

        # Récupère la liste des micros détectés par Qt
        microphones = QMediaDevices.audioInputs()
        
        # On vérifie que la liste n'est pas vide
        if microphones :
            # Vérification de audioInput
            if self.audio_input is None :
                # Crée un objet QAudioInput à partir du premier micro détecté
                self.audio_input = QAudioInput(microphones[0])
        else :
            print("Aucun micro détecté")

        # Pour chaque micro trouvé
        for micro in microphones:
            # description() = nom lisible affiché à l'utilisateur
            # micro = objet technique stocké en donnée cachée
            self.select_micro.addItem(micro.description(), micro)


    def load_cameras(self):
        """
        Charge les caméras disponibles dans la ComboBox.
        """

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
    
    # -----------------------------------------------------------------


    # ========== RECUPERATION DES PERIPHERIQUES SELECTIONNES ==========

    def get_selected_microphone(self):
        """
        Retourne le micro actuellement sélectionné.
        """

        return self.select_micro.currentData()


    def get_selected_camera(self):
        """
        Retourne la caméra actuellement sélectionnée.
        """

        return self.select_camera.currentData()


    def has_selected_microphone(self):
        """
        Indique si un micro est sélectionné.
        """

        return self.get_selected_microphone() is not None

    def has_selected_camera(self):
        """
        Indique si une caméra est sélectionnée.
        """

        return self.get_selected_camera() is not None
    
    # -----------------------------------------------------------------


    # ========== REFRESH DES PERIPHERIQUES ==========

    def refresh_microphones(self):
        """
        Recharge la liste des micros en essayant de conserver le micro sélectionné.
        """

        # Bloque temporairement les signaux pour éviter de déclencher micro_changed()
        # pendant le clear(), les addItem() et le setCurrentIndex().
        self.select_micro.blockSignals(True)

        # Valeur par défaut si aucun micro n'était sélectionné avant le refresh.
        current_micro_id = None

        # Récupère le micro actuellement sélectionné avant de recharger la liste.
        current_micro = self.get_selected_microphone()

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
                self.audio_input = QAudioInput(selected_micro)
                self.capture_session.setAudioInput(self.audio_input) # type: ignore

        # S'il n'y a plus aucun micro disponible, on vide l'objet audio.
        elif self.select_micro.count() == 0:
            self.audio_input = None

        # Réactive les signaux après la mise à jour automatique.
        self.select_micro.blockSignals(False)


    def refresh_cameras(self):
        """
        Recharge la liste des caméras en essayant de conserver la caméra sélectionnée.
        """

        # Bloque temporairement les signaux pour éviter de déclencher camera_changed()
        # pendant le clear(), les addItem() et le setCurrentIndex().
        self.select_camera.blockSignals(True)

        # Valeur par défaut si aucune caméra n'était sélectionnée avant le refresh.
        current_camera_id = None

        # Récupère la caméra actuellement sélectionnée avant de recharger la liste.
        current_camera = self.get_selected_camera()

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

                # Crée la nouvelle caméra active.
                self.camera = QCamera(selected_camera)

                # Configure son format.
                self.configure_camera_format(selected_camera)

                # Relance la preview avec la nouvelle caméra.
                self.start_camera_preview()

        # S'il n'y a plus aucune caméra disponible, on arrête et vide la caméra active.
        elif self.select_camera.count() == 0:
            if self.camera is not None:
                self.camera.stop()

            self.camera = None

        # Réactive les signaux après la mise à jour automatique.
        self.select_camera.blockSignals(False)

    # -----------------------------------------------------------------


    # ========== CHANGEMENT DE MICRO ET CAMERA ==========

    def change_microphone(self, _):
        """
        Applique le micro actuellement sélectionné dans la ComboBox.

        Le paramètre _ permet d'accepter l'index envoyé par currentIndexChanged.
        """

        if self.get_selected_microphone() is not None:
            print("Changement de micro :", self.get_selected_microphone().description())

            # Crée un nouvel objet QAudioInput.
            self.audio_input = QAudioInput(self.get_selected_microphone())

            # Branchement du micro à la session.
            self.capture_session.setAudioInput(self.audio_input) # type: ignore
    

    def change_camera(self, _):
        """
        Applique la caméra actuellement sélectionnée dans la ComboBox.

        Le paramètre _ permet d'accepter l'index envoyé par currentIndexChanged.
        """

        if self.get_selected_camera() is not None:
            print("Changement de caméra : ", self.get_selected_camera().description())

            # Stoppe l'ancienne caméra avant d'en créer une nouvelle.
            if self.camera is not None:
                self.camera.stop()

            # Crée la nouvelle caméra.
            self.camera = QCamera(self.get_selected_camera())

            # Configure son format.
            self.configure_camera_format(self.get_selected_camera())

            # Lance la preview avec la nouvelle caméra.
            self.start_camera_preview()
    
    # -----------------------------------------------------------------


    # ========== CHOIX AUTOMATIQUE DE LA QUALITE CAMERA ==========

    def configure_camera_format(self, camera_device):
        """
        Choisit automatiquement le meilleur format caméra disponible.

        Critères :
            1. au moins 30 FPS si possible ;
            2. meilleure résolution ;
            3. FPS le plus élevé.
        """

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

        # Sélectionne le meilleur format selon le score défini dans media_utils.py.
        best_format = max(formats, key=get_camera_format_score)

        # Sélectionne le format ayant le meilleur score selon les critères ci-dessus.
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

        self.video_width = best_width
        self.video_height = best_height
        self.video_fps = best_fps

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

    # -----------------------------------------------------------------


    # ========== PREVIEW CAMERA ==========

    def setup_camera_preview(self):
        """
        Prépare la zone de preview caméra.
        """

        # Crée le widget vidéo qui affichera le retour caméra
        self.video_widget = QVideoWidget()

        # Remplit la zone de preview en elevant les bandes noires
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)

        # Crée un layout dans le QWidget vide créé dans Designer
        layout = QVBoxLayout(self.area_preview)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Ajoute le widget vidéo dans le layout
        layout.addWidget(self.video_widget)

        # Cette session servira à relier la caméra, le micro, la preview et le recorder
        self.capture_session = QMediaCaptureSession()

        # Branche la sortie vidéo au QVideoWidget
        self.capture_session.setVideoOutput(self.video_widget)


    def start_camera_preview(self):
        """
        Lance le retour vidéo de la caméra.
        """

        # Si aucune caméra n'est disponible, on ne peut pas lancer la preview
        if self.camera is None:
            print("Aucune caméra disponible pour la preview")
            return

        # Branche la caméra à la session de capture
        self.capture_session.setCamera(self.camera) # type: ignore

        # Lance le retour caméra (flux vidéo)
        self.camera.start()

    # -----------------------------------------------------------------


    # ========== FORMAT ET PARAMETRES D'ENREGISTREMENT ==========
    
    def apply_recorder_bitrates(self):
        """
        Applique les débits audio et vidéo au recorder.
        """

        # On force un encodage piloté par le débit avant de définir le bitrate.
        self.recorder.setEncodingMode(QMediaRecorder.EncodingMode.ConstantBitRateEncoding) # type: ignore

        # Pour éviter que Qt choisisse automatiquement un débit trop faible,
        # on utilise le débit calculé selon la résolution de la caméra.
        self.recorder.setVideoBitRate(self.video_bitrate) # type: ignore

        # Définit le débit audio AAC.
        self.recorder.setAudioBitRate(self.audio_bitrate) # type: ignore

    # -----------------------------------------------------------------


    # ========== ENREGISTREMENT ==========

    def setup_recording(self) :
        """
        Prépare le QMediaRecorder et le connecte à la session de capture.
        """

        # Création de l’objet responsable de l’enregistrement
        self.recorder = QMediaRecorder()

        # Premier choix : H264, car il est plus adapté au MP4 et plus efficace que MPEG4.
        media_format = create_recording_media_format(QMediaFormat.VideoCodec.H264)
        self.recorder.setMediaFormat(media_format)
        print("Codec vidéo demandé :", self.recorder.mediaFormat().videoCodec().name)

        # Applique les bitrates vidéo/audio.
        self.apply_recorder_bitrates()

        # Surveille les erreurs d'encodage.
        # Si H264 échoue au moment de record(), on relancera automatiquement en MPEG4.
        self.recorder.errorOccurred.connect(self.recorder_error_occurred)

        # Branche le recorder à la session multimédia.
        self.capture_session.setRecorder(self.recorder) # type: ignore

        # Si un micro existe, on le branche à la session
        if self.audio_input is not None:
            self.capture_session.setAudioInput(self.audio_input) # type: ignore
        else:
            print("Aucun micro disponible")      


    def start_recording(self, language_code):
        """
        Démarre l'enregistrement audio/vidéo.

        Paramètre :
            language_code : code langue, par exemple "fr" ou "en".
        """

        # Construit le nom de fichier et le chemin complet.
        self.file_name, self.video_filepath, self.annotation_filepath, self.video_filepath_rel, self.annotation_filepath_rel = build_recording_filepaths(CONFIG["paths"]["data_dir"], CONFIG["paths"]["data_dir_rel"], language_code)

        # Affiche le chemin pour vérifier où la vidéo sera enregistrée
        print("Enregistrement dans :", self.video_filepath)

        # Indique la destination de l'enregistrement de la vidéo.
        self.recording_output_location = QUrl.fromLocalFile(str(self.video_filepath))
        self.recorder.setOutputLocation(self.recording_output_location) # type: ignore

        # Réinitialise le fallback pour ce nouvel enregistrement.
        self.h264_fallback_tried = False
        
        # Démarre l’enregistrement
        self.recorder.record() # type: ignore

        return True


    def stop_recording(self):
        """
        Stoppe l'enregistrement audio/vidéo.
        """
        
        # Record stoppé
        self.recorder.stop() # type: ignore

    # -----------------------------------------------------------------


    # ========== GESTION DES ERREURS ET FALLBACK CODEC ==========

    def recorder_error_occurred(self, error, error_string):
        # Affiche l'erreur remontée par Qt/FFmpeg.
        print("Erreur enregistrement :", error, error_string)

        # Si H264 échoue au démarrage, Qt peut remonter une erreur du type h264_vaapi.
        # Dans ce cas, on bascule automatiquement vers MPEG4 et on relance l'enregistrement.
        current_codec = self.recorder.mediaFormat().videoCodec() # type: ignore
        if current_codec == QMediaFormat.VideoCodec.H264 and not self.h264_fallback_tried:
            print("H264 a échoué, relance automatique en MPEG4")

            # Marque le fallback comme déjà tenté pour éviter une boucle infinie.
            self.h264_fallback_tried = True

            # Stoppe proprement le recorder avant de changer son format.
            self.recorder.stop() # type: ignore

            # Laisse un court délai à Qt pour libérer le fichier H264 raté.
            # Ensuite seulement, on supprime ce fichier et on relance en MPEG4.
            QTimer.singleShot(300, self.restart_recording_with_mpeg4)

    
    def restart_recording_with_mpeg4(self):
        # Récupère le chemin du fichier créé par la tentative H264.
        failed_filepath = self.video_filepath

        if self.video_filepath is not None:
            # Supprime le fichier H264 invalide avant de relancer l'enregistrement.
            # Si le fichier n'existe pas encore, missing_ok=True évite une erreur inutile.
            failed_filepath.unlink(missing_ok=True) # type: ignore
            print("Fichier H264 invalide supprimé :", failed_filepath)

        # Remplace le format H264 par un format MPEG4.
        media_format = create_recording_media_format(QMediaFormat.VideoCodec.MPEG4)
        self.recorder.setMediaFormat(media_format) # type: ignore
        print("Codec vidéo demandé après fallback :", self.recorder.mediaFormat().videoCodec().name) # type: ignore

        # Réapplique les bitrates après le changement de format.
        self.apply_recorder_bitrates()

        # Relance l'enregistrement vers le même chemin, maintenant propre.
        self.recorder.setOutputLocation(self.recording_output_location) # type: ignore
        self.recorder.record() # type: ignore
    
    # -----------------------------------------------------------------

    # ========== TEST MICRO ==========
    def start_micro_test(self, audio_device):
        """
        Démarre le test du micro sélectionné.
        audio_device doit venir de select_micro.currentData().
        """

        # Si un test micro est déjà actif, on l'arrête proprement avant d'en relancer un.
        if self.micro_test_is_running:
            self.stop_micro_test()

        # Si aucun micro n'est sélectionné, on ne fait rien.
        if audio_device is None:
            self.micro_level_changed.emit(0)
            return

        # Format audio simple pour mesurer le volume.
        audio_format = QAudioFormat()
        audio_format.setSampleRate(44100)
        audio_format.setChannelCount(1)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        # Si le micro ne supporte pas ce format, on prend son format préféré.
        if not audio_device.isFormatSupported(audio_format):
            audio_format = audio_device.preferredFormat()

        # On garde le format utilisé pour savoir comment interpréter les données.
        self.audio_format = audio_format

        # Création de la source audio avec le micro sélectionné.
        self.audio_source = QAudioSource(audio_device, self.audio_format)

        # Démarre la capture audio.
        self.audio_io_device = self.audio_source.start()

        # Si Qt n'arrive pas à ouvrir le flux, on remet la barre à zéro.
        if self.audio_io_device is None:
            self.micro_level_changed.emit(0)
            return

        # Active la lecture périodique du niveau sonore.
        self.micro_level_timer.start()

        # Indique que le test micro est actif.
        self.micro_test_is_running = True

    
    def stop_micro_test(self):
        """
        Arrête proprement le test micro.
        """

        # Arrête le timer de mesure.
        self.micro_level_timer.stop()

        # Arrête la source audio si elle existe.
        if self.audio_source is not None:
            self.audio_source.stop()
            self.audio_source = None

        # Nettoie les références.
        self.audio_io_device = None
        self.audio_format = None

        # Indique que le test micro n'est plus actif.
        self.micro_test_is_running = False

        # Remet la barre à zéro.
        self.micro_level_changed.emit(0)


    def process_micro_level(self):
        """
        Lit les données audio disponibles et calcule le niveau du micro.
        """

        # Si le flux audio n'existe pas, on quitte.
        if self.audio_io_device is None:
            return

        # Nombre d'octets actuellement disponibles dans le flux.
        bytes_available = self.audio_io_device.bytesAvailable()

        # S'il n'y a rien à lire, on quitte.
        if bytes_available <= 0:
            return

        # Lecture des données audio brutes.
        audio_data = self.audio_io_device.read(bytes_available)

        # Si aucune donnée n'a été lue, on quitte.
        if not audio_data:
            return

        # Calcule un niveau entre 0 et 100.
        level = self.calculate_audio_level(audio_data)

        # Envoie le niveau à l'interface.
        self.micro_level_changed.emit(level)
    
    
    def calculate_audio_level(self, audio_data):
        """
        Calcule un niveau sonore de 0 à 100 à partir de données audio Int16.
        """

        # On part sur des échantillons Int16, donc 2 octets par échantillon.
        sample_count = len(audio_data) // 2

        # S'il n'y a pas assez de données, le niveau est nul.
        if sample_count == 0:
            return 0

        # On tronque les données pour éviter un nombre impair d'octets.
        usable_audio_data = audio_data[:sample_count * 2]

        # Conversion des octets en entiers signés 16 bits.
        samples = struct.unpack("<" + "h" * sample_count, usable_audio_data)

        # Calcul du RMS, qui représente mieux le volume moyen qu'un simple pic.
        square_sum = 0

        for sample in samples:
            square_sum += sample * sample

        rms = math.sqrt(square_sum / sample_count)

        # Valeur maximale possible pour un échantillon Int16.
        max_int16 = 32767

        # Conversion en pourcentage.
        level = int((rms / max_int16) * 100)

        # Sécurité : on limite entre 0 et 100.
        level = max(0, min(level, 100))

        return level
    
    # -----------------------------------------------------------------

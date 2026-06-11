import csv
import platform
import socket
from datetime import datetime
from acquisition.media_manager import MediaManager
from acquisition.corpus_manager import CorpusManager

from utils.media_utils import extract_video_metadata

class MetadataManager:
    """
    Gère l'écriture des metadonnées associées aux vidéos enregistrées.
    """

    def __init__(self):
        """
        Initialise le gestionnaire de métadonnées.
        """

        # Nom de la machine utilisée pour les enregistrements.
        self.machine_name = socket.gethostname()

        # Système d'exploitation utilisé.
        self.operating_system = platform.system()

        # Colonnes du fichier CSV.
        self.fieldnames = [
            "file_name",
            "machine_name",
            "operating_system",
            "user_firstname",
            "video_path_abs",
            "video_path_rel",
            "metadata_file_path_abs",
            "metadata_file_path_rel",
            "video_format",
            "camera_name",
            "microphone_name",
            "duration_seconds",
            "video_codec",
            "video_width",
            "video_height",
            "video_fps",
            "video_bitrate",
            "audio_codec",
            "audio_sample_rate",
            "audio_channels",
            "audio_bitrate",
            "language_code",
            "language_name",
            "whisper_code",
            "sentence_display",
            "sentence_with_digit",
            "template_type",
            "recorded_at",
            "checksum_sha256"
        ]


    def save_recording_metadata(
        self,
        media_manager: MediaManager,
        corpus_manager: CorpusManager,
        user_firstname
    ):
        """
        Prépare les données de l'enregistrement courant et sauvegarde l'metadata.

        Paramètres :
            media_manager : gestionnaire multimédia de l'application.
            corpus_manager : gestionnaire du corpus de phrases.
            user_firstname : prénom de l'utilisateur qui réalise l'enregistrement.
        """

        # Informations produites par MediaManager pendant l'enregistrement.
        file_name = media_manager.file_name
        video_path_abs = media_manager.video_filepath
        video_path_rel = media_manager.video_filepath_rel
        metadata_file_path_abs = media_manager.metadata_filepath
        metadata_file_path_rel = media_manager.metadata_filepath_rel

        # Informations du corpus correspondant à la phrase qui vient d'être lue.
        sentence_display = corpus_manager.current_sentence
        sentence_with_digit = corpus_manager.sentence_with_digit
        template_type = corpus_manager.current_template_type
        language_code = corpus_manager.language_selected[1] # type: ignore
        language_name = corpus_manager.language_selected[0] # type: ignore
        whisper_code = corpus_manager.language_selected[2] # type: ignore

        # Périphériques utilisés pour l'enregistrement.
        selected_camera = media_manager.get_selected_camera()
        selected_microphone = media_manager.get_selected_microphone()
        camera_name = selected_camera.description() if selected_camera is not None else "unknown"
        microphone_name = selected_microphone.description() if selected_microphone is not None else "unknown"

        # Métadonnées réelles du fichier vidéo écrit sur disque.
        video_metadata = extract_video_metadata(media_manager.video_filepath)

        # Écriture de la ligne CSV avec les données préparées.
        self.save_metadata(
            metadata_file_path_abs,
            metadata_file_path_rel,
            file_name,
            video_path_abs,
            video_path_rel,
            language_code,
            language_name,
            whisper_code,
            sentence_display,
            sentence_with_digit,
            template_type,
            camera_name,
            microphone_name,
            video_metadata["video_format"],
            video_metadata["duration_seconds"],
            video_metadata["video_codec"],
            video_metadata["video_width"],
            video_metadata["video_height"],
            video_metadata["video_fps"],
            video_metadata["video_bitrate"],
            video_metadata["audio_codec"],
            video_metadata["audio_sample_rate"],
            video_metadata["audio_channels"],
            video_metadata["audio_bitrate"],
            video_metadata["checksum_sha256"],
            user_firstname
        )
    

    def save_metadata(
        self,
        metadata_file_path_abs,
        metadata_file_path_rel,
        file_name,
        video_path_abs,
        video_path_rel,
        language_code,
        language_name,
        whisper_code,
        sentence_display,
        sentence_with_digit,
        template_type,
        camera_name,
        microphone_name,
        video_format,
        duration_seconds,
        video_codec,
        video_width,
        video_height,
        video_fps,
        video_bitrate,
        audio_codec,
        audio_sample_rate,
        audio_channels,
        audio_bitrate,
        checksum_sha256,
        user_firstname
    ):
    
        """
        Ajoute les métadonnées d’un enregistrement dans un fichier CSV.

        Paramètres :
            metadata_file_path_abs : chemin absolu du fichier CSV de métadonnées.
            metadata_file_path_rel : chemin relatif du fichier CSV de métadonnées.

            file_name : nom du fichier vidéo sans extension.
            video_path_abs : chemin absolu de la vidéo enregistrée.
            video_path_rel : chemin relatif de la vidéo enregistrée.
            checksum_sha256 : empreinte SHA-256 calculée à partir du contenu du fichier vidéo.

            whisper_code : code de langue utilisé par Whisper pour la transcription.
            language_code : code interne de la langue, par exemple "fr" ou "en".
            language_name : nom lisible de la langue, par exemple "Français" ou "Anglais".

            sentence_display : phrase affichée à l’utilisateur dans l’interface.
            sentence_with_digit : phrase normalisée avec les nombres en chiffre,
            template_type : template utilisé pour générer ou sélectionner la phrase,
                par exemple "template_1" ou "template_2".

            camera_name : nom de la caméra utilisée pour l’enregistrement.
            microphone_name : nom du microphone utilisé pour l’enregistrement.

            video_format : format ou conteneur détecté dans le fichier vidéo.
            duration_seconds : durée réelle de la vidéo en secondes.

            video_codec : codec vidéo réellement utilisé dans le fichier.
            video_width : largeur réelle de la vidéo en pixels.
            video_height : hauteur réelle de la vidéo en pixels.
            video_fps : nombre d’images par seconde réel ou moyen de la vidéo.
            video_bitrate : débit vidéo réel du fichier.

            audio_codec : codec audio réellement utilisé dans le fichier.
            audio_sample_rate : fréquence d’échantillonnage audio, par exemple 48000 Hz.
            audio_channels : nombre de canaux audio, par exemple 1 pour mono ou 2 pour stéréo.
            audio_bitrate : débit audio réel du fichier.

            machine_name : nom de la machine utilisée pour l’enregistrement.
            operating_system : système d’exploitation utilisé pour l’enregistrement.
            user_firstname : prénom de l’utilisateur ayant lancé l’application.
        """
        
        # Vérifie si le fichier CSV existe déjà.
        file_exists = metadata_file_path_abs.exists()

        # Ouvre le fichier en mode ajout.
        # newline="" évite les lignes vides en trop dans les fichiers CSV.
        with open(metadata_file_path_abs, "a", encoding="utf-8", newline="") as csv_file:
            
            # Crée un writer CSV basé sur les noms de colonnes.
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            
            # Si le fichier n'existait pas, on écrit d'abord l'en-tête.
            if not file_exists:
                writer.writeheader()
            
            # Écrit une nouvelle ligne d'metadata.
            writer.writerow({
                "file_name": file_name,
                "user_firstname": user_firstname,
                "machine_name": self.machine_name,
                "operating_system": self.operating_system,
                "video_path_abs": str(video_path_abs),
                "video_path_rel": str(video_path_rel),
                "metadata_file_path_abs": str(metadata_file_path_abs),
                "metadata_file_path_rel": str(metadata_file_path_rel),
                "video_format": video_format,
                "camera_name": camera_name,
                "microphone_name": microphone_name,
                "duration_seconds": duration_seconds,
                "video_codec": video_codec,
                "video_width": video_width,
                "video_height": video_height,
                "video_fps": video_fps,
                "video_bitrate": video_bitrate,
                "audio_codec": audio_codec,
                "audio_sample_rate": audio_sample_rate,
                "audio_channels": audio_channels,
                "audio_bitrate": audio_bitrate,
                "language_code": language_code,
                "language_name" : language_name,
                "whisper_code" : whisper_code,
                "sentence_display": sentence_display,
                "sentence_with_digit": sentence_with_digit,
                "template_type": template_type,
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "checksum_sha256": checksum_sha256
            })

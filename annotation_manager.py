import csv, socket, platform
from datetime import datetime

class AnnotationManager:
    """
    Gère l'écriture des annotations associées aux vidéos enregistrées.
    """

    def __init__(self):
        """
        Initialise le gestionnaire d'annotations.
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
            "video_path",
            "file_path",
            "file_size_bytes",
            "format_name",
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
            "sentence",
            "template_type",
            "recorded_at"
            "status"
        ]
    
    def save_annotation(
        self,
        annotation_file_path,
        file_name,
        video_path,
        language_code,
        language_name,
        sentence,
        template_type,
        camera_name,
        microphone_name,
        file_size_bytes,
        format_name,
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
        status="recorded",
    ):
        """
        Ajoute une annotation dans le fichier CSV.

        Paramètres :
            annotation_file_path : chemin du fichier CSV d'annotation à créer ou compléter.
            file_name : nom du fichier vidéo sans extension.
            video_path : chemin de la vidéo enregistrée.
            language_code : code de la langue, par exemple "fr" ou "en".
            language_name : nom lisible de la langue, par exemple "Français" ou "Anglais".
            sentence : phrase affichée et lue par l'utilisateur.
            template_type : template utilisé, par exemple "template_1" ou "template_2".

            camera_name : nom de la caméra utilisée pour l'enregistrement.
            microphone_name : nom du micro utilisé pour l'enregistrement.

            file_size_bytes : taille réelle du fichier vidéo en octets.
            format_name : format/conteneur détecté dans le fichier vidéo.
            duration_seconds : durée réelle de la vidéo en secondes.

            video_codec : codec vidéo réellement utilisé dans le fichier.
            video_width : largeur réelle de la vidéo en pixels.
            video_height : hauteur réelle de la vidéo en pixels.
            video_fps : nombre d'images par seconde réel ou moyen de la vidéo.
            video_bitrate : débit vidéo réel du fichier.

            audio_codec : codec audio réellement utilisé dans le fichier.
            audio_sample_rate : fréquence d'échantillonnage audio, par exemple 48000 Hz.
            audio_channels : nombre de canaux audio, par exemple 1 ou 2.
            audio_bitrate : débit audio réel du fichier.

            status : état de l'enregistrement, par défaut "recorded".
            machine_name : nom de la machine utilisée pour l'enregistrement.
            operating_system : système d'exploitation utilisé pour l'enregistrement.
        """
        
        # Vérifie si le fichier CSV existe déjà.
        file_exists = annotation_file_path.exists()

        # Ouvre le fichier en mode ajout.
        # newline="" évite les lignes vides en trop dans les fichiers CSV.
        with open(annotation_file_path, "a", encoding="utf-8", newline="") as csv_file:
            
            # Crée un writer CSV basé sur les noms de colonnes.
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            
            # Si le fichier n'existait pas, on écrit d'abord l'en-tête.
            if not file_exists:
                writer.writeheader()
            
            # Écrit une nouvelle ligne d'annotation.
            writer.writerow({
                "file_name": file_name,
                "machine_name": self.machine_name,
                "operating_system": self.operating_system,
                "video_path": video_path,
                "file_path": str(annotation_file_path),
                "file_size_bytes": file_size_bytes,
                "format_name": format_name,
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
                "sentence": sentence,
                "template_type": template_type,
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
            })
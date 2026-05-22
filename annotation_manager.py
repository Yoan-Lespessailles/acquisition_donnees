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

        # Colonnes du fichier CSV.
        self.fieldnames = [
            "file_name",
            "machine_name",
            "operating_system",
            "camera_name",
            "microphone_name",
            "video_path",
            "video_width",
            "video_height",
            "video_fps",
            "video_bitrate",
            "audio_bitrate",
            "language_code",
            "language_name",
            "sentence",
            "template_type",
            "recorded_at",
            "status",
        ]
    
    def save_annotation(
        self,
        annotation_file_path,
        file_name,
        language_code,
        language_name,
        sentence,
        template_type,
        camera_name,
        microphone_name,
        video_path,
        video_width,
        video_height,
        video_fps,
        video_bitrate,
        audio_bitrate,
        status="recorded",
        machine_name = socket.gethostname(),
        operating_system = platform.system(),
    ):
        """
        Ajoute une annotation dans le fichier CSV.

        Paramètres :
            annotation_file_path : chemin du fichier annotations.csv.
            file_name : nom du fichier vidéo sans extension.
            video_path : chemin de la vidéo enregistrée.
            language_code : code de langue, par exemple "fr" ou "en".
            sentence : phrase affichée et lue par l'utilisateur.
            template_type : template utilisé, par exemple "template_1" ou "template_2".
            speaker_name : nom ou identifiant de la personne enregistrée.
            status : état de l'enregistrement, par défaut "recorded".
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
                "machine_name": machine_name,
                "operating_system": operating_system,
                "video_path": video_path,
                "camera_name": camera_name,
                "microphone_name": microphone_name,
                "video_width": video_width,
                "video_height": video_height,
                "video_fps": video_fps,
                "video_bitrate": video_bitrate,
                "audio_bitrate": audio_bitrate,
                "language_code": language_code,
                "language_name" : language_name,
                "sentence": sentence,
                "template_type": template_type,
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
            })
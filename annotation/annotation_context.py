from pathlib import Path


class AnnotationContext:
    def __init__(self, language_code, data_dir):
        
        self.language_code = language_code.lower()
        self.data_dir = data_dir

        self.language_dir = Path()
        self.videos_dir = Path()
        self.metadatas_dir = Path()

        self.video_files = []
        self.metadata_files = []

        self.build_paths()


    def build_paths(self):    
        # Construit le chemin du dossier de langue
        self.language_dir = self.data_dir / self.language_code

        # Construit le chemin du dossier vidéo
        self.videos_dir = self.language_dir / "videos"

        # construit le chemin du dossier annotations
        self.metadatas_dir = self.language_dir / "annotations"

    def validate_paths(self):
        # Vérifie que le dossier de langue existe.
        if not self.language_dir.is_dir():
            raise FileNotFoundError(f"Dossier de langue introuvable : {self.language_dir}")

        # Vérifie que le dossier des vidéos existe.
        if not self.videos_dir.is_dir():
            raise FileNotFoundError(f"Dossier vidéos introuvable : {self.videos_dir}")

        # Vérifie que le dossier des annotations existe.
        if not self.metadatas_dir.is_dir():
            raise FileNotFoundError(f"Dossier annotations introuvable : {self.metadatas_dir}")

        return True

        
    def load_file_list(self) :
        for video_file in self.videos_dir.glob(f"{self.language_code}*.mp4"):
            self.video_files.append(Path(video_file))

        for annotation_file in self.metadatas_dir.glob(f"{self.language_code}*.csv"):
            self.metadata_files.append(Path(annotation_file))
    

    def display_files(self):
        for video_file in self.video_files :
            print(video_file)

        for annotation_file in self.metadata_files :
            print(annotation_file)
from pathlib import Path


class AnnotationContext:
    def __init__(self, language_code, data_dir):
        
        self.language_code = language_code.lower()
        self.data_dir = data_dir

        self.language_dir = Path()
        self.videos_dir = Path()
        self.metadata_dir = Path()

        self.video_files = []
        self.metadata_files = []

        self.build_paths()


    def build_paths(self):    
        # Construit le chemin du dossier de langue
        self.language_dir = self.data_dir / self.language_code

        # Construit le chemin du dossier video
        self.videos_dir = self.language_dir / "videos"

        # construit le chemin du dossier metadata
        self.metadata_dir = self.language_dir / "metadata"

    def validate_paths(self):
        # Vérifie que le dossier de langue existe
        if not self.language_dir.is_dir():
            raise FileNotFoundError(f"Dossier de langue introuvable : {self.language_dir}")

        # Vérifie que le dossier des vidéos existe
        if not self.videos_dir.is_dir():
            raise FileNotFoundError(f"Dossier vidéos introuvable : {self.videos_dir}")

        # Vérifie que le dossier de métadonnées existe
        if not self.metadata_dir.is_dir():
            raise FileNotFoundError(f"Dossier metadata introuvable : {self.metadata_dir}")

        return True

        
    def load_file_list(self) :
        for video_file in self.videos_dir.glob(f"{self.language_code}*.mp4"):
            self.video_files.append(Path(video_file))

        for metadata_file in self.metadata_dir.glob(f"{self.language_code}*.csv"):
            self.metadata_files.append(Path(metadata_file))
    

    def display_files(self):
        for video_file in self.video_files :
            print(video_file)

        for metadata_file in self.metadata_files :
            print(metadata_file)
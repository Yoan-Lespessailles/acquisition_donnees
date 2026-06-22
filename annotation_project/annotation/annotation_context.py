from pathlib import Path


class AnnotationContext:
    """
    Regroupe les informations nécessaires au traitement d'une langue donnée.

    Cette classe centralise :
        - le code de langue demandé ;
        - le dossier principal des données ;
        - les chemins vers les dossiers de vidéos et de métadonnées ;
        - les listes des fichiers vidéo et metadata trouvés.
    """


    def __init__(self, language_code, data_dir):
        """
        Initialise le contexte d'annotation pour une langue.

        Paramètres :
            language_code (str) : code de la langue à traiter, par exemple "fr", "en" ou "it".
            data_dir (Path | str) : dossier racine contenant les données.

        Retourne :
            None
        """

        # Normalise le code langue en minuscules pour éviter les différences du type "FR" / "fr"
        self.language_code = language_code.lower()

        # Stocke le dossier racine contenant les données
        self.data_dir = Path(data_dir)

        # Initialise les chemins principaux avec des objets Path vides
        self.language_dir = Path()
        self.videos_dir = Path()
        self.metadata_dir = Path()

        # Initialise les listes qui contiendront les fichiers trouvés
        self.video_files = []
        self.metadata_files = []

        # Construit immédiatement les chemins utiles à partir du dossier racine et du code langue
        self.build_paths()


    def build_paths(self):
        """
        Construit les chemins des dossiers utilisés pour une langue donnée.

        Les chemins construits sont :
            - le dossier de langue ;
            - le dossier contenant les vidéos ;
            - le dossier contenant les fichiers de métadonnées.

        Retourne :
            None
        """

        # Construit le chemin du dossier de langue
        # Exemple : data/fr
        self.language_dir = self.data_dir / self.language_code

        # Construit le chemin du dossier contenant les vidéos
        # Exemple : data/fr/videos
        self.videos_dir = self.language_dir / "videos"

        # Construit le chemin du dossier contenant les fichiers de métadonnées
        # Exemple : data/fr/metadata
        self.metadata_dir = self.language_dir / "metadata"


    def validate_paths(self):
        """
        Vérifie que les dossiers nécessaires au traitement existent.

        Une erreur est levée si :
            - le dossier de langue est introuvable ;
            - le dossier des vidéos est introuvable ;
            - le dossier des métadonnées est introuvable.

        Retourne :
            bool : True si tous les dossiers existent.

        Exceptions :
            FileNotFoundError : si l'un des dossiers attendus est introuvable.
        """

        # Vérifie que le dossier associé à la langue existe
        if not self.language_dir.is_dir():
            raise FileNotFoundError(f"Dossier de langue introuvable : {self.language_dir}")

        # Vérifie que le dossier contenant les vidéos existe
        if not self.videos_dir.is_dir():
            raise FileNotFoundError(f"Dossier vidéos introuvable : {self.videos_dir}")

        # Vérifie que le dossier contenant les métadonnées existe
        if not self.metadata_dir.is_dir():
            raise FileNotFoundError(f"Dossier metadata introuvable : {self.metadata_dir}")

        return True


    def load_file_list(self):
        """
        Charge la liste des fichiers vidéo et des fichiers de métadonnées disponibles.

        Les fichiers sont filtrés à partir du code langue :
            - vidéos : fichiers .mp4 commençant par le code langue ;
            - métadonnées : fichiers .csv commençant par le code langue.

        Exemple :
            Pour language_code = "fr" :
                fr_20260602_092105.mp4
                fr_20260602_092105.csv

        Retourne :
            None
        """

        # Vide les listes avant le chargement pour éviter les doublons si la méthode est appelée plusieurs fois
        self.video_files.clear()
        self.metadata_files.clear()

        # Recherche les vidéos dont le nom commence par le code langue
        for video_file in self.videos_dir.glob(f"{self.language_code}*.mp4"):
            self.video_files.append(Path(video_file))

        # Recherche les fichiers metadata dont le nom commence par le code langue
        for metadata_file in self.metadata_dir.glob(f"{self.language_code}*.csv"):
            self.metadata_files.append(Path(metadata_file))


    def display_files(self):
        """
        Affiche dans le terminal les fichiers vidéo et metadata chargés.

        Cette méthode sert surtout au contrôle manuel ou au debug.

        Retourne :
            None
        """

        # Affiche les fichiers vidéo trouvés
        for video_file in self.video_files:
            print(video_file)

        # Affiche les fichiers de métadonnées trouvés
        for metadata_file in self.metadata_files:
            print(metadata_file)
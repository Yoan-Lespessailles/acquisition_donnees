import re
import subprocess

from pathlib import Path

from annotation.metadata_reader import csv_reader


class MfaManager:
    """
    Gère la préparation des fichiers d'entrée MFA et le lancement des commandes MFA.

    Logique générale :
        1. Récupérer les paires vidéo / métadonnées validées

        2. Pour chaque vidéo, préparer les fichiers attendus par MFA :
           - un fichier .wav contenant l'audio extrait de la vidéo
           - un fichier .lab contenant la phrase attendue

        3. Stocker ces fichiers dans :
           results/<code_langue>/mfa/input/

        4. Lancer mfa validate pour vérifier que :
           - les fichiers audio sont lisibles
           - les fichiers .lab sont présents
           - les mots sont connus du dictionnaire
           - le modèle acoustique est compatible

        5. Lancer mfa align pour produire les fichiers TextGrid contenant le découpage par mots et par phones

        6. Stocker les fichiers TextGrid dans :
           results/<code_langue>/mfa/aligned/
    """

    def __init__(
        self,
        valid_pairs,
        results_dir,
        language_code,
        dictionary_path,
        acoustic_model,
    ):
        """
        Initialise le gestionnaire MFA.

        Paramètres :
            valid_pairs : liste des paires valides [(video_path, metadata_path), ...]
            results_dir : dossier racine des résultats
            language_code : code de la langue traitée, par exemple "fr"
            dictionary_path : chemin vers un dictionnaire personnalisé MFA
                ou nom d'un dictionnaire MFA installé
            acoustic_model : nom du modèle acoustique MFA à utiliser
        """

        # Stocke les paires vidéo / métadonnées valides
        self.valid_pairs = valid_pairs

        # Stocke le dossier racine des résultats
        self.results_dir = Path(results_dir)

        # Stocke le code de langue
        self.language_code = language_code

        # Stocke le dictionnaire MFA
        # Soit c'est un chemin local ou alors le nom d'un dictionnaire MFA installé
        self.dictionary_path = dictionary_path

        # Stocke le nom du modèle acoustique MFA
        self.acoustic_model = acoustic_model

        # Dossier contenant les fichiers préparés pour MFA
        # Exemple : results/fr/mfa/input/
        self.mfa_input_dir = (
            self.results_dir / self.language_code / "mfa" / "input"
        )

        # Dossier contenant les résultats produits par MFA
        # Exemple : results/fr/mfa/aligned/
        self.mfa_aligned_dir = (
            self.results_dir / self.language_code / "mfa" / "aligned"
        )

    def normalize_sentence_for_mfa(self, sentence):
        """
        Normalise une phrase pour MFA.

        La phrase est mise en minuscules et la ponctuation simple est retirée.
        Les apostrophes et les tirets sont conservés pour les formes comme :
            d'après
            l'étang
            l'arc-en-ciel
        """

        # Met la phrase en minuscules
        sentence = sentence.lower()

        # Remplace les apostrophes typographiques par des apostrophes simples
        sentence = sentence.replace("’", "'")

        # Supprime la ponctuation qui ne doit pas devenir un mot MFA
        sentence = re.sub(r"[.,;:!?«»\"]", "", sentence)

        # Remplace les espaces multiples par un seul espace
        sentence = re.sub(r"\s+", " ", sentence)

        return sentence.strip()

    def prepare_mfa_input(self):
        """
        Prépare les fichiers d'entrée MFA.

        Pour chaque paire vidéo / metadata :
            - extrait l'audio de la vidéo en .wav
            - écrit la phrase attendue dans un fichier .lab

        Si un fichier .wav ou .lab portant le même nom existe déjà,
        il est remplacé.
        """

        # Crée le dossier d'entrée MFA si nécessaire
        self.mfa_input_dir.mkdir(parents=True, exist_ok=True)

        for media_path, metadata_path in self.valid_pairs:
            media_path = Path(media_path)
            metadata_path = Path(metadata_path)

            # Lit les métadonnées associées à la vidéo
            metadata = csv_reader(metadata_path)

            # Récupère le nom du fichier sans extension
            file_stem = media_path.stem

            # Définit les chemins des fichiers d'entrée MFA
            wav_path = self.mfa_input_dir / f"{file_stem}.wav"
            lab_path = self.mfa_input_dir / f"{file_stem}.lab"

            # Supprime l'ancien fichier WAV s'il existe déjà
            if wav_path.exists():
                wav_path.unlink()

            # Supprime l'ancien fichier LAB s'il existe déjà
            if lab_path.exists():
                lab_path.unlink()

            # Extrait l'audio de la vidéo en WAV mono 16 kHz
            self.extract_audio_to_wav(media_path, wav_path)

            # Récupère la phrase attendue
            sentence = metadata["sentence_display"]

            # Normalise la phrase pour MFA
            sentence = self.normalize_sentence_for_mfa(sentence)

            # Écrit la phrase dans le fichier .lab
            with lab_path.open("w", encoding="utf-8") as lab_file:
                lab_file.write(sentence)

    def extract_audio_to_wav(self, media_path, wav_path):
        """
        Extrait l'audio d'une vidéo vers un fichier WAV mono 16 kHz.

        Paramètres :
            media_path (Path | str) : chemin de la vidéo source
            wav_path (Path | str) : chemin du fichier WAV à générer
        """

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(media_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(wav_path),
        ]

        subprocess.run(command, check=True)

    def validate(self):
        """
        Lance la commande mfa validate sur les fichiers préparés.

        Cette étape vérifie que :
            - les fichiers audio sont lisibles
            - les fichiers .lab existent
            - les mots sont présents dans le dictionnaire
            - le modèle acoustique est compatible
        """

        # Vérifie que le dictionnaire local existe si un chemin local est utilisé
        # Si self.dictionary_path est un objet Path et si le chemin n'existe pas sur le disque
        if isinstance(self.dictionary_path, Path) and not self.dictionary_path.exists():
            raise FileNotFoundError(
                f"Dictionnaire MFA introuvable : {self.dictionary_path}"
            )

        # Prépare la commande MFA
        command = [
            "mfa",
            "validate",
            str(self.mfa_input_dir),
            str(self.dictionary_path),
            self.acoustic_model,
        ]

        # Affiche la commande pour faciliter le débogage
        print("Commande MFA validate lancée :")
        print(" ".join(command))

        # Lance MFA
        subprocess.run(command, check=True)

    def remove_existing_textgrids(self):
        """
        Supprime uniquement les anciens fichiers TextGrid correspondant
        aux vidéos en cours de traitement.

        Les autres fichiers présents dans le dossier aligned/ sont conservés.
        """

        # Crée le dossier de sortie des alignements si nécessaire
        self.mfa_aligned_dir.mkdir(parents=True, exist_ok=True)

        for media_path, metadata_path in self.valid_pairs:
            media_path = Path(media_path)

            # Construit le chemin du TextGrid attendu pour cette vidéo
            textgrid_path = self.mfa_aligned_dir / f"{media_path.stem}.TextGrid"

            # Supprime l'ancien TextGrid s'il existe déjà
            if textgrid_path.exists():
                textgrid_path.unlink()

    def align(self):
        """
        Lance l'alignement MFA.

        Cette étape produit les fichiers d'annotation finale,
        généralement au format TextGrid.
        """

        # Supprime uniquement les anciens TextGrid correspondant aux vidéos traitées
        self.remove_existing_textgrids()

        # Prépare la commande MFA
        command = [
            "mfa",
            "align",
            str(self.mfa_input_dir),
            str(self.dictionary_path),
            self.acoustic_model,
            str(self.mfa_aligned_dir),
        ]

        # Affiche la commande pour faciliter le débogage
        print("Commande MFA align lancée :")
        print(" ".join(command))

        # Lance MFA
        subprocess.run(command, check=True)

    def prepare_validate_and_align(self):
        """
        Prépare les fichiers d'entrée MFA, lance la validation,
        puis lance l'alignement final.
        """

        # Prépare les fichiers .wav et .lab
        self.prepare_mfa_input()

        # Vérifie que les fichiers et le dictionnaire sont compatibles
        self.validate()

        # Produit les annotations MFA
        self.align()

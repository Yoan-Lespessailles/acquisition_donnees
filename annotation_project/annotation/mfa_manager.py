import re
import shutil
import subprocess

from pathlib import Path

from annotation.metadata_reader import csv_reader


class MfaManager:
    """
    Gère la préparation des fichiers d'entrée MFA
    et le lancement des commandes MFA en ligne de commande.
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
            dictionary_path : chemin vers le dictionnaire personnalisé MFA
            acoustic_model : nom du modèle acoustique MFA à utiliser
        """

        # Stocke les paires vidéo / métadonnées valides.
        self.valid_pairs = valid_pairs

        # Stocke le dossier racine des résultats.
        self.results_dir = Path(results_dir)

        # Stocke le code de langue.
        self.language_code = language_code

        # Stocke le chemin du dictionnaire personnalisé.
        self.dictionary_path = Path(dictionary_path)

        # Stocke le nom du modèle acoustique MFA.
        self.acoustic_model = acoustic_model

        # Dossier contenant les fichiers préparés pour MFA.
        # Exemple : results/fr/mfa/input/
        self.mfa_input_dir = (
            self.results_dir / self.language_code / "mfa" / "input"
        )

        # Dossier contenant les résultats produits par MFA.
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

        # Met la phrase en minuscules.
        sentence = sentence.lower()

        # Remplace les apostrophes typographiques par des apostrophes simples.
        sentence = sentence.replace("’", "'")

        # Supprime la ponctuation qui ne doit pas devenir un mot MFA.
        sentence = re.sub(r"[.,;:!?«»\"]", "", sentence)

        # Remplace les espaces multiples par un seul espace.
        sentence = re.sub(r"\s+", " ", sentence)

        return sentence.strip()

    def prepare_mfa_input(self):
        """
        Prépare le dossier d'entrée MFA.

        Pour chaque paire vidéo / metadata :
            - extrait l'audio de la vidéo en .wav ;
            - écrit la phrase attendue dans un fichier .lab.
        """

        # Supprime l'ancien dossier d'entrée MFA pour éviter les fichiers périmés.
        if self.mfa_input_dir.exists():
            shutil.rmtree(self.mfa_input_dir)

        # Crée le dossier d'entrée MFA.
        self.mfa_input_dir.mkdir(parents=True, exist_ok=True)

        for media_path, metadata_path in self.valid_pairs:
            media_path = Path(media_path)
            metadata_path = Path(metadata_path)

            # Lit les métadonnées associées à la vidéo.
            metadata = csv_reader(metadata_path)

            # Récupère le nom du fichier sans extension.
            file_stem = media_path.stem

            # Définit les chemins de sortie pour MFA.
            wav_path = self.mfa_input_dir / f"{file_stem}.wav"
            lab_path = self.mfa_input_dir / f"{file_stem}.lab"

            # Extrait l'audio de la vidéo en WAV mono 16 kHz.
            self.extract_audio_to_wav(media_path, wav_path)

            # Récupère la phrase attendue.
            sentence = metadata["sentence_display"]

            # Normalise la phrase pour MFA.
            sentence = self.normalize_sentence_for_mfa(sentence)

            # Écrit la phrase dans le fichier .lab.
            with lab_path.open("w", encoding="utf-8") as lab_file:
                lab_file.write(sentence)

    def extract_audio_to_wav(self, media_path, wav_path):
        """
        Extrait l'audio d'une vidéo vers un fichier WAV mono 16 kHz.
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
            - les fichiers audio sont lisibles ;
            - les fichiers .lab existent ;
            - les mots sont présents dans le dictionnaire ;
            - le modèle acoustique est compatible.
        """

        # Vérifie que le dictionnaire personnalisé existe.
        if not self.dictionary_path.exists():
            raise FileNotFoundError(
                f"Dictionnaire MFA introuvable : {self.dictionary_path}"
            )

        # Prépare la commande MFA.
        command = [
            "mfa",
            "validate",
            str(self.mfa_input_dir),
            str(self.dictionary_path),
            self.acoustic_model,
        ]

        # Affiche la commande pour faciliter le débogage.
        print("Commande MFA validate lancée :")
        print(" ".join(command))

        # Lance MFA.
        subprocess.run(command, check=True)

    def align(self):
        """
        Lance l'alignement MFA.

        Cette étape produit les fichiers d'annotation finale,
        généralement au format TextGrid.
        """

        # Vérifie que le dictionnaire personnalisé existe.
        if not self.dictionary_path.exists():
            raise FileNotFoundError(
                f"Dictionnaire MFA introuvable : {self.dictionary_path}"
            )

        # Supprime l'ancien dossier d'alignement pour éviter les anciens résultats.
        if self.mfa_aligned_dir.exists():
            shutil.rmtree(self.mfa_aligned_dir)

        # Crée le dossier de sortie des alignements.
        self.mfa_aligned_dir.mkdir(parents=True, exist_ok=True)

        # Prépare la commande MFA.
        command = [
            "mfa",
            "align",
            str(self.mfa_input_dir),
            str(self.dictionary_path),
            self.acoustic_model,
            str(self.mfa_aligned_dir),
        ]

        # Affiche la commande pour faciliter le débogage.
        print("Commande MFA align lancée :")
        print(" ".join(command))

        # Lance MFA.
        subprocess.run(command, check=True)

    def prepare_validate_and_align(self):
        """
        Prépare les fichiers d'entrée MFA, lance la validation,
        puis lance l'alignement final.
        """

        # Prépare les fichiers .wav et .lab.
        self.prepare_mfa_input()

        # Vérifie que les fichiers et le dictionnaire sont compatibles.
        self.validate()

        # Produit les annotations MFA.
        self.align()

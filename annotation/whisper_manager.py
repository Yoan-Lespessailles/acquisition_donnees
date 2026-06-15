import whisper

from pathlib import Path

from annotation.metadata_reader import (
    csv_reader, 
    normalize_for_reading_check, 
    normalize_letters_only
)

from annotation.whisper_result_writer import (
    write_whisper_json, 
    create_pair_results_dir
)

class WhisperManager:
    def __init__(self, model, valid_pairs):
        """
        Initialise le gestionnaire Whisper.

        model :
            nom du modèle Whisper à charger.

        valid_pairs :
            liste des paires valides sous la forme :
            [(media_path, metadata_path), ...]
        """

        # Charge le modèle Whisper (par défaut : Large)
        self.model = whisper.load_model(model)

        # Stocke les paires vidéo / métadonnées valides
        self.valid_pairs = valid_pairs

        # Crée et stocke le chemin du dossier results/
        self.results_dir = self.create_results_dir()
        

    def create_results_dir(self):
        """
        Crée le dossier racine des résultats.

        Exemple :
            projet_stage/results/
        """

        # Récupère le dossier racine du projet
        base_dir = Path(__file__).resolve().parents[1]

        # Définit le dossier results à la racine du projet
        results_dir = base_dir / "results"

        # Crée le dossier s'il n'existe pas
        results_dir.mkdir(parents=True, exist_ok=True)

        return results_dir
    

    def oral_transcription(self):
        """
        Transcrit chaque paire vidéo/métadonnées avec Whisper, puis vérifie si la transcription correspond à la phrase attendue.

        La comparaison accepte deux formes :
            - la phrase affichée à l'utilisateur, généralement en toutes lettres ;
            - une variante avec certains nombres en chiffres, car Whisper peut parfois transcrire les nombres sous forme numérique.
        """

        invalid_control = []
        compliant_cpt = 0
        non_compliant_cpt = 0

        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]

            compliant = True

            # Lit les métadonnées associées à la vidéo.
            metadata = csv_reader(metadata_path)

            # Lance la transcription Whisper.
            whisper_result = self.model.transcribe(
                str(media_path),
                language = metadata["whisper_code"],
                fp16=False,
                word_timestamps=True
            )

            # Normalise la transcription produite par Whisper
            whisper_text = normalize_for_reading_check(whisper_result["text"])

            # Normalise la phrase affichée à l'utilisateur
            expected_sentence_display = normalize_for_reading_check(metadata["sentence_display"])

            # Normalise la variante utilisée pour accepter les nombres écrits en chiffres
            expected_sentence_digits = normalize_for_reading_check(metadata["sentence_with_digit"])

            # Supprime les espaces et caractères non alphabétiques pour une comparaison plus robuste
            whisper_letters = normalize_letters_only(whisper_text)
            expected_display_letters = normalize_letters_only(expected_sentence_display)
            expected_digits_letters = normalize_letters_only(expected_sentence_digits)

            # La transcription est non conforme uniquement si elle ne correspond ni à la phrase affichée, ni à la variante avec nombres en chiffres
            if whisper_letters != expected_digits_letters and whisper_letters != expected_display_letters:
                compliant = False

            if compliant:
                compliant_cpt+=1
                
                # Crée le dossier de résultats associé à cette paire.
                pair_results_dir = create_pair_results_dir(
                    self.results_dir,
                    metadata["language_code"],
                    media_path,
                )

                # Écrit le résultat complet de Whisper en JSON.
                write_whisper_json(pair_results_dir, whisper_result)

            else:
                non_compliant_cpt+=1

                # Stocke les fichiers dont le contrôle a échoué.
                invalid_control.append([media_path, metadata_path])
                
             # Affiche le résumé après le traitement complet.
            print(f"Transcriptions conformes : {compliant_cpt}")
            print(f"Transcriptions non conformes : {non_compliant_cpt}")

            if invalid_control:
                print("\nFichiers dont le contrôle n'a pas abouti :")

                for files in invalid_control:
                    print(f"{files[0]} | {files[1]}")
            
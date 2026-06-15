import whisper

from pathlib import Path

from annotation_project.annotation.metadata_reader import (
    csv_reader,
    normalize_for_reading_check,
    normalize_letters_only
)

from annotation_project.annotation.whisper_result_writer import (
    write_whisper_json,
    create_pair_results_dir,
    copy_source_files
)


class WhisperManager:
    """
    Gère la transcription des vidéos avec Whisper et le contrôle de conformité.

    Cette classe reçoit une liste de paires vidéo/métadonnées, lance Whisper sur
    chaque vidéo, compare la transcription obtenue avec la phrase attendue, puis
    sauvegarde les résultats lorsque le contrôle est conforme.
    """

    def __init__(self, model, valid_pairs):
        """
        Initialise le gestionnaire Whisper.

        Paramètres :
            model (str) : nom du modèle Whisper à charger.
            valid_pairs (list) : liste des paires valides sous la forme
                [(media_path, metadata_path), ...].

        Retourne :
            None
        """

        # Charge le modèle Whisper demandé.
        self.model = whisper.load_model(model)

        # Stocke les paires vidéo / métadonnées à traiter.
        self.valid_pairs = valid_pairs

        # Crée et stocke le chemin du dossier racine des résultats.
        self.results_dir = self.create_results_dir()

    def create_results_dir(self):
        """
        Crée le dossier racine des résultats.

        Exemple :
            annotation_project/results/

        Retourne :
            Path : chemin du dossier racine des résultats.
        """

        # Récupère le dossier parent du package annotation.
        base_dir = Path(__file__).resolve().parents[1]

        # Définit le dossier results dans annotation_project.
        results_dir = base_dir / "results"
        
        # Crée le dossier s'il n'existe pas déjà.
        results_dir.mkdir(parents=True, exist_ok=True)

        return results_dir

    def oral_transcription(self):
        """
        Transcrit chaque paire vidéo/métadonnées avec Whisper.

        Pour chaque vidéo, la méthode :
            - lit les métadonnées associées ;
            - lance la transcription Whisper ;
            - normalise la transcription obtenue ;
            - compare cette transcription avec la phrase attendue ;
            - sauvegarde les résultats si la transcription est conforme.

        La comparaison accepte deux formes :
            - la phrase affichée à l'utilisateur ;
            - une variante avec certains nombres écrits en chiffres,
              car Whisper peut parfois transcrire les nombres sous forme numérique.

        Retourne :
            None
        """

        # Stocke les paires pour lesquelles le contrôle de conformité échoue.
        invalid_control = []

        # Compteurs utilisés pour afficher un résumé final.
        compliant_cpt = 0
        non_compliant_cpt = 0

        # Parcourt chaque paire valide : vidéo + fichier de métadonnées.
        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]

            # Par défaut, on considère la transcription comme conforme.
            compliant = True

            # Lit les métadonnées associées à la vidéo.
            metadata = csv_reader(metadata_path)

            # Lance la transcription Whisper sur la vidéo.
            whisper_result = self.model.transcribe(
                str(media_path),
                language=metadata["whisper_code"],
                fp16=False,
                word_timestamps=True
            )

            # Normalise la transcription produite par Whisper.
            whisper_text = normalize_for_reading_check(whisper_result["text"])

            # Normalise la phrase réellement affichée à l'utilisateur.
            expected_sentence_display = normalize_for_reading_check(
                metadata["sentence_display"]
            )

            # Normalise la variante autorisant les nombres écrits en chiffres.
            expected_sentence_digits = normalize_for_reading_check(
                metadata["sentence_with_digit"]
            )

            # Supprime les espaces pour rendre la comparaison plus tolérante.
            whisper_letters = normalize_letters_only(whisper_text)
            expected_display_letters = normalize_letters_only(expected_sentence_display)
            expected_digits_letters = normalize_letters_only(expected_sentence_digits)

            # La transcription est non conforme uniquement si elle ne correspond
            # ni à la phrase affichée, ni à la variante avec nombres en chiffres.
            if (
                whisper_letters != expected_display_letters
                and whisper_letters != expected_digits_letters
            ):
                compliant = False

            # Si la transcription est conforme, les résultats sont sauvegardés.
            if compliant:
                compliant_cpt += 1

                # Crée le dossier de résultats associé à cette paire.
                pair_results_dir = create_pair_results_dir(
                    self.results_dir,
                    metadata["language_code"],
                    media_path
                )

                # Copie la vidéo et le fichier metadata dans le dossier de résultats.
                copy_source_files(pair_results_dir, media_path, metadata_path)

                # Écrit le résultat complet de Whisper dans un fichier JSON.
                write_whisper_json(pair_results_dir, whisper_result)

            # Si la transcription est non conforme, la paire est conservée pour affichage.
            else:
                non_compliant_cpt += 1

                # Stocke les fichiers dont le contrôle a échoué.
                invalid_control.append([media_path, metadata_path])

        # Affiche le résumé après le traitement complet.
        print(f"Transcriptions conformes : {compliant_cpt}")
        print(f"Transcriptions non conformes : {non_compliant_cpt}")

        # Affiche le détail des fichiers non conformes, s'il y en a.
        if invalid_control:
            print("\nFichiers dont le contrôle n'a pas abouti :")

            for files in invalid_control:
                print(f"{files[0]} | {files[1]}")
import whisper
import csv
import shutil

from pathlib import Path
from annotation.metadata_reader import csv_reader, normalize_for_reading_check, normalize_letters_only

class WhisperManager:
    def __init__(self, model, valid_pairs):
        self.model = whisper.load_model(model)
        self.valid_pairs = valid_pairs
        self.compliant_pairs = []
        self.non_compliant_pairs = []

    def oral_transcription(self):
        """
        Transcrit chaque paire vidéo/métadonnées avec Whisper, puis vérifie si la transcription correspond à la phrase attendue.

        La comparaison accepte deux formes :
            - la phrase affichée à l'utilisateur, généralement en toutes lettres ;
            - une variante avec certains nombres en chiffres, car Whisper peut parfois transcrire les nombres sous forme numérique.
        """
        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]
            compliant = True

            metadata = csv_reader(metadata_path)

            result = self.model.transcribe(
                str(media_path),
                language = metadata["whisper_code"],
                fp16=False,
            )

            # Normalise la transcription produite par Whisper.
            whisper_text = normalize_for_reading_check(result["text"])

            # Normalise la phrase affichée à l'utilisateur.
            expected_sentence_display = normalize_for_reading_check(metadata["sentence_display"])

            # Normalise la variante utilisée pour accepter les nombres écrits en chiffres.
            expected_sentence_digits = normalize_for_reading_check(metadata["sentence_with_digit"])

            # Supprime les espaces et caractères non alphabétiques pour une comparaison plus robuste.
            whisper_letters = normalize_letters_only(whisper_text)
            expected_display_letters = normalize_letters_only(expected_sentence_display)
            expected_digits_letters = normalize_letters_only(expected_sentence_digits)

            # La transcription est non conforme uniquement si elle ne correspond
            # ni à la phrase affichée, ni à la variante avec nombres en chiffres.
            if whisper_letters != expected_digits_letters and whisper_letters != expected_display_letters:
                compliant = False

            if compliant:
                # Si la lecture est conforme, on conserve la phrase affichée comme transcription finale.
                final_transcription = metadata["sentence_display"]
                self.compliant_pairs.append([files, final_transcription])

            else:
                # Si la lecture est non conforme, on conserve la transcription réelle de Whisper
                print(f"Transcription de Whisper : {whisper_text}")
                print(f"Phrase d’annotation attendue : {expected_sentence_digits}")
                print(f"Phrase affichée à l’utilisateur : {expected_sentence_display} \n")    

                final_transcription = result["text"]
                self.non_compliant_pairs.append([files, final_transcription])

            print(f"Nombres de paires conformes : {len(self.compliant_pairs)}")
            print(f"Nombres de paires non conformes : {len(self.non_compliant_pairs)} \n")


    def update_metadata_with_whisper_result(self):
        if not self.non_compliant_pairs :
            return False

        for non_compliant_pair in self.non_compliant_pairs :
            metadata_path = Path(non_compliant_pair[0][1])

            with metadata_path.open("r", encoding="utf-8", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)
                fieldnames = list(reader.fieldnames) # type: ignore

            new_column = "whisper_transcription"

            if new_column not in fieldnames:
                fieldnames.append(new_column)
            
            rows[0]["whisper_transcription"] = non_compliant_pair[1]

            # Réécrit le CSV avec les anciennes colonnes + les nouvelles.
            with metadata_path.open("w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        return True
        
    



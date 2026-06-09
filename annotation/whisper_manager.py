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
        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]
            compliant = True

            metadata = csv_reader(metadata_path)

            result = self.model.transcribe(str(media_path),language = metadata["whisper_code"],fp16=False)

            text_result = normalize_for_reading_check(result["text"])
            sentence_annotation = normalize_for_reading_check(metadata["sentence_annotation"])
            sentence_display = normalize_for_reading_check(metadata["sentence_display"])

            text_result_letters = normalize_letters_only(text_result)
            sentence_annotation_letters = normalize_letters_only(sentence_annotation)
            sentence_display_letters = normalize_letters_only(sentence_display)

            if text_result_letters != sentence_annotation_letters and text_result_letters != sentence_display_letters:
                compliant = False

            if compliant:
                final_transcription = metadata["sentence_display"]
                self.compliant_pairs.append([files, final_transcription])

            else:
                print(f"Transcription de Whisper : {text_result}")
                print(f"Phrase d’annotation attendue : {sentence_annotation}")
                print(f"Phrase affichée à l’utilisateur : {sentence_display}")    

                final_transcription = result["text"]
                self.non_compliant_pairs.append([files, final_transcription])

            print(f"Nombres de paires conformes : {len(self.compliant_pairs)} \n")
            print(f"Nombres de paires non conformes : {len(self.non_compliant_pairs)}")


    def update_metadata_with_whisper_result(self):
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


        




import whisper
from annotation.metadata_reader import csv_reader, normalize_for_comparison

class WhisperManager:
    def __init__(self, model, valid_pairs):
        self.model = whisper.load_model(model)
        self.valid_pairs = valid_pairs
        self.compliant_pairs = []

    def oral_transcription(self):
        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]

            metadata = csv_reader(metadata_path)

            result = self.model.transcribe(str(media_path),language = metadata["whisper_code"],fp16=False)

            text_result = normalize_for_comparison(result["text"])
            sentence_annotation = normalize_for_comparison(metadata["sentence_annotation"])
            sentence_display = normalize_for_comparison(metadata["sentence_display"])

            print(f"Transcription de Whisper : {text_result}")
            print(f"Phrase affiché lors de l'enregistrement : {sentence_annotation} | {sentence_display}")

            if text_result == sentence_annotation or text_result == sentence_display :
                self.compliant_pairs.append(files)

            print(f"Nombres de paires conformes : {len(self.compliant_pairs)} \n")

            



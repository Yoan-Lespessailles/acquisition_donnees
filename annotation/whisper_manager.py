import whisper
from annotation.metadata_reader import csv_reader

class WhisperManager:
    def __init__(self, model, valid_pairs):
        self.model = whisper.load_model(model)
        self.valid_pairs = valid_pairs

    def oral_transcription(self):
        for files in self.valid_pairs:
            media_path = files[0]
            metadata_path = files[1]

            sentence_display, sentence_annotation = csv_reader(metadata_path)

            result = self.model.transcribe(str(media_path))

            print(f"Transcription de Whisper : {result["text"]}")
            print(f"Phrase affiché lors de l'enregistrement : {sentence_annotation}")



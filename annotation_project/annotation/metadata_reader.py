import csv
import string
import unicodedata

def csv_reader(metadata_path):
    with metadata_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        metadata = next(reader)
            
    return metadata

def normalize_for_reading_check(text):
    # Supprime les espaces au début et à la fin
    normalized_text = text.strip()

    # Met le texte en minuscules de manière robuste
    normalized_text = normalized_text.casefold()

    # Décompose les caractères accentués
    # Exemple : "é" devient "e" + accent séparé
    normalized_text = unicodedata.normalize("NFD", normalized_text)

    # Supprime les accents et signes diacritiques
    normalized_text = "".join(
        char for char in normalized_text
        if unicodedata.category(char) != "Mn"
    )

    # Supprime la ponctuation classique
    normalized_text = normalized_text.translate(
        str.maketrans("", "", string.punctuation)
    )

    # Réduit les espaces multiples à un seul espace
    normalized_text = " ".join(normalized_text.split())

    return normalized_text

def normalize_letters_only(text):
    return text.replace(" ","")
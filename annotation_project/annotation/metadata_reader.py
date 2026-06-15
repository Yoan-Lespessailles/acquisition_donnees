import csv
import string
import unicodedata


def csv_reader(metadata_path):
    """
    Lit un fichier CSV de métadonnées et retourne sa première ligne.

    Le fichier CSV est lu sous forme de dictionnaire grâce à csv.DictReader.
    Les noms des colonnes deviennent les clés du dictionnaire retourné.

    Paramètres :
        metadata_path (Path) : chemin du fichier CSV de métadonnées à lire.

    Retourne :
        dict : première ligne du fichier CSV sous forme de dictionnaire.
    """

    # Ouvre le fichier CSV en lecture avec l'encodage UTF-8.
    with metadata_path.open("r", encoding="utf-8", newline="") as csv_file:
        # Lit le fichier CSV sous forme de dictionnaire.
        reader = csv.DictReader(csv_file)

        # Récupère la première ligne de métadonnées.
        metadata = next(reader)

    return metadata


def normalize_for_reading_check(text):
    """
    Normalise un texte pour faciliter la comparaison entre deux phrases.

    Cette fonction permet de comparer plus facilement :
        - la phrase attendue issue des métadonnées ;
        - la phrase reconnue automatiquement par Whisper.

    La normalisation applique plusieurs traitements :
        - suppression des espaces inutiles ;
        - passage en minuscules ;
        - suppression des accents ;
        - suppression de la ponctuation ;
        - réduction des espaces multiples.

    Paramètres :
        text (str) : texte à normaliser.

    Retourne :
        str : texte normalisé.
    """

    # Supprime les espaces au début et à la fin.
    normalized_text = text.strip()

    # Met le texte en minuscules de manière robuste.
    # casefold() est plus complet que lower() pour certaines langues.
    normalized_text = normalized_text.casefold()

    # Décompose les caractères accentués.
    # Exemple : "é" devient "e" + accent séparé.
    normalized_text = unicodedata.normalize("NFD", normalized_text)

    # Supprime les accents et signes diacritiques.
    normalized_text = "".join(
        char for char in normalized_text
        if unicodedata.category(char) != "Mn"
    )

    # Supprime la ponctuation classique.
    normalized_text = normalized_text.translate(
        str.maketrans("", "", string.punctuation)
    )

    # Réduit les espaces multiples à un seul espace.
    normalized_text = " ".join(normalized_text.split())

    return normalized_text


def normalize_letters_only(text):
    """
    Supprime les espaces d'un texte déjà normalisé.

    Cette fonction peut être utilisée après normalize_for_reading_check()
    lorsqu'on veut comparer deux phrases uniquement sur la suite de lettres,
    sans tenir compte des espaces.

    Exemple :
        "bonjour tout le monde"
        devient :
        "bonjourtoutlemonde"

    Paramètres :
        text (str) : texte dont les espaces doivent être supprimés.

    Retourne :
        str : texte sans espaces.
    """

    # Supprime uniquement les espaces simples.
    return text.replace(" ", "")
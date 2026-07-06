import csv


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

    # Ouvre le fichier CSV en lecture avec l'encodage UTF-8
    with metadata_path.open("r", encoding="utf-8", newline="") as csv_file:
        # Lit le fichier CSV sous forme de dictionnaire
        reader = csv.DictReader(csv_file)

        # Récupère la première ligne de métadonnées
        metadata = next(reader)

    return metadata

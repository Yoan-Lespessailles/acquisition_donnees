from pathlib import Path
import yaml


def load_config():
    """
    Charge le fichier config.yaml et retourne un dictionnaire de configuration.

    Les chemins définis dans le YAML sont d'abord conservés en version relative
    avec le suffixe "_rel", puis remplacés par leur version absolue pour le
    reste de l'application.
    """
    # Dossier racine du projet.
    base_dir = Path(__file__).resolve().parents[1]

    # Chemin du fichier YAML.
    config_path = base_dir / "config.yaml"

    # Ouverture et lecture du fichier YAML.
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    # Sécurité : si le fichier YAML est vide, on retourne un dictionnaire vide.
    if config is None:
        config = {}

    # Ajoute le chemin racine du projet dans la configuration.
    config["base_dir"] = base_dir

    # Conserve le chemin relatif
    config["paths"]["data_dir_rel"] = Path(config["paths"]["data_dir"])
    config["paths"]["corpus_dir_rel"] = Path(config["paths"]["corpus_dir"])

    # Convertit les chemins relatifs du YAML en chemins absolus.
    config["paths"]["data_dir"] = base_dir / config["paths"]["data_dir"]
    config["paths"]["corpus_dir"] = base_dir / config["paths"]["corpus_dir"]

    return config

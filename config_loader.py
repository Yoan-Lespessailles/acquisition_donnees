from pathlib import Path
import yaml


def load_config():
    """
    Charge le fichier config.yaml et retourne un dictionnaire de configuration.
    """

    # Dossier racine du projet.
    base_dir = Path(__file__).resolve().parent

    # Chemin du fichier YAML.
    config_path = base_dir / "config.yaml"

    # Ouverture et lecture du fichier YAML.
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    # Ajoute le chemin racine du projet dans la configuration.
    config["base_dir"] = base_dir

    # Convertit les chemins relatifs du YAML en chemins absolus.
    config["paths"]["data_dir"] = base_dir / config["paths"]["data_dir"]
    config["paths"]["corpus_dir"] = base_dir / config["paths"]["corpus_dir"]

    return config
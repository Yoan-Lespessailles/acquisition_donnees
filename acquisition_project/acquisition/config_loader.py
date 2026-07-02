from pathlib import Path
import sys

import yaml


def load_config():
    """
    Charge le fichier config.yaml et retourne un dictionnaire de configuration.

    On conserve les chemins relatifs du YAML ainsi que les chemins absolus. Les chemins relatifs sont stockés avec le suffixe "_rel", puis remplacés par leur version absolue pour le reste de l'application.
    """

    # Dossier du package acquisition_project
    if getattr(sys, "frozen", False):
        # En production, config.yaml reste modifiable a cote de l'executable
        acquisition_project_dir = Path(sys.executable).resolve().parent
        base_dir = acquisition_project_dir.parent
    else:
        acquisition_project_dir = Path(__file__).resolve().parents[1]
        base_dir = acquisition_project_dir.parent

    # Dossier racine du dépôt, situé au-dessus de acquisition_project
    # Chemin du fichier YAML
    config_path = acquisition_project_dir / "config.yaml"

    # Ouverture et lecture du fichier YAML
    with open(config_path, "r", encoding="utf-8") as file:
        user_config = yaml.safe_load(file)

    # Si le YAML est vide, on utilise uniquement les valeurs par défaut
    config = user_config or {}

    # Valeurs par défaut si elles ne sont pas définies dans config.yaml ou si le YAML est incomplet
    config.setdefault("paths", {})
    config["paths"].setdefault("data_dir", "data")
    config["paths"].setdefault("corpus_dir", "corpus")

    config.setdefault("recording", {})
    config["recording"].setdefault("audio_bitrate", 128000)
    config["recording"].setdefault("video_bitrate_low", 8000000)
    config["recording"].setdefault("video_bitrate_medium", 12000000)
    config["recording"].setdefault("video_bitrate_high", 20000000)

    config.setdefault("sentence", {})
    config["sentence"].setdefault("mode", 0)

    # Ajoute le chemin racine du projet dans la configuration
    config["base_dir"] = base_dir

    # Conserve le chemin relatif
    config["paths"]["data_dir_rel"] = Path(config["paths"]["data_dir"])
    config["paths"]["corpus_dir_rel"] = Path(config["paths"]["corpus_dir"])

    # Convertit les chemins relatifs du YAML en chemins absolus
    config["paths"]["data_dir"] = base_dir / config["paths"]["data_dir"]
    config["paths"]["corpus_dir"] = base_dir / config["paths"]["corpus_dir"]

    return config

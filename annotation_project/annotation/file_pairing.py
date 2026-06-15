from pathlib import Path


def match_video_and_metadata_files(video_files, metadata_files, videos_dir, metadata_dir):
    """
    Associe les fichiers vidéo et les fichiers de métadonnées ayant le même nom de base.

    Exemple :
        video_001.mp4 sera associé à video_001.csv si les deux fichiers existent.

    Paramètres :
        video_files (list) : liste des fichiers vidéo trouvés.
        metadata_files (list) : liste des fichiers de métadonnées trouvés.
        videos_dir (Path | str) : dossier contenant les vidéos.
        metadata_dir (Path | str) : dossier contenant les fichiers de métadonnées.

    Retourne :
        tuple :
            - built_file_pairs : liste des paires valides sous forme (video_path, metadata_path).
            - rebuilt_file_paths_video : liste des vidéos sans fichier de métadonnées associé.
            - rebuilt_file_paths_metadata : liste des fichiers de métadonnées sans vidéo associée.
    """

    # Extensions attendues pour les fichiers vidéo et les fichiers de métadonnées.
    video_extension = "mp4"
    metadata_extension = "csv"

    # Récupère uniquement les noms de fichiers sans extension.
    # Exemple : "fr_20260602_092105.mp4" devient "fr_20260602_092105".
    videos_set = extract_file_stems(video_files)
    metadata_set = extract_file_stems(metadata_files)

    # Identifie les fichiers présents à la fois côté vidéo et côté métadonnées.
    pairs = videos_set & metadata_set

    # Identifie les vidéos qui n'ont pas de fichier de métadonnées correspondant.
    videos_without_metadata = videos_set - metadata_set

    # Identifie les fichiers de métadonnées qui n'ont pas de vidéo correspondante.
    metadata_without_video = metadata_set - videos_set

    # Affiche un résumé du résultat de l'association.
    print_match(
        videos_set,
        metadata_set,
        pairs,
        videos_without_metadata,
        metadata_without_video
    )

    # Reconstruit les chemins complets des paires valides.
    built_file_pairs = build_pairs(
        pairs,
        videos_dir,
        metadata_dir,
        video_extension,
        metadata_extension
    )

    # Reconstruit les chemins complets des vidéos sans métadonnées.
    rebuilt_file_paths_video = rebuild_file_paths_from_stems(
        videos_without_metadata,
        videos_dir,
        video_extension
    )

    # Reconstruit les chemins complets des métadonnées sans vidéo.
    rebuilt_file_paths_metadata = rebuild_file_paths_from_stems(
        metadata_without_video,
        metadata_dir,
        metadata_extension
    )

    return built_file_pairs, rebuilt_file_paths_video, rebuilt_file_paths_metadata


def print_match(videos_set, metadata_set, pairs, videos_without_metadata, metadata_without_video):
    """
    Affiche un résumé du résultat de l'association entre vidéos et métadonnées.

    Paramètres :
        videos_set (set) : ensemble des noms de vidéos sans extension.
        metadata_set (set) : ensemble des noms de métadonnées sans extension.
        pairs (set) : ensemble des noms présents dans les deux dossiers.
        videos_without_metadata (set) : ensemble des vidéos sans métadonnées associées.
        metadata_without_video (set) : ensemble des métadonnées sans vidéo associée.

    Retourne :
        None
    """

    print(f"Vidéos trouvées : {len(videos_set)}")
    print(f"Metadata trouvées : {len(metadata_set)}")
    print(f"Paires valides : {len(pairs)}")
    print(f"Vidéos sans metadata : {len(videos_without_metadata)}")
    print(f"Metadata sans vidéo : {len(metadata_without_video)}")


def extract_file_stems(files):
    """
    Extrait les noms de fichiers sans leur extension.

    Exemple :
        "/data/fr/videos/fr_20260602_092105.mp4"
        devient :
        "fr_20260602_092105"

    Paramètres :
        files (list) : liste de chemins de fichiers.

    Retourne :
        set : ensemble des noms de fichiers sans extension.
    """

    file_stems = set()

    # Parcourt chaque fichier pour récupérer uniquement son nom sans extension.
    for file_path in files:
        file_stems.add(Path(file_path).stem)

    return file_stems


def rebuild_file_paths_from_stems(file_stems, source_dir, extension):
    """
    Reconstruit des chemins complets à partir de noms de fichiers sans extension.

    Exemple :
        file_stem = "fr_20260602_092105"
        source_dir = "data/fr/videos"
        extension = "mp4"

        Résultat :
        data/fr/videos/fr_20260602_092105.mp4

    Paramètres :
        file_stems (set) : ensemble des noms de fichiers sans extension.
        source_dir (Path | str) : dossier dans lequel reconstruire les chemins.
        extension (str) : extension à ajouter aux noms de fichiers.

    Retourne :
        list : liste des chemins reconstruits.
    """

    rebuilt_file_paths = []

    # Reconstruit chaque chemin en combinant le dossier, le nom du fichier et l'extension.
    for file_stem in file_stems:
        rebuilt_file_paths.append(Path(source_dir) / f"{file_stem}.{extension}")

    return rebuilt_file_paths


def build_pairs(pairs, videos_dir, metadata_dir, video_extension, metadata_extension):
    """
    Construit les paires de chemins vidéo/métadonnées à partir des noms communs.

    Exemple :
        "fr_20260602_092105"
        devient :
        (
            data/fr/videos/fr_20260602_092105.mp4,
            data/fr/annotations/fr_20260602_092105.csv
        )

    Paramètres :
        pairs (set) : ensemble des noms de fichiers présents dans les deux dossiers.
        videos_dir (Path | str) : dossier contenant les vidéos.
        metadata_dir (Path | str) : dossier contenant les métadonnées.
        video_extension (str) : extension des fichiers vidéo.
        metadata_extension (str) : extension des fichiers de métadonnées.

    Retourne :
        list : liste de tuples sous la forme (video_path, metadata_path).
    """

    built_file_pairs = []

    # Pour chaque nom commun, reconstruit le chemin vidéo et le chemin métadonnées.
    for file_stem in pairs:
        video_path = Path(videos_dir) / f"{file_stem}.{video_extension}"
        metadata_path = Path(metadata_dir) / f"{file_stem}.{metadata_extension}"

        built_file_pairs.append((video_path, metadata_path))

    return built_file_pairs
import shutil
from pathlib import Path

def create_destination_path(unmatched_dir, file_type) :
    return (Path(unmatched_dir) / file_type)


def create_unmatched_directories(language_dir, videos_without_metadata, metadatas_without_video) :
    
    unmatched_dir = Path(language_dir) / "unmatched"
    unmatched_videos_dir = None
    unmatched_metadatas_dir = None


    unmatched_dir.mkdir(parents=True, exist_ok=True)

    # Si la liste est vide
    if videos_without_metadata :
        unmatched_videos_dir = create_destination_path(unmatched_dir, "videos")
        unmatched_videos_dir.mkdir(parents=True, exist_ok=True)
    

    if metadatas_without_video :
        unmatched_metadatas_dir = create_destination_path(unmatched_dir, "metadatas")
        unmatched_metadatas_dir.mkdir(parents=True, exist_ok=True)
    

    return unmatched_videos_dir, unmatched_metadatas_dir


def move_unmatched_files (language_dir, videos_without_metadata, metadatas_without_video):
    #Si aucun fichier n’est non appairé, aucun dossier unmatched n’est créé.
    if not videos_without_metadata and not metadatas_without_video :
        return False
    
    unmatched_videos_dir, unmatched_metadatas_dir = create_unmatched_directories(language_dir, videos_without_metadata, metadatas_without_video)

    if unmatched_videos_dir is not None :
        # Pour chaque vidéo dans la liste, on déplace les fichiers dans un autre dossier
        for video in videos_without_metadata :
            # shutil.move(source, destination)
            shutil.move(video, unmatched_videos_dir / Path(video).name)
    
    if unmatched_metadatas_dir is not None :
         for metadata in metadatas_without_video :
            shutil.move(metadata, unmatched_metadatas_dir / Path(video).name)

    
import shutil
from pathlib import Path

def create_destination_path(unmatched_dir, file_type) :
    return (Path(unmatched_dir) / file_type)



def create_unmatched_directories(language_dir, videos_without_metadata, metadata_without_video) :
    
    unmatched_dir = Path(language_dir) / "unmatched"
    unmatched_videos_dir = None
    unmatched_metadata_dir = None


    unmatched_dir.mkdir(parents=True, exist_ok=True)

    # Si la liste est vide
    if videos_without_metadata :
        unmatched_videos_dir = create_destination_path(unmatched_dir, "videos")
        unmatched_videos_dir.mkdir(parents=True, exist_ok=True)
    

    if metadata_without_video :
        unmatched_metadata_dir = create_destination_path(unmatched_dir, "metadata")
        unmatched_metadata_dir.mkdir(parents=True, exist_ok=True)
    

    return unmatched_videos_dir, unmatched_metadata_dir



def move_unmatched_files (language_dir, videos_without_metadata, metadata_without_video):
    #Si aucun fichier n’est non appairé, aucun dossier unmatched n’est créé.
    if not videos_without_metadata and not metadata_without_video :
        return 0, 0
    
    unmatched_videos_dir, unmatched_metadata_dir = create_unmatched_directories(language_dir, videos_without_metadata, metadata_without_video)
    move_videos_cpt = 0
    move_metadata_cpt = 0


    if unmatched_videos_dir is not None :
        # Pour chaque vidéo dans la liste, on déplace les fichiers dans un autre dossier
        for video in videos_without_metadata :
            # shutil.move(source, destination)
            shutil.move(video, unmatched_videos_dir / Path(video).name)
            move_videos_cpt += 1
    
    if unmatched_metadata_dir is not None :
         for metadata in metadata_without_video :
            shutil.move(metadata, unmatched_metadata_dir / Path(metadata).name)
            move_metadata_cpt +=1
    
    return move_videos_cpt, move_metadata_cpt



def move_pair_to_human_review(language_dir, non_compliant_pairs):
    non_compliant_video_dir, non_compliant_metadata_dir = create_non_compliant_directories(language_dir)
    move_files_cpt = 0

    for non_compliant_pair in non_compliant_pairs :
        media_file = non_compliant_pair[0][0]
        metadata_file = non_compliant_pair[0][1]

        shutil.move(media_file, non_compliant_video_dir / Path(media_file).name)
        shutil.move(metadata_file, non_compliant_metadata_dir / Path(metadata_file).name)

        move_files_cpt += 2

    return move_files_cpt



def create_non_compliant_directories(language_dir):
    non_compliant_dir = Path(language_dir) / "non_compliant"
    non_compliant_dir.mkdir(parents=True, exist_ok=True)

    non_compliant_video_dir = non_compliant_dir / "videos"
    non_compliant_metadata_dir = non_compliant_dir / "metadata"

    non_compliant_video_dir.mkdir(parents=True, exist_ok=True)
    non_compliant_metadata_dir.mkdir(parents=True, exist_ok=True)

    return non_compliant_video_dir, non_compliant_metadata_dir
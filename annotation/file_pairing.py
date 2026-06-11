from pathlib import Path

def match_video_and_metadata_files(video_files, metadata_files, videos_dir, metadata_dir):
    video_extension = "mp4"
    metadata_extension = "csv"

    videos_set = extract_file_stems(video_files)
    metadata_set = extract_file_stems(metadata_files)

    pairs = videos_set & metadata_set
    videos_without_annotation = videos_set - metadata_set
    metadata_without_video = metadata_set - videos_set

    print_match(videos_set, metadata_set, pairs, videos_without_annotation, metadata_without_video)

    return build_pairs(pairs, videos_dir, metadata_dir, video_extension, metadata_extension), rebuild_file_paths_from_stems(videos_without_annotation, videos_dir, video_extension), rebuild_file_paths_from_stems(metadata_without_video, metadata_dir, metadata_extension)
    

def print_match(videos_set, annotations_set, pairs, videos_without_annotation, annotations_without_video):
    print(f"Vidéos trouvées : {len(videos_set)}")
    print(f"Annotations trouvées : {len(annotations_set)}")
    print(f"Paires valides : {len(pairs)}")
    print(f"Vidéos sans annotation : {len(videos_without_annotation)}")
    print(f"Annotations sans vidéo : {len(annotations_without_video)}")


def extract_file_stems(files):
    file_stems = set()

    for file_path in files:
        file_stems.add(Path(file_path).stem)

    return file_stems


def rebuild_file_paths_from_stems(file_stems, source_dir, extension):
    rebuilt_file_paths = []

    for file_stem in file_stems:
        rebuilt_file_paths.append(Path(source_dir) / f"{file_stem}.{extension}")

    return rebuilt_file_paths


def build_pairs(pairs, videos_dir, metadata_dir, video_extension, metadata_extension):
    built_file_pairs = []

    for file_stem in pairs :
        built_file_pairs.append((Path(videos_dir) / f"{file_stem}.{video_extension}", Path(metadata_dir) / f"{file_stem}.{metadata_extension}"))
    
    return built_file_pairs
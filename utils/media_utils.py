import av, hashlib

from av.audio.stream import AudioStream
from av.video.stream import VideoStream

from pathlib import Path

from PySide6.QtMultimedia import QMediaFormat



def get_camera_format_score(camera_format):
    """
    Calcule un score pour comparer les formats caméra.

    Priorité :
        1. atteindre au moins 30 FPS ;
        2. avoir la meilleure résolution ;
        3. avoir le FPS le plus élevé.

    Le score est retourné sous forme de tuple.
    Python compare les tuples élément par élément, dans l'ordre.
    """

    # Récupère la résolution du format caméra.
    resolution = camera_format.resolution()

    # Récupère la largeur et la hauteur de la résolution.
    width = resolution.width()
    height = resolution.height()

    # Calcule le nombre total de pixels.
    pixels = width * height

    # Récupère le nombre maximum d'images par seconde.
    max_fps = camera_format.maxFrameRate()

    # Donne la priorité aux formats capables d'atteindre au moins 30 FPS.
    has_good_fps = max_fps >= 30

    # Retourne les critères de comparaison.
    return (has_good_fps, pixels, max_fps)


def create_recording_media_format(preferred_video_codec):
    """
    Crée le format d'enregistrement MP4 avec le codec vidéo demandé si disponible.

    Paramètre :
        preferred_video_codec : codec vidéo que l'on souhaite utiliser en priorité.

    Retourne :
        un objet QMediaFormat configuré.
    """

    # Crée un format média Qt.
    media_format = QMediaFormat()

    # Définit le conteneur MP4.
    # Dans Qt, QMediaFormat.MPEG4 correspond ici au conteneur MP4.
    media_format.setFileFormat(QMediaFormat.FileFormat.MPEG4)

    # Récupère les codecs vidéo disponibles en encodage pour ce conteneur.
    supported_video_codecs = media_format.supportedVideoCodecs(
        QMediaFormat.ConversionMode.Encode
    )

    # Affiche les codecs disponibles pour le debug.
    print(
        "Codecs vidéo supportés en encodage MP4 :",
        [codec.name for codec in supported_video_codecs],
    )

    # Utilise le codec préféré s'il est disponible.
    if preferred_video_codec in supported_video_codecs:
        media_format.setVideoCodec(preferred_video_codec)

    # Sinon, tente MPEG4.
    elif QMediaFormat.VideoCodec.MPEG4 in supported_video_codecs:
        print("Codec demandé non disponible, fallback vers MPEG4")
        media_format.setVideoCodec(QMediaFormat.VideoCodec.MPEG4)

    # Dernier recours : MotionJPEG.
    else:
        print("Encodeur MPEG4 non disponible, fallback vers MotionJPEG")
        media_format.setVideoCodec(QMediaFormat.VideoCodec.MotionJPEG)

    # Définit le codec audio AAC.
    media_format.setAudioCodec(QMediaFormat.AudioCodec.AAC)

    return media_format


def extract_video_metadata(video_filepath):
    """
    Extrait les métadonnées réelles d'un fichier vidéo avec PyAV.

    Paramètres :
        video_filepath : chemin du fichier vidéo à analyser.

    Retourne :
        un dictionnaire contenant les informations utiles pour l'annotation.
    """
    

    # Convertit le chemin reçu en objet Path.
    # Cela permet de ne pas avoir d'erreurs de Pylance
    video_filepath = Path(video_filepath)

    # Calcule le checksum SHA-256 du fichier vidéo.
    # Il permet de vérifier plus tard que le fichier n'a pas été modifié ou corrompu.
    checksum_sha256 = calculate_file_checksum(video_filepath)

    # Ouvre le fichier vidéo.
    container = av.open(str(video_filepath))

    # Récupère le format enregistré à partir de l'extension du fichier.
    video_format = video_filepath.suffix.replace(".", "").lower()

    # Récupère la durée globale du conteneur.
    # PyAV exprime souvent la durée en microsecondes via container.duration.
    duration_seconds = None
    if container.duration is not None:
        duration_seconds = round(container.duration / 1_000_000, 3)

    # Recherche la première piste vidéo.
    # container.streams.video est typé par PyAV comme une liste de VideoStream.
    # Cela évite les fausses erreurs de l'IDE sur .width, .height, etc.
    if container.streams.video:
        video_stream: VideoStream | None = container.streams.video[0]
    else:
        video_stream = None

    # Recherche la première piste audio.
    # container.streams.audio est typé par PyAV comme une liste de AudioStream.
    # Cela évite les fausses erreurs de l'IDE sur .channels, .sample_rate, etc.
    if container.streams.audio:
        audio_stream: AudioStream | None = container.streams.audio[0]
    else:
        audio_stream = None

    # Métadonnées vidéo.
    video_codec = None
    video_width = None
    video_height = None
    video_fps = None
    video_bitrate = None

    if video_stream is not None:
        video_codec = video_stream.codec_context.name
        video_width = video_stream.width
        video_height = video_stream.height
        video_bitrate = video_stream.codec_context.bit_rate

        # average_rate peut être une fraction, par exemple 30/1 ou 30000/1001.
        if video_stream.average_rate is not None:
            video_fps = float(video_stream.average_rate)

    # Métadonnées audio.
    audio_codec = None
    audio_sample_rate = None
    audio_channels = None
    audio_bitrate = None

    if audio_stream is not None:
        audio_codec = audio_stream.codec_context.name
        audio_sample_rate = audio_stream.codec_context.sample_rate
        audio_channels = audio_stream.codec_context.channels
        audio_bitrate = audio_stream.codec_context.bit_rate

    # Ferme le conteneur proprement.
    container.close()

    return {
        "video_format": video_format,
        "checksum_sha256": checksum_sha256,

        "duration_seconds": duration_seconds,

        "video_codec": video_codec,
        "video_width": video_width,
        "video_height": video_height,
        "video_fps": video_fps,
        "video_bitrate": video_bitrate,

        "audio_codec": audio_codec,
        "audio_sample_rate": audio_sample_rate,
        "audio_channels": audio_channels,
        "audio_bitrate": audio_bitrate,
    }

def calculate_file_checksum(file_path):
    """
    Calcule le checksum SHA-256 d'un fichier.

    Le fichier est lu par blocs pour éviter de charger toute la vidéo
    en mémoire, ce qui est important pour les fichiers volumineux.
    """

    # Convertit le chemin reçu en objet Path.
    file_path = Path(file_path)

    # Crée l'objet de calcul SHA-256.
    sha256_hash = hashlib.sha256()

    # Ouvre le fichier en mode binaire.
    with file_path.open("rb") as file:
        # Lit le fichier par blocs de 8192 octets jusqu'à la fin.
        for block in iter(lambda: file.read(8192), b""):
            sha256_hash.update(block)

    # Retourne le checksum sous forme de chaîne hexadécimale.
    return sha256_hash.hexdigest()
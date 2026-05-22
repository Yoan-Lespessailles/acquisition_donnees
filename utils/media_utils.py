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
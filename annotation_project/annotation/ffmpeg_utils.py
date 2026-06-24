import os
import shutil

from pathlib import Path


def find_ffmpeg_executable():
    """
    Trouve l'exécutable FFmpeg à utiliser.

    La recherche utilise d'abord le PATH courant. Sous Windows, si Conda masque
    le PATH système, la recherche vérifie aussi l'emplacement utilisé par winget
    pour le paquet Gyan.FFmpeg.
    """

    ffmpeg_from_path = shutil.which("ffmpeg")

    if ffmpeg_from_path is not None:
        return ffmpeg_from_path

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data is not None:
            winget_packages_dir = (
                Path(local_app_data)
                / "Microsoft"
                / "WinGet"
                / "Packages"
            )

            ffmpeg_candidates = sorted(
                winget_packages_dir.glob(
                    "Gyan.FFmpeg_*/*/bin/ffmpeg.exe"
                )
            )

            if ffmpeg_candidates:
                return str(ffmpeg_candidates[-1])

    raise FileNotFoundError(
        "FFmpeg est introuvable. Installe une version complète de FFmpeg "
        "et vérifie que la commande ffmpeg est disponible dans le terminal."
    )

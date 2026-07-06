import os
import shutil
import subprocess

from pathlib import Path


def ffmpeg_has_ass_filter(ffmpeg_executable):
    """
    Indique si l'exécutable FFmpeg possède le filtre ASS.
    """

    try:
        # Demande à FFmpeg la liste complète des filtres disponibles
        completed_process = subprocess.run(
            [str(ffmpeg_executable), "-filters"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, PermissionError, subprocess.CalledProcessError):
        # Si FFmpeg est introuvable, inaccessible ou invalide, on l'ignore
        return False

    # FFmpeg peut écrire certaines informations dans stdout ou stderr
    filters_output = completed_process.stdout + completed_process.stderr

    # Le filtre ass est nécessaire pour incruster les sous-titres ASS
    return " ass " in filters_output


def iter_ffmpeg_candidates():
    """
    Liste les exécutables FFmpeg possibles, en évitant les doublons.
    """

    # Mémorise les chemins déjà proposés pour éviter de tester deux fois le même FFmpeg
    seen_candidates = set()

    # Récupère le PATH courant, qui peut contenir un FFmpeg installé par Conda
    path_value = os.environ.get("PATH", "")

    # Parcourt chaque dossier du PATH pour trouver les exécutables FFmpeg disponibles
    for path_entry in path_value.split(os.pathsep):
        if not path_entry:
            continue

        # Sous Windows l'exécutable s'appelle ffmpeg.exe, ailleurs ffmpeg
        candidate = Path(path_entry) / (
            "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        )

        if candidate.exists():
            # Utilise le chemin résolu pour comparer les candidats sans doublons
            # resolve() est une méthode de Path permettant de récupérer le chemin absolu
            resolved_candidate = str(candidate.resolve())

            if resolved_candidate not in seen_candidates:
                seen_candidates.add(resolved_candidate)
                yield candidate

    # Vérifie aussi le résultat standard de shutil.which
    ffmpeg_from_path = shutil.which("ffmpeg")

    if ffmpeg_from_path is not None:
        candidate = Path(ffmpeg_from_path)
        resolved_candidate = str(candidate.resolve())

        if resolved_candidate not in seen_candidates:
                seen_candidates.add(resolved_candidate)
                yield candidate

    # Sous Windows, Winget peut installer Gyan FFmpeg hors de l'environnement Conda
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data is not None:
            # Winget peut exposer certaines commandes dans le dossier Links
            winget_links_candidate = (
                Path(local_app_data)
                / "Microsoft"
                / "WinGet"
                / "Links"
                / "ffmpeg.exe"
            )

            if winget_links_candidate.exists():
                resolved_candidate = str(winget_links_candidate.resolve())

                if resolved_candidate not in seen_candidates:
                    seen_candidates.add(resolved_candidate)
                    yield winget_links_candidate

            # Dossier où Winget installe les paquets utilisateur
            winget_packages_dir = (
                Path(local_app_data)
                / "Microsoft"
                / "WinGet"
                / "Packages"
            )

            ffmpeg_candidates = []

            # Recherche les installations Gyan.FFmpeg dans le dossier des paquets Winget
            for package_dir in winget_packages_dir.glob("Gyan.FFmpeg_*"):
                ffmpeg_candidates.extend(
                    package_dir.glob("ffmpeg-*/bin/ffmpeg.exe")
                )
                ffmpeg_candidates.extend(
                    package_dir.glob("ffmpeg-*full_build/bin/ffmpeg.exe")
                )

                for ffmpeg_dir in package_dir.glob("ffmpeg-*"):
                    # Ajoute aussi le chemin attendu directement, même si son accès est particulier
                    direct_candidate = ffmpeg_dir / "bin" / "ffmpeg.exe"
                    ffmpeg_candidates.append(direct_candidate)

            for candidate in ffmpeg_candidates:
                resolved_candidate = str(candidate.resolve())

                if resolved_candidate not in seen_candidates:
                    seen_candidates.add(resolved_candidate)
                    yield candidate


def find_ffmpeg_executable():
    """
    Trouve l'exécutable FFmpeg à utiliser.

    La recherche sélectionne un FFmpeg qui possède le filtre ASS. Cela évite
    d'utiliser automatiquement le FFmpeg installé par Conda lorsqu'il ne permet
    pas d'incruster les sous-titres .ass.
    """

    tested_candidates = []

    # Teste chaque FFmpeg trouvé et garde uniquement un exécutable compatible ASS
    for ffmpeg_candidate in iter_ffmpeg_candidates():
        tested_candidates.append(str(ffmpeg_candidate))

        if ffmpeg_has_ass_filter(ffmpeg_candidate):
            return str(ffmpeg_candidate)

    # Prépare une liste lisible des candidats testés pour aider au diagnostic
    tested_candidates_message = "\n".join(
        f"- {candidate}" for candidate in tested_candidates
    )

    raise FileNotFoundError(
        "Aucun FFmpeg compatible n'a été trouvé. Installe une version complète "
        "de FFmpeg avec le filtre 'ass'. Sous Windows : winget install Gyan.FFmpeg\n"
        f"FFmpeg testés :\n{tested_candidates_message}"
    )

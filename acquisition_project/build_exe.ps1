# Interrompt immediatement le script si une commande echoue. Sans cette option,
# PowerShell pourrait continuer et produire une distribution incomplete
$ErrorActionPreference = "Stop"

# $PSScriptRoot correspond au dossier qui contient ce script, quel que soit le
# dossier depuis lequel il est lance
$projectDir = $PSScriptRoot

# Le depot est le dossier parent de acquisition_project. Il contient notamment
# le corpus partage et recevra le dossier final de distribution
$repositoryDir = Split-Path -Parent $projectDir

# Organisation finale :
# AVDataCollector/
# |-- AVDataCollector.exe
# |-- config.yaml
# `-- corpus/
#
# PyInstaller cree automatiquement le dossier AVDataCollector a partir du nom
# declare dans acquisition.spec. --distpath doit donc pointer vers son parent.
$distParentDir = $repositoryDir
$applicationDir = Join-Path $distParentDir "AVDataCollector"

# PyInstaller doit etre execute depuis acquisition_project afin que les chemins
# relatifs declares dans acquisition.spec soient resolus correctement
# Push-Location memorise le dossier courant avant de se deplacer
Push-Location $projectDir
try {
    # Construit l'application avec le Python de l'environnement actuellement
    # actif. Il faut donc lancer `conda activate acquisition` au prealable
    #
    # --noconfirm : remplace une ancienne construction sans poser de question
    # --clean     : supprime le cache temporaire de la construction precedente
    # --distpath  : place le dossier AVDataCollector a la racine du depot
    #
    # Le caractere ` place en fin de ligne est la continuation de ligne propre
    # a PowerShell
    python -m PyInstaller `
        --noconfirm `
        --clean `
        --distpath $distParentDir `
        acquisition.spec

    # config.yaml n'est pas integre dans l'EXE : il reste a cote de celui-ci
    # pour pouvoir etre consulte ou modifie apres la compilation
    Copy-Item `
        -LiteralPath (Join-Path $projectDir "config.yaml") `
        -Destination (Join-Path $applicationDir "config.yaml") `
        -Force

    # Copie le corpus a cote de l'executable. -Recurse copie tous ses fichiers
    # et sous-dossiers ; -Force met a jour une copie existante
    Copy-Item `
        -LiteralPath (Join-Path $repositoryDir "corpus") `
        -Destination (Join-Path $applicationDir "corpus") `
        -Recurse `
        -Force

    # Indique le dossier a distribuer une fois toutes les etapes terminees
    Write-Host "Application construite dans : $applicationDir"
}
finally {
    # Revient toujours au dossier de depart, meme si la construction echoue
    Pop-Location
}

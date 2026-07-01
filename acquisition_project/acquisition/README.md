## Installation et lancement

Cette application correspond à la partie acquisition du projet. Elle permet d'enregistrer les vidéos et de générer le dossier `data` utilisé ensuite par l'application d'annotation.

Les commandes ci-dessous sont à exécuter depuis la racine du dépôt `acquisition_donnees`.

### 1. Préparer un environnement Python

L'application nécessite Python 3.12.

La version est déclarée dans `pyproject.toml`, mais ce fichier ne sélectionne pas automatiquement l'interpréteur Python. Il indique seulement à `pip` quelles versions sont acceptées. Il faut donc lancer les commandes depuis un environnement qui utilise déjà Python 3.12.

#### Windows PowerShell avec `.venv`

```powershell
cd acquisition_project
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

La commande `py -3.12 -m venv .venv` sert uniquement à créer un nouvel environnement virtuel avec Python 3.12. Si l'environnement existe déjà, il suffit de l'activer.

Si la commande `py -3.12` n'est pas reconnue, installer Python 3.12 puis relancer la commande. Il est aussi possible d'utiliser le chemin complet vers `python.exe` 3.12 :

```powershell
C:\chemin\vers\Python312\python.exe -m venv .venv
```

Le projet ne s'installe pas avec Python 3.11. Si l'environnement `.venv` a déjà été créé avec Python 3.11, il faut le supprimer puis le recréer avec Python 3.12.

#### Linux / macOS

```bash
cd acquisition_project
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

#### Avec conda

Si un environnement conda Python 3.12 existe déjà, il peut être utilisé à la place de `.venv`. Si vous n'en avez pas et que vous souhaitez en créer un :

```powershell
conda create -n acquisition-python312 python=3.12
```

Dans un terminal où conda est disponible :

```powershell
conda activate acquisition-python312
cd acquisition_project
python --version
python -m pip install --upgrade pip
python -m pip install -e .
```

La commande `python --version` doit afficher Python 3.12. Si `pip` affiche une erreur indiquant Python 3.11, c'est que l'environnement conda n'est pas actif dans ce terminal. Dans ce cas, ouvrir un terminal conda, activer l'environnement, puis utiliser `python -m pip` plutôt que `pip`.

### 2. Lancer l'application

Depuis le dossier `acquisition_project`, avec l'environnement activé :

```bash
python -m acquisition.main
```

Il est aussi possible de fournir directement le prénom de l'utilisateur :

```bash
python -m acquisition.main --firstname Alice
```

### 3. Modifier l'interface Qt

L'interface graphique est décrite dans le fichier Qt Designer :

```text
acquisition/ui/main_pyside.ui
```

Depuis le dossier `acquisition_project`, avec l'environnement activé, ouvrir l'interface dans Qt Designer :

```powershell
pyside6-designer acquisition\ui\main_pyside.ui
```

Après modification du fichier `.ui`, régénérer le fichier Python utilisé par l'application :

```powershell
pyside6-uic acquisition\ui\main_pyside.ui -o acquisition\ui\ui_main_pyside6.py
```

Relancer ensuite l'application pour vérifier les changements :

```powershell
python -m acquisition.main
```

### 4. Construire l'exécutable Windows

La construction de l'exécutable est optionnelle. Elle nécessite les dépendances de build :

```powershell
cd acquisition_project
python -m pip install -e ".[build]"
.\build_exe.ps1
```

Ces deux lignes sont deux commandes séparées :

- `python -m pip install -e ".[build]"` installe le projet Python avec les dépendances nécessaires à la construction, en utilisant le Python de l'environnement actif.
- `.\build_exe.ps1` lance ensuite le script PowerShell qui construit l'exécutable.

Ne pas lancer `pip install -e .\build_exe.ps1` : `build_exe.ps1` est un script, pas un projet Python installable.

L'application compilée est ensuite générée dans :

```text
distribution/
└── AVDataCollector/
```

## Présentation générale de l'application d'acquisition

L'application d'acquisition constitue la première étape du pipeline de création du corpus audio-vidéo. Elle permet d'enregistrer un utilisateur pendant la lecture de phrases issues d'un corpus linguistique prédéfini. Chaque enregistrement produit une vidéo, accompagnée d'un fichier de métadonnées contenant les métadonnées utiles : langue, phrase lue, type de template, périphériques utilisés, informations techniques du fichier vidéo et statut de validation.

Le fonctionnement général suit une logique de session. L'utilisateur renseigne d'abord son prénom, configure la caméra et le microphone, puis effectue un test micro. Une fois les périphériques validés, il choisit la langue de lecture. Le corpus correspondant est alors chargé, puis les phrases sont affichées une par une. Pour chaque phrase, l'utilisateur peut enregistrer une vidéo, la valider, la recommencer ou, après un premier échec, passer à la phrase suivante.

L'objectif principal de cette application est de garantir une acquisition structurée et exploitable des données. Les vidéos sont sauvegardées dans une arborescence organisée par langue, tandis que les métadonnées associées permettent ensuite à l'application d'annotation de retrouver automatiquement les informations nécessaires au traitement avec MFA.

Les diagrammes de flux ci-dessous présentent le déroulement fonctionnel d'une session d'acquisition.
Le déroulement fonctionnel a été divisé en deux parties : la première correspond à la préparation de la session et la deuxième à la boucle d'acquisition.

### Préparation de la session d'acquisition

```mermaid
flowchart TD
    A([Début]) --> B[Demande du prénom de l'utilisateur]
    B --> C[Choix des périphériques audio et vidéo]
    C --> D[Positionnement de la personne sur l'aperçu vidéo]
    D --> E[Test du microphone]

    E --> F{Niveau micro satisfaisant ?}
    F -- Non --> C
    F -- Oui --> G[Choix de la langue]
    G --> H[Chargement du corpus associé]
    H --> I([Début de l'acquisition])

    classDef startend fill:#d9ead3,stroke:#6aa84f,stroke-width:2px,color:#000;
    classDef process fill:#d9eaf7,stroke:#3d85c6,stroke-width:1.5px,color:#000;
    classDef decision fill:#fce5cd,stroke:#e69138,stroke-width:2px,color:#000;
    classDef retry fill:#f4cccc,stroke:#cc0000,stroke-width:1.5px,color:#000;

    class A,I startend;
    class B,C,D,E,G,H process;
    class F decision;
```

### Boucle d'enregistrement des phrases

```mermaid
flowchart TD
    A([Début de l'acquisition]) --> B{Toutes les phrases ont-elles été traitées ?}

    B -- Oui --> Z([Fin de la session])

    B -- Non --> C[Affichage de la phrase courante]
    C --> D[Enregistrement de la phrase avec le visage et la voix]

    D --> E{Premier essai pour cette phrase ?}

    E -- Oui --> J{Pop-up de validation :<br/>Oui / Non}
    E -- Non --> H{Pop-up de validation :<br/>Oui / Non / Skip}

    J -- Oui --> F[Enregistrement de la vidéo et des métadonnées]
    F --> B

    J -- Non --> G[Suppression de la vidéo refusée<br/>phrase courante conservée]
    G --> C

    H -- Oui --> F
    H -- Non --> G
    H -- Skip --> I[Phrase ignorée / passage à la suivante]
    I --> B

    classDef startend fill:#d9ead3,stroke:#6aa84f,stroke-width:2px,color:#000;
    classDef process fill:#d9eaf7,stroke:#3d85c6,stroke-width:1.5px,color:#000;
    classDef decision fill:#fce5cd,stroke:#e69138,stroke-width:2px,color:#000;
    classDef save fill:#d9ead3,stroke:#38761d,stroke-width:2px,color:#000;
    classDef retry fill:#f4cccc,stroke:#cc0000,stroke-width:1.5px,color:#000;
    classDef skip fill:#fff2cc,stroke:#bf9000,stroke-width:1.5px,color:#000;

    class A,Z startend;
    class C,D process;
    class B,E,J,H decision;
    class F save;
    class G retry;
    class I skip;
```

## Architecture de l'application d'acquisition

L'application d'acquisition est structurée autour de plusieurs composants ayant chacun une responsabilité précise. La fenêtre principale coordonne le déroulement de la session, tandis que des gestionnaires spécialisés prennent en charge les périphériques audio-vidéo, le corpus, l'indicateur d'enregistrement et la sauvegarde des métadonnées.

Cette organisation permet de séparer la logique d'interface, la logique métier et les traitements techniques. Elle facilite également l'évolution du projet, notamment l'ajout de l'application d'annotation, qui pourra réutiliser certains modules ou certaines données produites par l'acquisition.

### Diagramme de classes

Le diagramme de classes présente les principales classes de l'application d'acquisition et leurs relations. Il met en évidence le rôle central de `MyWindow`, qui possède et coordonne les différents gestionnaires : `MediaManager`, `CorpusManager`, `RecordingIndicator` et `MetadataManager`.

Chaque classe est représentée avec ses principaux attributs et méthodes afin de donner une vue synthétique de l'organisation interne du code. Le diagramme ne cherche pas à lister toutes les méthodes techniques : il montre surtout les responsabilités importantes de chaque classe.

```mermaid
classDiagram

    class MyWindow {
        - media_manager : MediaManager
        - corpus_manager : CorpusManager
        - recording_indicator : RecordingIndicator
        - metadata_manager : MetadataManager
        - user_firstname : str
        - is_recording : bool
        - cpt_retry_register : int

        + configure_responsive_ui()
        + update_responsive_text_sizes()
        + setup_managers()
        + connect_signals()
        + ask_user_firstname()
        + load_languages_into_combobox()
        + language_changed(index)
        + display_current_sentence()
        + can_start_recording() : bool
        + button_record_clicked()
        + start_recording_flow()
        + stop_recording_flow()
        + finalize_recording()
        + ask_manual_validation() : str
        + delete_failed_file()
        + update_sentence()
        + button_test_micro_clicked()
        + update_micro_level(level)
    }

    class MediaManager {
        + micro_level_changed : Signal

        - select_micro : QComboBox
        - select_camera : QComboBox
        - area_preview : QWidget
        - camera : QCamera
        - audio_input : QAudioInput
        - capture_session : QMediaCaptureSession
        - video_widget : QVideoWidget
        - recorder : QMediaRecorder
        - media_devices : QMediaDevices
        - video_bitrate : int
        - audio_bitrate : int
        - h264_fallback_tried : bool
        - file_name : str
        - video_filepath : Path
        - video_filepath_rel : Path
        - metadata_filepath : Path
        - metadata_filepath_rel : Path
        - video_width : int
        - video_height : int
        - video_fps : float
        - micro_test_is_running : bool
        - audio_source : QAudioSource
        - audio_io_device : QIODevice
        - audio_format : QAudioFormat

        + setup()
        + load_microphones()
        + load_cameras()
        + refresh_microphones()
        + refresh_cameras()
        + change_microphone(index)
        + change_camera(index)
        + get_selected_microphone()
        + get_selected_camera()
        + has_selected_microphone() : bool
        + has_selected_camera() : bool
        + configure_camera_format(camera_device)
        + setup_camera_preview()
        + start_camera_preview()
        + setup_recording()
        + apply_recorder_bitrates()
        + start_recording(language_code) : bool
        + stop_recording()
        + recorder_error_occurred(error, error_string)
        + restart_recording_with_mpeg4()
        + start_micro_test(audio_device)
        + stop_micro_test()
        + process_micro_level()
        + calculate_audio_level(audio_data) : int
    }

    class CorpusManager {
        - corpus_dir : Path
        - sentence_total : int
        - sentence_mode : int
        - sentence_count : int
        - languages : list
        - language_selected : tuple
        - corpus_data : dict
        - current_sentence : str
        - current_template_type : str
        - sentence_with_digit : str

        + load_languages() : list
        + select_language(index) : bool
        + prepare_session() : bool
        + load_selected_language_corpus() : bool
        + total_sentences() : int
        + shuffle_corpus() : bool
        + reset_session()
        + get_current_sentence() : str
        + build_template_1_sentence() : str
        + consume_current_sentence() : bool
        + is_session_finished() : bool
        + get_sentence_counter_text() : str
    }

    class RecordingIndicator {
        - label_record_timer : QLabel
        - label_record_dot : QLabel
        - blink_timer : QTimer
        - record_timer : QTimer
        - record_seconds : int
        - blink_visible : bool

        + show()
        + hide()
        + start()
        + stop()
        + set_timer_text(text)
        + blink_dot()
        + update_record_timer()
    }

    class MetadataManager {
        - machine_name : str
        - operating_system : str
        - fieldnames : list

        + save_recording_metadata(media_manager : MediaManager, corpus_manager : CorpusManager, user_firstname : str)
        + save_metadata(...)
    }

    MyWindow *-- MediaManager : possède
    MyWindow *-- CorpusManager : possède
    MyWindow *-- RecordingIndicator : possède
    MyWindow *-- MetadataManager : possède

    MyWindow ..> MediaManager : démarre / arrête enregistrements
    MyWindow ..> CorpusManager : affiche et consomme phrases
    MyWindow ..> RecordingIndicator : affiche état REC
    MediaManager ..> QMediaDevices : surveille périphériques
    MediaManager ..> QMediaRecorder : enregistre vidéo
    MediaManager ..> QAudioSource : mesure niveau micro
    MetadataManager ..> MediaManager : lit les données vidéo
    MetadataManager ..> CorpusManager : lit phrase, langue et template
```

### Diagramme de dépendances entre modules

Le diagramme de dépendances complète le diagramme de classes en montrant les relations entre les fichiers Python de l'application. Contrairement au diagramme de classes, il peut représenter aussi bien des fichiers contenant des classes que des modules utilitaires.

Ce diagramme permet de visualiser quels modules dépendent les uns des autres. Il montre notamment que `main_window.py` orchestre les principaux gestionnaires, tandis que certains modules s'appuient sur des fichiers communs comme `config_loader.py`, `file_utils.py` ou `media_utils.py` pour charger la configuration, construire les chemins de fichiers ou extraire les métadonnées vidéo.

```mermaid
flowchart LR
%% =========================
%% ZONES PRINCIPALES
%% =========================

subgraph UI["Interface utilisateur"]
    main_window["main_window.py<br/><b>MyWindow</b><br/>Fenêtre principale"]
    recording_indicator["recording_indicator.py<br/><b>RecordingIndicator</b><br/>Timer + point rouge"]
end

subgraph MANAGERS["Gestionnaires métier"]
    media_manager["media_manager.py<br/><b>MediaManager</b><br/>Caméra, micro, enregistrement"]
    corpus_manager["corpus_manager.py<br/><b>CorpusManager</b><br/>Langues, phrases, progression"]
    metadata_manager["metadata_manager.py<br/><b>MetadataManager</b><br/>Création des métadonnées CSV"]
end

subgraph SERVICES["Services transversaux"]
    config_loader["config_loader.py<br/><b>load_config()</b><br/>Chargement configuration"]
    utils["utils.py<br/><b>Fonctions utilitaires</b><br/>Chemins, métadonnées vidéo, fichiers"]
end

subgraph DATA["Données manipulées"]
    config_file["config.yaml<br/>Paramètres application"]
    corpus_files["corpus/*.json<br/>Corpus linguistiques"]
    video_file["Fichier vidéo<br/>.mp4"]
    metadata_file["Fichier métadonnées<br/>.csv"]
end

%% =========================
%% DÉPENDANCES PRINCIPALES
%% =========================

main_window -->|"possède / pilote"| media_manager
main_window -->|"possède / pilote"| corpus_manager
main_window -->|"possède / pilote"| metadata_manager
main_window -->|"affiche"| recording_indicator

media_manager -->|"utilise"| utils
media_manager -->|"lit paramètres"| config_loader

corpus_manager -->|"lit paramètres"| config_loader
corpus_manager -->|"charge"| corpus_files

metadata_manager -->|"récupère données vidéo"| media_manager
metadata_manager -->|"récupère phrase + langue"| corpus_manager
metadata_manager -->|"utilise"| utils

config_loader -->|"lit"| config_file

media_manager -->|"produit"| video_file
metadata_manager -->|"produit"| metadata_file

%% =========================
%% COULEURS
%% =========================

classDef ui fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#111827;
classDef manager fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#111827;
classDef service fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#111827;
classDef data fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#111827;

class main_window,recording_indicator ui;
class media_manager,corpus_manager,metadata_manager manager;
class config_loader,utils service;
class config_file,corpus_files,video_file,metadata_file data;
```

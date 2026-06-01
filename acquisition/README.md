## Présentation générale de l'application d'acquisition

L'application d'acquisition constitue la première étape du pipeline de création du corpus audio-vidéo. Elle permet d'enregistrer un utilisateur pendant la lecture de phrases issues d'un corpus linguistique prédéfini. Chaque enregistrement produit une vidéo, accompagnée d'un fichier d'annotation contenant les métadonnées utiles : langue, phrase lue, type de template, périphériques utilisés, informations techniques du fichier vidéo et statut de validation.

Le fonctionnement général suit une logique de session. L'utilisateur renseigne d'abord son prénom, configure la caméra et le microphone, puis effectue un test micro. Une fois les périphériques validés, il choisit la langue de lecture. Le corpus correspondant est alors chargé, puis les phrases sont affichées une par une. Pour chaque phrase, l'utilisateur peut enregistrer une vidéo, la valider, la recommencer ou, après un premier échec, passer à la phrase suivante.

L'objectif principal de cette application est de garantir une acquisition structurée et exploitable des données. Les vidéos sont sauvegardées dans une arborescence organisée par langue, tandis que les annotations associées permettent ensuite à l'application d'annotation de retrouver automatiquement les informations nécessaires au traitement avec Whisper.

Le diagramme de flux ci-dessous présente le déroulement fonctionnel d'une session d'acquisition.

```mermaid
flowchart TD
    A([Début]) --> A1[Prénom utilisateur]
    A1 --> B[Configuration caméra / micro]
    B --> C[Positionnement + preview]
    C --> D[Test micro]

    D --> E{Micro OK ?}
    E -- Non --> B
    E -- Oui --> F[Choix langue]
    F --> G[Chargement corpus]

    G --> H{Session terminée ?}
    H -- Oui --> Z([Fin])
    H -- Non --> I[Affichage phrase]

    I --> J[Enregistrement]

    J --> K{Validation 1 :<br/>Oui / Non}
    K -- Oui --> L[Sauvegarde vidéo + CSV]
    K -- Non --> M[Réenregistrement]

    M --> N{Validation suivante :<br/>Oui / Non / Skip}
    N -- Oui --> L
    N -- Non --> M
    N -- Skip --> O[Passage à la phrase suivante]

    O --> H
    L --> H
```

## Architecture de l'application d'acquisition

L'application d'acquisition est structurée autour de plusieurs composants ayant chacun une responsabilité précise. La fenêtre principale coordonne le déroulement de la session, tandis que des gestionnaires spécialisés prennent en charge les périphériques audio-vidéo, le corpus, l'indicateur d'enregistrement et la sauvegarde des annotations.

Cette organisation permet de séparer la logique d'interface, la logique métier et les traitements techniques. Elle facilite également l'évolution du projet, notamment l'ajout de l'application d'annotation, qui pourra réutiliser certains modules ou certaines données produites par l'acquisition.

### Diagramme de classes

Le diagramme de classes présente les principales classes de l'application d'acquisition et leurs relations. Il met en évidence le rôle central de `MyWindow`, qui possède et coordonne les différents gestionnaires : `MediaManager`, `CorpusManager`, `RecordingIndicator` et `AnnotationManager`.

Chaque classe est représentée avec ses principaux attributs et méthodes afin de donner une vue synthétique de l'organisation interne du code. Ce diagramme ne représente que les véritables classes Python du projet ; les fichiers contenant uniquement des fonctions utilitaires sont volontairement exclus de ce diagramme.

```mermaid
classDiagram

    class MyWindow {
        - media_manager : MediaManager
        - corpus_manager : CorpusManager
        - recording_indicator : RecordingIndicator
        - annotation_manager : AnnotationManager
        - is_recording : bool

        + setup_managers()
        + connect_signals()
        + load_languages_into_combobox()
        + display_current_sentence()
        + can_start_recording() : bool
        + button_record_clicked()
        + start_recording_flow()
        + stop_recording_flow()
        + finalize_recording()
        + button_test_micro_clicked()
    }

    class MediaManager {
        + micro_level_changed : Signal

        - camera : QCamera
        - audio_input : QAudioInput
        - capture_session : QMediaCaptureSession
        - recorder : QMediaRecorder
        - media_devices : QMediaDevices

        - file_name : str
        - video_filepath : Path
        - annotation_filepath : Path
        - micro_test_is_running : bool

        + setup()
        + load_microphones()
        + load_cameras()
        + refresh_microphones()
        + refresh_cameras()
        + get_selected_microphone()
        + get_selected_camera()
        + has_selected_microphone() : bool
        + has_selected_camera() : bool
        + start_recording(language_code) : bool
        + stop_recording()
        + start_micro_test(audio_device)
        + stop_micro_test()
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

        + load_languages() : list
        + select_language(index) : bool
        + prepare_session() : bool
        + get_current_sentence() : str
        + consume_current_sentence() : bool
        + is_session_finished() : bool
        + get_sentence_counter_text() : str
    }

    class RecordingIndicator {
        - label_record_timer : QLabel
        - label_record_dot : QLabel
        - record_seconds : int
        - blink_visible : bool

        + show()
        + hide()
        + start()
        + stop()
        + blink_dot()
        + update_record_timer()
    }

    class AnnotationManager {
        - machine_name : str
        - operating_system : str
        - fieldnames : list

        + save_recording_annotation(media_manager : MediaManager, corpus_manager : CorpusManager)
        + save_annotation(...)
    }

    MyWindow *-- MediaManager : possède
    MyWindow *-- CorpusManager : possède
    MyWindow *-- RecordingIndicator : possède
    MyWindow *-- AnnotationManager : possède

    AnnotationManager ..> MediaManager : lit les données vidéo
    AnnotationManager ..> CorpusManager : lit la phrase et la langue
```

### Diagramme de dépendances entre modules

Le diagramme de dépendances complète le diagramme de classes en montrant les relations entre les fichiers Python de l'application. Contrairement au diagramme de classes, il peut représenter aussi bien des fichiers contenant des classes que des modules utilitaires.

Ce diagramme permet de visualiser quels modules dépendent les uns des autres. Il montre notamment que `main_window.py` orchestre les principaux gestionnaires, tandis que certains modules s'appuient sur des fichiers communs comme `config_loader.py`, `file_utils.py` ou `media_utils.py` pour charger la configuration, construire les chemins de fichiers ou extraire les métadonnées vidéo.

    ```mermaid
    flowchart TD
    MW[main_window.py<br/>MyWindow]

    MM[media_manager.py<br/>MediaManager]
    CM[corpus_manager.py<br/>CorpusManager]
    AM[annotation_manager.py<br/>AnnotationManager]
    RI[recording_indicator.py<br/>RecordingIndicator]

    CL[config_loader.py<br/>load_config()]
    FU[file_utils.py<br/>fonctions de chemins]
    MU[media_utils.py<br/>fonctions média]

    MW --> MM
    MW --> CM
    MW --> AM
    MW --> RI

    MM --> CL
    CM --> CL

    MM --> FU
    MM --> MU
    AM --> FU
    AM --> MU
```
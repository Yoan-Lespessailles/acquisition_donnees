# QMainWindow est la classe de base de la fenêtre principale.
from PySide6.QtWidgets import QMainWindow

# Slot permet de déclarer explicitement certaines méthodes connectées aux signaux Qt.
from PySide6.QtCore import Slot

# Interface générée depuis Qt Designer.
from ui.ui_main_pyside6 import Ui_MainWindow

# Gestion de toute la partie caméra / micro / preview / enregistrement.
from media_manager import MediaManager

# Gestion du corpus, des langues, des phrases et du compteur.
from corpus_manager import CorpusManager

# Gestion de l'affichage REC : chrono + point rouge clignotant.
from recording_indicator import RecordingIndicator

# Gestion du fichier d'annotations
from annotation_manager import AnnotationManager

from utils.media_utils import extract_video_metadata

class MyWindow(QMainWindow, Ui_MainWindow):
    """
    Fenêtre principale de l'application.

    Cette classe ne doit pas contenir toute la logique technique.
    Son rôle principal est :
        - initialiser l'interface ;
        - connecter les boutons et ComboBox ;
        - coordonner MediaManager, CorpusManager et RecordingIndicator.
    """

    def __init__(self):
        """
        Initialise la fenêtre principale.
        """

        # Initialise la fenêtre Qt.
        super().__init__()

        self.setWindowTitle("Prototype Application")
        self.resize(600, 400)

        # Charge l'interface créée avec Qt Designer
        self.setupUi(self)

        self.setStyleSheet("""
                           
            #button_record[recording="false"], #button_record[recording="true"]{   
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
            }

            #button_record[recording="false"]:hover {
                background-color: #006609;
            }

            #button_record[recording="true"]:hover {
                background-color: #C70000;
            }

            #button_record[recording="false"]:pressed {
                background-color: #005209;
            }
                           
            #button_record[recording="true"]:pressed {
                background-color: #A60303;
            }
                           
            #button_record[recording="false"] {
                background-color: #00820A;
            }

            #button_record[recording="true"] {
                background-color: #D10000 ;
            }
                           
            #button_record:disabled {
            background-color: #ABABAB ;
            color: #F0F0F0;
            }
        
        """)

        #ABABAB

        # Active le QSS
        self.button_record.setProperty("recording", False)
    
      # Indique si un enregistrement est actuellement en cours.
        self.is_recording = False

        # Initialise les gestionnaires spécialisés.
        self.setup_managers()

        # Connecte les signaux Qt aux méthodes Python.
        self.connect_signals()

        # Charge les langues disponibles dans la ComboBox.
        self.load_languages_into_combobox()

        # Affiche la première phrase si un corpus est disponible.
        self.display_current_sentence()

       
    # ========== INITIALISATION DES GESTIONNAIRES ==========

    def setup_managers(self):
        """
        Initialise les classes spécialisées utilisées par la fenêtre.
        """

        # Gère les micros, caméras, preview et enregistrements.
        self.media_manager = MediaManager(self.select_micro, self.select_camera, self.area_preview)

        # Prépare toute la partie multimédia.
        self.media_manager.setup()

        # Gère les langues, corpus, phrases et compteurs.
        self.corpus_manager = CorpusManager()

        # Gère l'affichage du timer REC et du point rouge.
        self.recording_indicator = RecordingIndicator(self.label_record_timer, self.label_record_dot)

        self.annotation_manager = AnnotationManager()

    # -----------------------------------------------------------------

        
    # ========== CONNEXION DES SIGNAUX ==========
        
    def connect_signals(self):
        """
        Connecte les signaux Qt aux méthodes de l'application.
        """

        # Bouton principal d'enregistrement.
        self.button_record.clicked.connect(self.button_record_clicked)

        # Changement de micro sélectionné.
        self.select_micro.currentIndexChanged.connect(
            self.media_manager.change_microphone
        )

        # Changement de caméra sélectionnée.
        self.select_camera.currentIndexChanged.connect(
            self.media_manager.change_camera
        )

        # Changement de langue sélectionnée.
        self.select_language.currentIndexChanged.connect(
            self.language_changed
        )

        # Détection automatique d'un changement dans la liste des micros.
        self.media_manager.media_devices.audioInputsChanged.connect(self.media_manager.refresh_microphones)

        # Détection automatique d'un changement dans la liste des caméras.
        self.media_manager.media_devices.videoInputsChanged.connect(self.media_manager.refresh_cameras)

    # -----------------------------------------------------------------


    # ========== LANGUES ET CORPUS ========== 
    def load_languages_into_combobox(self):
        """
        Charge les langues disponibles dans la ComboBox de l'interface.
        """

        # Vide la ComboBox avant de la remplir.
        self.select_language.clear()

        # Demande au CorpusManager la liste des langues disponibles.
        languages = self.corpus_manager.load_languages()

        # Ajoute chaque langue dans la ComboBox.
        for language_name, language_code in languages:
            self.select_language.addItem(language_name, language_code)

        # Si aucune langue n'est disponible, on désactive le bouton d'enregistrement.
        if not languages:
            self.button_record.setEnabled(False)
            self.label_sentence.setText("Aucun corpus disponible")
            self.label_cpt_sentence.setText("0/0")
            return

        # Sélectionne la première langue par défaut.
        self.corpus_manager.select_language(0)

        # Prépare le corpus de la langue sélectionnée.
        session_ready = self.corpus_manager.prepare_session()

        # Active ou désactive le bouton selon le résultat.
        self.button_record.setEnabled(session_ready)


    @Slot(int)
    def language_changed(self, index):
        """
        Réagit au changement de langue dans la ComboBox.
        """

        # Informe le CorpusManager de la langue sélectionnée.
        self.corpus_manager.select_language(index)

        # Charge et prépare le corpus de cette langue.
        session_ready = self.corpus_manager.prepare_session()

        # Met à jour l'affichage.
        self.display_current_sentence()

        # Active le bouton seulement si le corpus est prêt.
        self.button_record.setEnabled(session_ready)


    def display_current_sentence(self):
        """
        Affiche la phrase courante et le compteur de phrases.
        """

        # Récupère la phrase courante depuis le CorpusManager.
        sentence = self.corpus_manager.get_current_sentence()

        # Affiche la phrase dans le label prévu.
        self.label_sentence.setText(sentence)

        # Affiche le compteur.
        self.label_cpt_sentence.setText(self.corpus_manager.get_sentence_counter_text())

        # Lorsque toutes les phrases sont consommées, on désactive le bouton.
        self.button_record.setEnabled(not self.corpus_manager.is_session_finished())       
    
    # -----------------------------------------------------------------


    # ========== VERIFICATIONS AVANT ENREGISTREMENT ==========
    
    def can_start_recording(self):
        """
        Vérifie si toutes les conditions sont réunies pour démarrer un enregistrement.
        """

        # Vérifie qu'un micro est sélectionné.
        if not self.media_manager.has_selected_microphone():
            print("Aucun micro sélectionné")
            return False

        # Vérifie qu'une caméra est sélectionnée.
        if not self.media_manager.has_selected_camera():
            print("Aucune caméra sélectionnée")
            return False

        # Vérifie qu'une langue est sélectionnée.
        if self.corpus_manager.language_selected is None: # type: ignore
            print("Aucune langue sélectionnée")
            return False

        # Vérifie qu'il reste au moins une phrase à enregistrer.
        if self.corpus_manager.is_session_finished():
            print("Toutes les phrases ont déjà été enregistrées")
            return False

        # Si tout est bon, on peut enregistrer.
        return True

    # -----------------------------------------------------------------

    # ========== BOUTON D'ENREGISTREMENT ==========

    @Slot()
    def button_record_clicked(self):
        """
        Gère le clic sur le bouton d'enregistrement.

        Si aucun enregistrement n'est en cours :
            - démarre l'enregistrement.

        Si un enregistrement est déjà en cours :
            - arrête l'enregistrement ;
            - consomme la phrase courante ;
            - affiche la phrase suivante.
        """

        # Si aucun enregistrement n'est en cours, on démarre.
        if not self.is_recording:
            self.start_recording_flow()
            return

        # Sinon, on arrête l'enregistrement en cours.
        self.stop_recording_flow()
    


    def start_recording_flow(self):
        """
        Démarre toute la séquence d'enregistrement côté interface.
        """

        # Vérifie les conditions nécessaires avant d'enregistrer.
        if not self.can_start_recording():
            return

        # Récupère le code de langue courant.
        language_code = self.corpus_manager.language_selected[1] # type: ignore

        # Demande au MediaManager de démarrer l'enregistrement.
        recording_started = self.media_manager.start_recording(language_code)

        # Si l'enregistrement n'a pas démarré, on ne change pas l'interface.
        if not recording_started:
            return

        # L'application passe en état "enregistrement".
        self.is_recording = True

        # Modifie le texte du bouton.
        self.button_record.setText("Stop recording")

        # Ajoute une propriété Qt pour appliquer un style QSS spécifique si besoin.
        self.button_record.setProperty("recording", True)

        # Force Qt à recalculer le style du bouton.
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # Empêche de changer de micro pendant l'enregistrement.
        self.select_micro.setEnabled(False)

        # Empêche de changer de caméra pendant l'enregistrement.
        self.select_camera.setEnabled(False)

        # Empêche de changer de langue pendant l'enregistrement.
        self.select_language.setEnabled(False)

        # Affiche et lance l'indicateur REC.
        self.recording_indicator.show()
        self.recording_indicator.start()


    def stop_recording_flow(self):
        """
        Arrête toute la séquence d'enregistrement côté interface.
        """

        # Demande au MediaManager d'arrêter l'enregistrement.
        self.media_manager.stop_recording()

        # L'application n'est plus en état "enregistrement".
        self.is_recording = False

        # Remet le texte initial du bouton.
        self.button_record.setText("Start recording")

        # Retire la propriété de style QSS liée à l'enregistrement.
        self.button_record.setProperty("recording", False)

        # Force Qt à recalculer le style du bouton.
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # Réactive les sélecteurs.
        self.select_micro.setEnabled(True)
        self.select_camera.setEnabled(True)
        self.select_language.setEnabled(True)

        # Arrête et masque l'indicateur REC.
        self.recording_indicator.stop()
        self.recording_indicator.hide()

       
        file_name = self.media_manager.file_name
        video_path = self.media_manager.recording_output_location.toLocalFile()
        annotation_file_path = self.media_manager.annotation_filepath
        
        sentence = self.corpus_manager.current_sentence
        template_type = self.corpus_manager.current_template_type
        language_code = self.corpus_manager.language_selected[1] # type: ignore
        language_name = self.corpus_manager.language_selected[0] # type: ignore

        selected_camera = self.media_manager.get_selected_camera()
        selected_microphone = self.media_manager.get_selected_microphone()
        camera_name = selected_camera.description() if selected_camera is not None else "unknown"
        microphone_name = selected_microphone.description() if selected_microphone is not None else "unknown"

        video_metadata = extract_video_metadata(self.media_manager.video_filepath)

        self.annotation_manager.save_annotation(
            annotation_file_path, 
            file_name,
            video_path,
            language_code,
            language_name,
            sentence,
            template_type,
            camera_name,
            microphone_name,
            video_metadata["file_size_bytes"],
            video_metadata["format_name"],
            video_metadata["duration_seconds"],
            video_metadata["video_codec"],
            video_metadata["video_width"],
            video_metadata["video_height"],
            video_metadata["video_fps"],
            video_metadata["video_bitrate"],
            video_metadata["audio_codec"],
            video_metadata["audio_sample_rate"],
            video_metadata["audio_channels"],
            video_metadata["audio_bitrate"]
            )

        # Supprime du corpus la phrase qui vient d'être lue.
        self.corpus_manager.consume_current_sentence()

        # Affiche la phrase suivante.
        self.display_current_sentence()

    # -----------------------------------------------------------------
# QMainWindow est la classe de base de la fenêtre principale.
from PySide6.QtWidgets import QMainWindow

# Slot permet de déclarer explicitement certaines méthodes connectées aux signaux Qt.
from PySide6.QtCore import Slot, QTimer, Qt

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

            #button_test_micro[testing="false"], #button_test_micro[testing="true"] {
                color: black;
                border: none;
                border-radius: 10px;

                padding: 6px 12px;
                text-align: center;
            }

            #button_test_micro[testing="false"] {
                background-color: #2ECC71
            }
                           
            #button_test_micro[testing="false"]:hover {
                background-color: #0FBD5A
            }
                           
            #button_test_micro[testing="false"]:pressed {
                background-color: #02A849
            }
                           
            #button_test_micro[testing="true"] {
                background-color: #FFE857
            }
                           
            #button_test_micro[testing="true"]:hover {
                background-color: #FFE200
            }
                           
            #button_test_micro[testing="true"]:pressed {
                background-color: #DBC200
            }
                           
            #progressbar_micro_level {
                border: 1px solid #555555;
                border-radius: 6px;
                background-color: #E5E5E5;
            }

            #progressbar_micro_level::chunk {
                background-color: #2ECC71;
                border-radius: 5px;
            }
        
        """)

        # Centre le bouton horizontalement dans le layout de area_micro_test.
        self.area_micro_test.layout().setAlignment(self.button_test_micro, Qt.AlignmentFlag.AlignHCenter) # type: ignore

        # Enlève le texte sur la progressbar
        self.progressbar_micro_level.setTextVisible(False)

        # Active le QSS
        self.button_record.setProperty("recording", False)
        self.button_test_micro.setProperty("testing", False)

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
        self.select_micro.currentIndexChanged.connect(self.media_manager.change_microphone)

        # Changement de caméra sélectionnée.
        self.select_camera.currentIndexChanged.connect(self.media_manager.change_camera)

        # Changement de langue sélectionnée.
        self.select_language.currentIndexChanged.connect(self.language_changed)

        # Détection automatique d'un changement dans la liste des micros.
        self.media_manager.media_devices.audioInputsChanged.connect(self.media_manager.refresh_microphones)

        # Détection automatique d'un changement dans la liste des caméras.
        self.media_manager.media_devices.videoInputsChanged.connect(self.media_manager.refresh_cameras)

        # Bouton de test micro
        self.button_test_micro.clicked.connect(self.button_test_micro_clicked)

        # Quand MediaManager calcule un nouveau niveau micro,
        # on met à jour la ProgressBar.
        self.media_manager.micro_level_changed.connect(self.update_micro_level)

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

        # Si l'utilisateur n'a pas désactiver le test micro, on l'arrête pour éviter des conflits
        if self.media_manager.micro_test_is_running:
            self.media_manager.stop_micro_test()

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


        # Attend un peu avant de lire le fichier MP4.
        # Cela laisse le temps à Qt de finaliser le conteneur vidéo.
        QTimer.singleShot(500, self.finalize_recording)


       
    def finalize_recording(self):
        """
        Finalise le traitement après l'arrêt de l'enregistrement.

        Cette méthode est appelée après un court délai pour laisser le temps
        au fichier MP4 d'être complètement écrit.
        """
        
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
            video_metadata["video_format"],
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


    # ========== BOUTON DE TEST MICRO ==========
    @Slot()
    def button_test_micro_clicked(self):
        """
        Démarre ou arrête le test micro selon l'état actuel du MediaManager.
        """

        # Si le test micro est déjà en cours, on l'arrête.
        if self.media_manager.micro_test_is_running:
            self.media_manager.stop_micro_test()
            self.button_test_micro.setText("Tester le micro")

            self.button_test_micro.setProperty("testing", False)

            # Force Qt à recalculer le style du bouton.
            self.update_style(self.button_test_micro)

            # Débloque la sélection de micro
            self.select_micro.setEnabled(True)

            return

        # Sinon, on récupère le micro sélectionné.
        micro = self.media_manager.get_selected_microphone()

        # On démarre le test micro.
        self.media_manager.start_micro_test(micro)
        self.button_test_micro.setText("Arrêter le test micro")

        self.button_test_micro.setProperty("testing", True)
        
        # Force Qt à recalculer le style du bouton.
        self.update_style(self.button_test_micro)
        
        # Bloque la sélection de micro
        self.select_micro.setEnabled(False)
    

    @Slot(int)
    def update_micro_level(self, level):
        """
        Met à jour la barre de niveau micro avec la valeur reçue.
        """

        self.progressbar_micro_level.setValue(level)

    # -----------------------------------------------------------------

    def update_style(self, widget):
        """
        Force Qt à réappliquer le style QSS d'un widget.

        Cette méthode est utile quand on change une propriété dynamique
        utilisée dans le QSS, par exemple :

        self.button_test_micro.setProperty("testing", True)

        Qt ne rafraîchit pas toujours automatiquement le style après ce type
        de changement. On force donc le widget à être "dé-stylé", puis
        "re-stylé".
        """

        # Retire temporairement le style actuellement appliqué au widget.
        widget.style().unpolish(widget)

        # Réapplique le style au widget en tenant compte de ses propriétés actuelles.
        widget.style().polish(widget)
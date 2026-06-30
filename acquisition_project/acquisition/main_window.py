# QMainWindow est la classe de base de la fenêtre principale
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QMessageBox, QDialogButtonBox, QInputDialog, QApplication, QLineEdit

# Slot permet de déclarer explicitement certaines méthodes connectées aux signaux Qt
from PySide6.QtCore import Slot, QTimer, Qt

# QFontMetrics permet de mesurer la place prise par un texte avec une police donnée
# On l'utilise pour choisir automatiquement une taille de police qui rentre dans un QLabel
from PySide6.QtGui import QFontMetrics

# Interface générée depuis Qt Designer
from acquisition.ui.ui_main_pyside6 import Ui_MainWindow

# Gestion de toute la partie caméra / micro / preview / enregistrement
from acquisition.media_manager import MediaManager

# Gestion du corpus, des langues, des phrases et du compteur
from acquisition.corpus_manager import CorpusManager

# Gestion de l'affichage REC : chrono + point rouge clignotant
from acquisition.recording_indicator import RecordingIndicator

# Gestion du fichier de métadonnées
from acquisition.metadata_manager import MetadataManager


class MyWindow(QMainWindow, Ui_MainWindow):
    """
    Fenêtre principale de l'application.

    Cette classe ne doit pas contenir toute la logique technique.
    Son rôle principal est :
        - initialiser l'interface ;
        - connecter les boutons et ComboBox ;
        - coordonner MediaManager, CorpusManager et RecordingIndicator.
    """

    def __init__(self, user_firstname=None):
        """
        Initialise la fenêtre principale.

        Paramètres :
            user_firstname : prénom fourni en ligne de commande.
                Si None, une fenêtre de saisie sera affichée.
        """

        # Initialise la fenêtre Qt
        super().__init__()

        self.resize(600, 400)

        # Charge l'interface créée avec Qt Designer
        self.setupUi(self)
        self.setWindowTitle("AVDataCollector")

        # Si un prénom est fourni en ligne de commande, on l'utilise directement
        if user_firstname is not None and user_firstname.strip():
            self.user_firstname = user_firstname.strip().capitalize()
            print("Prénom de l'utilisateur : " + user_firstname)

        # Sinon, on demandera le prénom avec une fenêtre Qt après le lancement
        else:
            QTimer.singleShot(0, self.ask_user_firstname)

        # Le QSS garde les couleurs, bordures et espacements
        # Les tailles de police restent gérées en Python par le système responsive
        self.setStyleSheet("""
                           
            #button_record[recording="false"], #button_record[recording="true"]{   
                color: white;
                border: none;
                border-radius: 10px;
                padding: 4px;
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

        # Configure les tailles, alignements et comportements responsive
        # Cette méthode prépare les widgets, puis applique un premier calcul de taille
        self.configure_responsive_ui()

        # Active le QSS
        self.button_record.setProperty("recording", False)
        self.button_test_micro.setProperty("testing", False)

        # Indique si un enregistrement est actuellement en cours
        self.is_recording = False
        
        # Compteur indiquant le nombre d'essais d'enregistrement (fait apparaitre le bouton skip au pour de 2)
        self.cpt_retry_register = 0

        # Initialise les gestionnaires spécialisés
        self.setup_managers()

        # Connecte les signaux Qt aux méthodes Python
        self.connect_signals()

        # Charge les langues disponibles dans la ComboBox
        self.load_languages_into_combobox()

        # Affiche la première phrase si un corpus est disponible
        self.display_current_sentence()


    def configure_responsive_ui(self):
        """
        Configure l'interface pour que les textes suivent la taille de la fenêtre.
        """

        # Widgets texte simples : ils partagent une taille de police de base
        # On les garde séparés des ComboBox et boutons car ces widgets ont aussi
        # besoin d'une hauteur minimale adaptée
        self._standard_text_widgets = [
            self.label_select_language,
            self.label_micro,
            self.label_select_camera,
            self.label_micro_state,
            self.label_cpt_sentence,
            self.label_record_timer,
        ]

        # ComboBox qui doivent suivre la taille de la fenêtre
        # La police et la hauteur sont recalculées ensemble
        self._responsive_combo_boxes = [
            self.select_micro,
            self.select_camera,
            self.select_language,
        ]

        # Boutons responsives
        # button_record est traité plus bas avec une taille plus imposante
        self._responsive_buttons = [
            self.button_test_micro,
            self.button_record,
        ]

        # Les labels courts peuvent revenir à la ligne si la fenêtre devient étroite
        # Leur QSizePolicy leur permet de s'étendre horizontalement sans imposer
        # une largeur fixe au layout
        for label in self._standard_text_widgets :
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # La phrase à lire est l'élément principal de l'interface :
        # elle prend l'espace disponible et reste centrée dans sa zone
        self.label_sentence.setWordWrap(True)
        self.label_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sentence.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.label_sentence.setMinimumHeight(70)

        # Hauteurs minimales de départ
        # Elles seront ensuite ajustées plus finement dans update_responsive_text_sizes()
        self.button_test_micro.setMinimumHeight(34)
        self.button_record.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )
        self.button_record.setMinimumHeight(32)
        self.progressbar_micro_level.setFixedHeight(20)


        # Centre le bouton de test micro dans sa zone si le layout existe bien
        layout_micro_test = self.area_micro_test.layout()
        if layout_micro_test is not None:
            layout_micro_test.setAlignment(
                self.button_test_micro,
                Qt.AlignmentFlag.AlignHCenter,
            )

        # Premier calcul responsive
        # Il sera refait après l'affichage réel de la fenêtre dans showEvent()
        self.update_responsive_text_sizes()


    def resizeEvent(self, event):
        """
        Recalcule les tailles de texte à chaque redimensionnement de la fenêtre.
        """

        super().resizeEvent(event)
        if hasattr(self, "_standard_text_widgets"):
            # Chaque changement de taille de fenêtre relance le calcul des polices
            self.update_responsive_text_sizes()


    def showEvent(self, event):
        """
        Applique le responsive une fois que Qt connaît la géométrie réelle.
        """

        super().showEvent(event)
        if hasattr(self, "_standard_text_widgets"):
            # Au lancement, Qt ne connaît pas toujours les tailles finales des widgets
            # pendant __init__. singleShot(0, ...) reporte le calcul juste après le
            # premier passage de layout, lorsque les dimensions sont stabilisées
            QTimer.singleShot(0, self.update_responsive_text_sizes)


    def update_responsive_text_sizes(self):
        """
        Adapte les tailles de police aux dimensions actuelles de la fenêtre.
        """

        # Echelle globale basée sur la taille initiale créée dans Qt Designer
        # La valeur est bornée pour éviter des textes trop petits ou trop grands
        scale = max(0.75, min(1.45, min(self.width() / 820, self.height() / 595)))

        # Tailles de police calculées par catégorie de widgets
        # Le bouton principal d'enregistrement est volontairement plus grand
        standard_size = round(10 * scale)
        counter_size = round(9 * scale)
        combo_size = round(10 * scale)
        test_button_size = round(11 * scale)
        record_button_size = round(12 * scale)
        record_dot_size = max(12, round(20 * scale))

        # Labels standards : police de base, avec une taille légèrement plus discrète
        # pour le compteur de phrases
        for widget in self._standard_text_widgets:
            font_size = standard_size
            if widget is self.label_cpt_sentence:
                font_size = counter_size

            self.set_widget_font_size(widget, font_size)

        # ComboBox : on adapte la police mais aussi la hauteur, sinon le texte peut
        # sembler compressé verticalement lorsque la police augmente
        for combo_box in self._responsive_combo_boxes:
            self.set_widget_font_size(combo_box, combo_size)
            combo_box.setMinimumHeight(max(26, round(30 * scale)))

        # Boutons : le bouton d'enregistrement reçoit une taille plus imposante
        # que le bouton de test micro pour rester visuellement prioritaire
        for button in self._responsive_buttons:
            if button is self.button_record:
                font_size = record_button_size
                button.setMinimumHeight(max(32, round(34 * scale)))
                button.setMaximumHeight(max(36, round(42 * scale)))
                button.setMinimumWidth(max(170, round(190 * scale)))
                button.setMaximumWidth(max(220, round(300 * scale)))
            else:
                font_size = test_button_size
                button.setMinimumHeight(max(32, round(38 * scale)))

            self.set_widget_font_size(button, font_size)

        # Le rond rouge REC suit aussi la taille de la fenêtre
        self.set_record_dot_size(record_dot_size)

        # La phrase principale est ajustée selon l'espace réellement disponible
        # dans son QLabel, pas seulement selon la taille globale de la fenêtre
        self.fit_label_text(
            self.label_sentence,
            min_size=max(10, round(12 * scale)),
            max_size=max(18, round(28 * scale)),
        )


    def set_widget_font_size(self, widget, point_size):
        """
        Applique une taille de police sans changer la famille ni le gras existants.
        """

        font = widget.font()

        # Evite de réappliquer exactement la même taille à chaque resize
        if font.pointSize() == point_size:
            return

        font.setPointSize(point_size)
        widget.setFont(font)


    def set_record_dot_size(self, size):
        """
        Ajuste le rond rouge d'enregistrement en gardant une forme circulaire.
        """

        # setFixedSize force la largeur et la hauteur à rester identiques
        self.label_record_dot.setFixedSize(size, size)

        # Le rayon vaut la moitié de la taille : le QLabel reste donc un cercle
        self.label_record_dot.setStyleSheet(
            f"background-color: red; border-radius: {size // 2}px;"
        )


    def fit_label_text(self, label, min_size, max_size):
        """
        Choisit la plus grande taille de police qui tient dans le QLabel.
        """

        text = label.text()
        if not text:
            # Si le label est vide, on garde la taille maximale possible
            self.set_widget_font_size(label, max_size)
            return

        # contentsRect correspond à la zone réellement utilisable par le texte
        # On retire quelques pixels pour éviter que le texte colle aux bords
        contents = label.contentsRect()
        available_width = max(20, contents.width() - 8)
        available_height = max(20, contents.height() - 8)

        # Flags utilisés par QFontMetrics pour mesurer le texte comme Qt l'affichera :
        # centré et autorisé à revenir à la ligne
        text_flags = (
            Qt.TextFlag.TextWordWrap.value
            | Qt.AlignmentFlag.AlignCenter.value
        )

        best_size = min_size

        # On teste les tailles de la plus grande à la plus petite
        # La première qui tient dans la hauteur disponible devient la taille retenue
        for point_size in range(max_size, min_size - 1, -1):
            font = label.font()
            font.setPointSize(point_size)
            font.setBold(True)
            metrics = QFontMetrics(font)
            text_rect = metrics.boundingRect(
                0,
                0,
                available_width,
                10000,
                text_flags,
                text,
            )

            if text_rect.height() <= available_height:
                best_size = point_size
                break

        # Applique la taille retenue à la phrase principale
        font = label.font()
        font.setPointSize(best_size)
        font.setBold(True)
        label.setFont(font)

       
    # ========== INITIALISATION DES GESTIONNAIRES ==========

    def setup_managers(self):
        """
        Initialise les classes spécialisées utilisées par la fenêtre.
        """

        # Gère les micros, caméras, preview et enregistrements
        self.media_manager = MediaManager(self.select_micro, self.select_camera, self.area_preview)

        # Prépare toute la partie multimédia
        self.media_manager.setup()

        # Gère les langues, corpus, phrases et compteurs
        self.corpus_manager = CorpusManager()

        # Gère l'affichage du timer REC et du point rouge
        self.recording_indicator = RecordingIndicator(self.label_record_timer, self.label_record_dot)

        self.metadata_manager = MetadataManager()

    # -----------------------------------------------------------------

        
    # ========== CONNEXION DES SIGNAUX ==========
        
    def connect_signals(self):
        """
        Connecte les signaux Qt aux méthodes de l'application.
        """

        # Bouton principal d'enregistrement
        self.button_record.clicked.connect(self.button_record_clicked)

        # Changement de micro sélectionné
        self.select_micro.currentIndexChanged.connect(self.media_manager.change_microphone)

        # Changement de caméra sélectionnée
        self.select_camera.currentIndexChanged.connect(self.media_manager.change_camera)

        # Changement de langue sélectionnée
        self.select_language.currentIndexChanged.connect(self.language_changed)

        # Détection automatique d'un changement dans la liste des micros
        self.media_manager.media_devices.audioInputsChanged.connect(self.media_manager.refresh_microphones)

        # Détection automatique d'un changement dans la liste des caméras
        self.media_manager.media_devices.videoInputsChanged.connect(self.media_manager.refresh_cameras)

        # Bouton de test micro
        self.button_test_micro.clicked.connect(self.button_test_micro_clicked)

        # Quand MediaManager calcule un nouveau niveau micro,
        # on met à jour la ProgressBar
        self.media_manager.micro_level_changed.connect(self.update_micro_level)

    # -----------------------------------------------------------------


    # ========== LANGUES ET CORPUS ========== 
    def load_languages_into_combobox(self):
        """
        Charge les langues disponibles dans la ComboBox de l'interface.
        """

        # Vide la ComboBox avant de la remplir
        self.select_language.clear()

        # Demande au CorpusManager la liste des langues disponibles
        languages = self.corpus_manager.load_languages()

        # Ajoute chaque langue dans la ComboBox
        for language_name, language_code, _ in languages:
            self.select_language.addItem(language_name, language_code)

        # Si aucune langue n'est disponible, on désactive le bouton d'enregistrement
        if not languages:
            self.button_record.setEnabled(False)
            self.label_sentence.setText("Aucun corpus disponible")
            self.label_cpt_sentence.setText("0/0")

            # Le message d'erreur remplace une phrase normale :
            # on relance donc le calcul pour adapter sa taille au label
            self.update_responsive_text_sizes()
            return

        # Sélectionne la première langue par défaut
        self.corpus_manager.select_language(0)

        # Prépare le corpus de la langue sélectionnée
        session_ready = self.corpus_manager.prepare_session()

        # Active ou désactive le bouton selon le résultat
        self.button_record.setEnabled(session_ready)


    @Slot(int)
    def language_changed(self, index):
        """
        Réagit au changement de langue dans la ComboBox.

        Paramètres :
            index : position de la langue sélectionnée dans la ComboBox.
        """

        # Informe le CorpusManager de la langue sélectionnée
        self.corpus_manager.select_language(index)

        # Charge et prépare le corpus de cette langue
        session_ready = self.corpus_manager.prepare_session()

        # Met à jour l'affichage
        self.display_current_sentence()

        # Active le bouton seulement si le corpus est prêt
        self.button_record.setEnabled(session_ready)


    def display_current_sentence(self):
        """
        Affiche la phrase courante et le compteur de phrases.
        """

        # Récupère la phrase courante depuis le CorpusManager
        sentence = self.corpus_manager.get_current_sentence()

        # Affiche la phrase dans le label prévu
        self.label_sentence.setText(sentence)

        # Affiche le compteur
        self.label_cpt_sentence.setText(self.corpus_manager.get_sentence_counter_text())

        # Le texte peut avoir une longueur très différente d'une phrase à l'autre
        # On recalcule donc la taille de police après chaque changement de phrase
        self.update_responsive_text_sizes()

        # Lorsque toutes les phrases sont consommées, on désactive le bouton
        self.button_record.setEnabled(not self.corpus_manager.is_session_finished())       
    
    # -----------------------------------------------------------------


    # ========== VERIFICATIONS AVANT ENREGISTREMENT ==========
    
    def can_start_recording(self):
        """
        Vérifie si toutes les conditions sont réunies pour démarrer un enregistrement.
        """

        # Vérifie qu'un micro est sélectionné
        if not self.media_manager.has_selected_microphone():
            print("Aucun micro sélectionné")
            return False

        # Vérifie qu'une caméra est sélectionnée
        if not self.media_manager.has_selected_camera():
            print("Aucune caméra sélectionnée")
            return False

        # Vérifie qu'une langue est sélectionnée
        if self.corpus_manager.language_selected is None: # type: ignore
            print("Aucune langue sélectionnée")
            return False

        # Vérifie qu'il reste au moins une phrase à enregistrer
        if self.corpus_manager.is_session_finished():
            print("Toutes les phrases ont déjà été enregistrées")
            return False

        # Si tout est bon, on peut enregistrer
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

            # Remet la propriété QSS du bouton de test dans son état inactif
            self.button_test_micro.setProperty("testing", False)
            self.button_test_micro.setText("Tester le micro")

            # Force Qt à recalculer le style du bouton
            self.update_style(self.button_test_micro)


        # Si aucun enregistrement n'est en cours, on démarre
        if not self.is_recording:
            self.start_recording_flow()
            return

        # Sinon, on arrête l'enregistrement en cours
        self.stop_recording_flow()
    


    def start_recording_flow(self):
        """
        Démarre toute la séquence d'enregistrement côté interface.
        """

        # Vérifie les conditions nécessaires avant d'enregistrer
        if not self.can_start_recording():
            return

        # Récupère le code de langue courant
        language_code = self.corpus_manager.language_selected[1] # type: ignore

        # Demande au MediaManager de démarrer l'enregistrement
        recording_started = self.media_manager.start_recording(language_code)

        # Si l'enregistrement n'a pas démarré, on ne change pas l'interface
        if not recording_started:
            return

        # L'application passe en état "enregistrement"
        self.is_recording = True

        # Modifie le texte du bouton
        self.button_record.setText("Stop recording")

        # Ajoute une propriété Qt pour appliquer un style QSS spécifique si besoin
        self.button_record.setProperty("recording", True)

        # Force Qt à recalculer le style du bouton
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # Empêche de changer de micro pendant l'enregistrement
        self.select_micro.setEnabled(False)

        # Empêche de changer de caméra pendant l'enregistrement
        self.select_camera.setEnabled(False)

        # Empêche de changer de langue pendant l'enregistrement
        self.select_language.setEnabled(False)

        # Affiche et lance l'indicateur REC
        self.recording_indicator.show()
        self.recording_indicator.start()


    def stop_recording_flow(self):
        """
        Arrête toute la séquence d'enregistrement côté interface.
        """

        # Demande au MediaManager d'arrêter l'enregistrement
        self.media_manager.stop_recording()

        # L'application n'est plus en état "enregistrement"
        self.is_recording = False

        # Remet le texte initial du bouton
        self.button_record.setText("Start recording")

        # Retire la propriété de style QSS liée à l'enregistrement
        self.button_record.setProperty("recording", False)

        # Force Qt à recalculer le style du bouton
        self.button_record.style().unpolish(self.button_record)
        self.button_record.style().polish(self.button_record)

        # Réactive les sélecteurs
        self.select_micro.setEnabled(True)
        self.select_camera.setEnabled(True)
        self.select_language.setEnabled(True)

        # Arrête et masque l'indicateur REC
        self.recording_indicator.stop()
        self.recording_indicator.hide()


        # Attend un peu avant de lire le fichier MP4
        # Cela laisse le temps à Qt de finaliser le conteneur vidéo
        QTimer.singleShot(500, self.finalize_recording)


       
    def finalize_recording(self):
        """
        Finalise le traitement après l'arrêt de l'enregistrement.

        Cette méthode est appelée après un court délai pour laisser le temps
        au fichier MP4 d'être complètement écrit.
        """

        user_validation = self.ask_manual_validation()

        if user_validation == "yes":
            # Prépare et sauvegarde la métadonnée de l'enregistrement qui vient de se terminer
            self.metadata_manager.save_recording_metadata(
                self.media_manager,
                self.corpus_manager,
                self.user_firstname
            )
            print("Enregistrement confirmé")

            # Supprime la phrase et affiche la suivante
            self.update_sentence()

        elif user_validation == "no":
            # Supprime le fichier vidéo non conforme
            failed_filepath = self.media_manager.video_filepath
            failed_filepath.unlink(missing_ok=True) # type: ignore
            print("Enregistrement non conforme supprimé")

        else:
            # Supprime le fichier vidéo non conforme
            self.delete_failed_file()

            # Supprime la phrase et affiche la suivante
            self.update_sentence()

            print("Phrase skipée")
            

    def delete_failed_file(self):
        """
        Supprime le fichier vidéo associé à un enregistrement non validé.

        Cette méthode est utilisée lorsque l'enregistrement est refusé
        ou considéré comme non conforme. Le fichier vidéo est alors supprimé
        afin de ne pas conserver de données inutilisables dans le dossier de sortie.
        """

        # Supprime le fichier vidéo non conforme
        failed_filepath = self.media_manager.video_filepath
        failed_filepath.unlink(missing_ok=True) # type: ignore


    def update_sentence(self):
        """
        Passe à la phrase suivante du corpus.

        Cette méthode est appelée lorsqu'un enregistrement est validé
        ou lorsqu'une phrase est volontairement ignorée. Elle retire d'abord
        la phrase actuelle du corpus, puis affiche la phrase suivante dans l'interface.
        """

        # Supprime du corpus la phrase qui vient d'être lue
        self.corpus_manager.consume_current_sentence()

        # Affiche la phrase suivante
        self.display_current_sentence()

    # -----------------------------------------------------------------


    # ========== BOUTON DE TEST MICRO ==========
    @Slot()
    def button_test_micro_clicked(self):
        """
        Démarre ou arrête le test micro selon l'état actuel du MediaManager.
        """

        # Si le test micro est déjà en cours, on l'arrête
        if self.media_manager.micro_test_is_running:
            self.media_manager.stop_micro_test()
            self.button_test_micro.setText("Test micro")

            self.button_test_micro.setProperty("testing", False)

            # Force Qt à recalculer le style du bouton
            self.update_style(self.button_test_micro)

            # Débloque la sélection de micro
            self.select_micro.setEnabled(True)

            return

        # Sinon, on récupère le micro sélectionné
        micro = self.media_manager.get_selected_microphone()

        # On démarre le test micro
        self.media_manager.start_micro_test(micro)
        self.button_test_micro.setText("Stop test")

        self.button_test_micro.setProperty("testing", True)
        
        # Force Qt à recalculer le style du bouton
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

        # Retire temporairement le style actuellement appliqué au widget
        widget.style().unpolish(widget)

        # Réapplique le style au widget en tenant compte de ses propriétés actuelles
        widget.style().polish(widget)


    def ask_manual_validation(self):
        """
        Affiche une pop-up demandant à l'utilisateur s'il veut valider,
        recommencer ou ignorer l'enregistrement.
        """

        # Création de la boîte de dialogue
        msg_box = QMessageBox(self)

        # Titre de la pop-up
        msg_box.setWindowTitle("Validation")

        # Message affiché
        msg_box.setText("Recording satisfactory ?")

        if self.cpt_retry_register > 0 :
            msg_box.setInformativeText(
                "If the sentence is too difficult to read, you can skip it.\n"
                "After skipping, you won't be able to return to this sentence."
            )

        msg_box.setStyleSheet("""
            QLabel {
                min-width: 450px;
                color: #222222;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }

            QPushButton {
                min-width: 110px;
                padding: 6px 12px;
                border: 1px solid #9e9e9e;
                border-radius: 6px;
                background-color: #ffffff;
                color: #222222;
            }

            QPushButton:hover {
                background-color: #e8e8e8;
            }

            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)

        # Bouton pour valider l'enregistrement
        button_yes = msg_box.addButton(
            "Yes",
            QMessageBox.ButtonRole.AcceptRole
        )

        # Bouton pour recommencer l'enregistrement
        button_no = msg_box.addButton(
            "No",
            QMessageBox.ButtonRole.RejectRole
        )

        if self.cpt_retry_register > 0:
            # Bouton pour ignorer la phrase
            button_skip = msg_box.addButton(
                "Skip",
                QMessageBox.ButtonRole.DestructiveRole
            )

        # Bouton sélectionné par défaut
        msg_box.setDefaultButton(button_yes)

        # Récupère la zone interne qui contient les boutons de la QMessageBox
        button_box = msg_box.findChild(QDialogButtonBox)

        # Si elle existe, on force le centrage des boutons
        if button_box is not None:
            button_box.setCenterButtons(True)

        # Affiche la pop-up et attend le choix de l'utilisateur
        msg_box.exec()

        # Récupère le bouton cliqué
        clicked_button = msg_box.clickedButton()

        # Retourne une valeur selon le choix utilisateur
        if clicked_button == button_yes:
            self.cpt_retry_register = 0
            return "yes"

        elif clicked_button == button_no:
            self.cpt_retry_register += 1
            return "no"

        elif clicked_button == button_skip:
            self.cpt_retry_register = 0
            return "skip"
    

    def ask_user_firstname(self):
        """
        Demande le prénom de l'utilisateur.

        OK avec champ vide : relance la fenêtre.
        OK avec prénom valide : stocke le prénom.
        Annuler ou croix : ferme l'application.
        """

        while True:
            dialog = QInputDialog(self)

            dialog.setWindowTitle("Identification utilisateur")
            dialog.setLabelText("Veuillez renseigner votre prénom :")
            dialog.setTextEchoMode(QLineEdit.EchoMode.Normal)

            dialog.setStyleSheet("""
                QInputDialog {
                background-color: #f5f5f5;
                }

                QLabel {
                    min-width: 450px;
                    color: #222222;
                    font-size: 14px;
                    qproperty-alignment: AlignCenter;
                }

                QLineEdit {
                    min-width: 300px;
                    padding: 6px 10px;
                    border: 1px solid #9e9e9e;
                    border-radius: 6px;
                    background-color: #ffffff;
                    color: #222222;
                    font-size: 14px;
                }

                QPushButton {
                    min-width: 110px;
                    padding: 6px 12px;
                    border: 1px solid #9e9e9e;
                    border-radius: 6px;
                    background-color: #ffffff;
                    color: #222222;
                }

                QPushButton:hover {
                    background-color: #e8e8e8;
                }

                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)

            result = dialog.exec()

            # Si l'utilisateur clique sur Annuler ou ferme avec la croix
            if result != QInputDialog.DialogCode.Accepted:
                QApplication.quit()
                return False

            firstname = dialog.textValue().strip().capitalize()

            # Si le prénom est vide, on relance la fenêtre
            if not firstname:
                continue

            # Si le prénom est valide, on le stocke
            self.user_firstname = firstname

            print("Prénom de l'utilisateur : " + firstname)

            return True

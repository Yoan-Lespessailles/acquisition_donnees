from PySide6.QtCore import QTimer

class RecordingIndicator :
    """
    Gère uniquement l'affichage visuel de l'enregistrement :
    - le timer REC. 00:00 ;
    - le point rouge clignotant.
    """

    def __init__(self, qlabel_record_timer, qlabel_record_dot):
        """
        Initialise l'indicateur d'enregistrement.

        Paramètres :
            qlabel_record_timer : QLabel qui affiche le temps d'enregistrement.
            qlabel_record_dot : QLabel qui représente le point rouge clignotant.
        """

        self.label_record_timer = qlabel_record_timer
        self.label_record_dot = qlabel_record_dot

        # ========== blink_timer ==========

        # Timer du clignotement du rond rouge
        self.blink_timer = QTimer()

        # Le clignotement est paramétré sur 500ms 
        self.blink_timer.setInterval(500)

        # Toutes les 500ms la méthode blink_dot est appelée
        self.blink_timer.timeout.connect(self.blink_dot)

        #-----------------------------------------------------

        # ========== record_timer ==========

        # Timer du chrono
        self.record_timer = QTimer()

        # Mise à jour du timer paramétré toutes les secondes 
        self.record_timer.setInterval(1000)

        # Toutes les secondes la méthode update_record_timer est appelée
        self.record_timer.timeout.connect(self.update_record_timer) 

        #-----------------------------------------------------

        # Temps écoulé en secondes
        self.record_seconds = 0
        
        # Le rond rouge est actuellement masqué
        self.blink_visible = False

        # Au lancement de l'application, l'indicateur est caché
        self.hide()
    


    def show(self):
        """
        Affiche l'indicateur d'enregistrement et remet son affichage à zéro.
        """

        # Remet le compteur à zéro pour un nouvel enregistrement
        self.record_seconds = 0

        # Affiche le texte initial du chrono
        self.set_timer_text("REC. 00:00")

        # Le point rouge commence visible
        self.blink_visible = True
        self.label_record_dot.setVisible(True)

        # Affiche les deux labels
        self.label_record_timer.show()
        self.label_record_dot.show()

    
    def hide(self):
        """
        Masque les éléments visuels de l'indicateur.
        """

        self.label_record_timer.hide()
        self.label_record_dot.hide()


    def start(self):
        """
        Démarre les timers de l'indicateur d'enregistrement.
        """

        # Démarre le clignotement du point rouge
        self.blink_timer.start()

        # Démarre le chrono
        self.record_timer.start()


    def stop(self):
        """
        Arrête les timers de l'indicateur d'enregistrement.
        """

        # Arrête le clignotement
        self.blink_timer.stop()

        # Arrête le chrono
        self.record_timer.stop()


    def set_timer_text(self, text):
        """
        Modifie le texte affiché dans le chrono.
        """

        # Met à jour le timer affiché
        self.label_record_timer.setText(text)
        
    

    def blink_dot(self):
        """
        Fait clignoter le point rouge en alternant visible / invisible.
        """
         
        # Inversion de l'état de l'attribut pour le clignotement 
        self.blink_visible = not self.blink_visible

        # Alterne entre visible et non visible en fonction de l'état de l'attribut blink_visible
        self.label_record_dot.setVisible(self.blink_visible)



    def update_record_timer(self):
        """
        Incrémente le chrono et met à jour son affichage.
        """
        # A chaque appel de la méthode, on rajoute une seconde au compteur
        self.record_seconds+=1

        # Convertit en minutes / secondes
        minutes = self.record_seconds // 60
        seconds = self.record_seconds % 60

        # Formatage du texte à afficher
        timer_text = f"REC. {minutes:02}:{seconds:02}"

        # Mise à jour du timer vidéo 
        self.set_timer_text(timer_text)
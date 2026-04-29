import subprocess
# Permet de lancer FFmpeg comme processus externe

from PySide6.QtCore import QThread, Signal
# QThread permet de lire le flux FFmpeg sans bloquer l'interface graphique
# Signal permet d'envoyer les images lues vers la fenêtre principale

from PySide6.QtGui import QImage
# QImage représente une image en mémoire utilisable par PySide6


class FFmpegPreviewThread(QThread):
    # Signal envoyé à la fenêtre principale quand une nouvelle image est disponible
    frame_ready = Signal(QImage)

    def __init__(self, camera_id, width=640, height=480):
        super().__init__()

        # Identifiant de la caméra sélectionnée, par exemple /dev/video0
        self.camera_id = camera_id

        # Largeur de l'image d'aperçu
        self.width = width

        # Hauteur de l'image d'aperçu
        self.height = height

        # Indique si le thread doit continuer à lire le flux FFmpeg
        self.running = True

        # Contiendra le processus FFmpeg lancé par subprocess
        self.process = None

    def run(self):
        # Calcule la taille d'une image brute RGB24.
        # RGB24 = 3 octets par pixel : rouge, vert, bleu.
        frame_size = self.width * self.height * 3

        # Commande FFmpeg :
        # - lit la caméra avec v4l2
        # - récupère le flux vidéo en 640x480 à 30 FPS
        # - convertit les images en RGB24
        # - envoie les images brutes vers Python via pipe:1
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",

            "-f", "v4l2",
            "-framerate", "30",
            "-video_size", f"{self.width}x{self.height}",
            "-i", self.camera_id,

            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "pipe:1"
        ]

        print("Commande aperçu FFmpeg :", " ".join(command))

        # Lance FFmpeg.
        # stdout=subprocess.PIPE permet à Python de lire les images.
        # stderr=subprocess.PIPE récupère les erreurs FFmpeg sans polluer la console.
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Lit les images tant que l'aperçu est actif
        while self.running:
            # Lit une image complète depuis stdout
            raw_frame = self.process.stdout.read(frame_size)

            # Si la taille reçue est incorrecte, FFmpeg s'est probablement arrêté
            if len(raw_frame) != frame_size:
                break

            # Crée une image Qt à partir des données brutes
            image = QImage(
                raw_frame,
                self.width,
                self.height,
                self.width * 3,
                QImage.Format_RGB888
            ).copy()

            # Envoie l'image à la fenêtre principale
            self.frame_ready.emit(image)

        # Arrête FFmpeg si la boucle se termine
        self.stop()

    def stop(self):
        # Demande l'arrêt de la boucle de lecture
        self.running = False

        # Si FFmpeg est lancé, on l'arrête proprement
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None
import shutil
import subprocess

from pathlib import Path

from annotation.ffmpeg_utils import find_ffmpeg_executable


class SubtitleManager:
    """
    Génère des sous-titres ASS à partir des fichiers TextGrid produits par MFA,
    puis crée des copies vidéo sous-titrées sans modifier les vidéos d'origine.

    Logique générale du traitement :
        1. Récupérer un fichier TextGrid produit par MFA

        2. Isoler les deux niveaux utiles du TextGrid :
            - le niveau "words", qui contient les mots avec leurs temps de début et de fin
            - le niveau "phones", qui contient les phones avec leurs temps de début et de fin

        3. Transformer ces informations en listes Python :
            - self.words contient les mots alignés
            - self.phones contient les phones alignés

            Chaque élément est représenté sous la forme : {"start": ..., "end": ..., "text": ...}

        4. Pour chaque phone, retrouver le mot auquel il appartient
            Exemple :
               phone "b" : 1.20 -> 1.23
               mot "bertrand" : 1.20 -> 1.67
            Comme le phone est situé dans l'intervalle temporel du mot, il est associé au mot "bertrand".

        5. Générer un fichier ASS où chaque sous-titre correspond à un phone
            Le sous-titre affiche :
                - le mot courant
                - la suite complète des phones du mot
                - le phone courant mis en évidence

        6. Utiliser FFmpeg pour créer une copie vidéo sous-titrée
            La vidéo originale située dans data/ n'est jamais modifiée.
            La vidéo sous-titrée est enregistrée dans results/.
    """

    def __init__(self, valid_pairs, results_dir, language_code):
        """
        Initialise le gestionnaire de sous-titres.

        Paramètres :
            valid_pairs (list) : liste des paires valides [(video_path, metadata_path), ...]
            results_dir (Path | str) : dossier racine des résultats
            language_code (str) : code de la langue traitée, par exemple "fr"
        """

        # Stocke les paires vidéo / métadonnées valides
        self.valid_pairs = valid_pairs

        # Stocke le dossier racine des résultats
        self.results_dir = Path(results_dir)

        # Stocke le code de langue
        self.language_code = language_code

        # Stocke les mots extraits du TextGrid en cours de traitement
        self.words = []

        # Stocke les phones extraits du TextGrid en cours de traitement
        self.phones = []

        # Dossier contenant les TextGrid produits par MFA
        # Exemple : results/fr/mfa/aligned/
        self.textgrid_dir = (
            self.results_dir / self.language_code / "mfa" / "aligned"
        )

        # Dossier contenant les fichiers de sous-titres ASS générés
        # Exemple : results/fr/mfa/subtitles/
        self.ass_output_dir = (
            self.results_dir / self.language_code / "mfa" / "subtitles"
        )

        # Dossier contenant les copies vidéo avec les sous-titres incrustés
        # Exemple : results/fr/mfa/subtitled_videos/
        self.subtitled_videos_dir = (
            self.results_dir / self.language_code / "mfa" / "subtitled_videos"
        )

        # Stocke l'exécutable FFmpeg détecté
        self.ffmpeg_executable = None

    def ensure_ffmpeg_ass_filter_available(self):
        """
        Vérifie que le FFmpeg disponible possède le filtre ASS.

        Ce filtre est nécessaire pour incruster les fichiers de sous-titres .ass
        dans les vidéos.
        """

        self.ffmpeg_executable = find_ffmpeg_executable()


    def parse_textgrid_intervals(self, textgrid_path):
        """
        Lit un fichier TextGrid MFA et stocke les intervalles words et phones.

        Les mots sont stockés dans self.words.
        Les phones sont stockés dans self.phones.

        Paramètre :
            textgrid_path (Path | str) : chemin du fichier TextGrid à lire

        Retourne :
            None
        """

        # Convertit le chemin en Path
        textgrid_path = Path(textgrid_path)

        # Lit le contenu complet du fichier TextGrid
        content = textgrid_path.read_text(encoding="utf-8")

        # Extrait le bloc correspondant au niveau words
        words_block = self.extract_tier_block(content, "words")

        # Extrait le bloc correspondant au niveau phones
        phones_block = self.extract_tier_block(content, "phones")

        # Stocke les intervalles du niveau words dans l'objet courant
        self.words = self.extract_intervals(words_block)

        # Stocke les intervalles du niveau phones dans l'objet courant
        self.phones = self.extract_intervals(phones_block)


    def extract_tier_block(self, content, tier_name):
        """
        Extrait le bloc correspondant à un niveau précis du TextGrid.

        Paramètres :
            content (str) : contenu complet du fichier TextGrid
            tier_name (str) : nom du niveau recherché, par exemple "words" ou "phones"

        Retourne :
            str : bloc de texte correspondant au niveau demandé
        """

        # Construit le texte exact à rechercher
        # Exemple : name = "words" ou name = "phones"
        pattern = f'name = "{tier_name}"'

        # Cherche la position du niveau demandé dans le fichier TextGrid
        start_index = content.find(pattern)

        # Si le niveau n'est pas trouvé, find() renvoie -1
        if start_index == -1:
            raise ValueError(f"Niveau introuvable dans le TextGrid : {tier_name}")

        # Cherche le prochain bloc "item [" après le niveau actuel
        next_item_index = content.find("\n    item [", start_index + 1)

        # Si aucun autre bloc "item [" n'est trouvé, le niveau actuel va jusqu'à la fin du fichier
        if next_item_index == -1:
            return content[start_index:]

        # Retourne le texte depuis le niveau actuel jusqu'au début du prochain niveau
        return content[start_index:next_item_index]


    def extract_intervals(self, tier_block):
        """
        Extrait les intervalles d'un bloc TextGrid.

        Chaque intervalle contient :
            - start : temps de début
            - end : temps de fin
            - text : étiquette associée

        Paramètre :
            tier_block (str) : bloc TextGrid correspondant à un niveau

        Retourne :
            list[dict] : liste des intervalles non vides
        """

        intervals = []
        current_interval = None

        # Parcourt le bloc TextGrid ligne par ligne
        for raw_line in tier_block.splitlines():
            line = raw_line.strip()

            # Début d'un nouvel intervalle
            if line.startswith("intervals ["):
                current_interval = {}

            # Récupère le temps de début de l'intervalle courant
            elif current_interval is not None and line.startswith("xmin = "):
                start_value = line.replace("xmin = ", "", 1)
                current_interval["start"] = float(start_value)

            # Récupère le temps de fin de l'intervalle courant
            elif current_interval is not None and line.startswith("xmax = "):
                end_value = line.replace("xmax = ", "", 1)
                current_interval["end"] = float(end_value)

            # Récupère le texte de l'intervalle courant
            elif current_interval is not None and line.startswith("text = "):
                text_value = line.replace("text = ", "", 1).strip()

                # Retire les guillemets autour du texte
                if text_value.startswith('"') and text_value.endswith('"'):
                    text_value = text_value[1:-1]

                current_interval["text"] = text_value.strip()

                # Ignore les silences ou intervalles vides
                if current_interval["text"]:
                    intervals.append(current_interval)

                # Réinitialise l'intervalle courant
                current_interval = None

        return intervals


    def find_word_for_phone(self, phone):
        """
        Trouve le mot auquel appartient un phone.

        La méthode utilise self.words, qui contient les mots extraits
        du TextGrid en cours de traitement.
        Exemple :
               phone "b" : 1.20 -> 1.23
               mot "bertrand" : 1.20 -> 1.67
        Comme l'intervalle du phone est compris dans l'intervalle du mot, le phone "b" est associé au mot "bertrand".

        Paramètre :
            phone (dict) : phone courant avec "start", "end" et "text"

        Retourne :
            dict | None : dictionnaire du mot correspondant,
                          ou None si aucun mot n'est trouvé
        """

        for word in self.words:
            if word["start"] <= phone["start"] < word["end"]:
                return word

        return None

    def get_phones_for_word(self, word):
        """
        Récupère tous les phones associés à un mot.

        La méthode utilise self.phones, qui contient les phones extraits
        du TextGrid en cours de traitement.

        Paramètre :
            word (dict) : mot courant avec "start", "end" et "text"

        Retourne :
            list[dict] : phones appartenant au mot
        """

        word_phones = []

        for phone in self.phones:
            if word["start"] <= phone["start"] < word["end"]:
                word_phones.append(phone)

        return word_phones

    def format_ass_time(self, seconds):
        """
        Convertit un temps en secondes au format ASS.

        Format attendu par ASS :
            h:mm:ss.cc

        Exemple :
            1.23 -> 0:00:01.23
        """

        # Calcule les heures
        hours = int(seconds // 3600)

        # Calcule les minutes
        minutes = int((seconds % 3600) // 60)

        # Calcule les secondes restantes
        remaining_seconds = seconds % 60

        return f"{hours}:{minutes:02d}:{remaining_seconds:05.2f}"

    def build_highlighted_phone_line(self, current_phone, word_phones):
        """
        Construit la ligne des phones du mot avec le phone courant mis en évidence.

        Paramètres :
            current_phone (dict) : phone affiché pendant l'intervalle courant
            word_phones (list[dict]) : tous les phones du mot

        Retourne :
            str : ligne de phones avec mise en évidence du phone courant
        """

        displayed_phones = []

        for phone in word_phones:
            phone_text = phone["text"]

            if phone is current_phone:
                # Met le phone courant en évidence
                # Couleur ASS : jaune clair
                displayed_phones.append(
                    r"{\c&H00FFFF&}" + phone_text + r"{\c&HFFFFFF&}"
                )
            else:
                displayed_phones.append(phone_text)

        return " ".join(displayed_phones)

    def build_ass_content(self):
        """
        Construit le contenu complet d'un fichier ASS.

        Chaque ligne de sous-titre correspond à un phone.
        Le sous-titre affiche :
            - le mot courant
            - la suite complète des phones du mot
            - le phone courant mis en évidence

        Les données utilisées proviennent de :
            - self.words
            - self.phones

        Retourne :
            str : contenu du fichier ASS
        """

        lines = [
            "[Script Info]",
            "Title: MFA phone subtitles",
            "ScriptType: v4.00+",
            "PlayResX: 1280",
            "PlayResY: 720",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Default,Arial,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,40,40,50,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]

        # Crée une ligne de sous-titre par phone
        for phone in self.phones:
            word = self.find_word_for_phone(phone)

            # Ignore les phones qui ne sont associés à aucun mot
            if word is None:
                continue

            # Récupère tous les phones du mot courant
            word_phones = self.get_phones_for_word(word)

            # Construit la ligne des phones avec le phone courant en évidence
            highlighted_phones = self.build_highlighted_phone_line(
                phone,
                word_phones,
            )

            # Convertit les temps au format ASS
            start = self.format_ass_time(phone["start"])
            end = self.format_ass_time(phone["end"])

            # Récupère le mot à afficher dans le sous-titre
            word_text = word["text"]

            # Texte affiché sur la vidéo
            # \N correspond à un retour à la ligne en ASS
            subtitle_text = (
                f"Mot : {word_text}"
                r"\N"
                f"Phones : {highlighted_phones}"
            )

            # Ajoute l'événement de sous-titre
            lines.append(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,,{subtitle_text}"
            )

        return "\n".join(lines)

    def write_ass_file(self, textgrid_path):
        """
        Génère un fichier ASS à partir d'un fichier TextGrid.

        Paramètre :
            textgrid_path (Path | str) : chemin du fichier TextGrid

        Retourne :
            Path : chemin du fichier ASS généré
        """

        # Convertit le chemin en Path
        textgrid_path = Path(textgrid_path)

        # Lit le TextGrid et stocke les mots et phones dans self.words et self.phones
        self.parse_textgrid_intervals(textgrid_path)

        # Crée le dossier de sortie des sous-titres ASS
        self.ass_output_dir.mkdir(parents=True, exist_ok=True)

        # Définit le chemin du fichier ASS généré
        ass_path = self.ass_output_dir / f"{textgrid_path.stem}.ass"

        # Supprime l'ancien fichier ASS s'il existe déjà
        if ass_path.exists():
            ass_path.unlink()

        # Construit le contenu du fichier ASS
        ass_content = self.build_ass_content()

        # Écrit le fichier ASS
        ass_path.write_text(ass_content, encoding="utf-8")

        return ass_path

    def generate_all_ass_files(self):
        """
        Génère un fichier ASS pour chaque TextGrid trouvé.

        Retourne :
            dict[str, Path] : dictionnaire associant le nom sans extension au chemin du fichier ASS généré
        """

        ass_files = {}

        # Parcourt tous les fichiers TextGrid produits par MFA
        for textgrid_path in self.textgrid_dir.glob("*.TextGrid"):
            ass_path = self.write_ass_file(textgrid_path)

            # Stocke le fichier ASS par nom de fichier sans extension
            ass_files[textgrid_path.stem] = ass_path

        return ass_files


    def create_subtitled_video(self, video_path, ass_path):
        """
        Crée une copie sous-titrée d'une vidéo à partir d'un fichier ASS.

        La vidéo originale n'est jamais modifiée.
        Une nouvelle vidéo est créée dans :
            results/<code_langue>/mfa/subtitled_videos/

        Paramètres :
            video_path (Path | str) : chemin de la vidéo originale
            ass_path (Path | str) : chemin du fichier ASS à incruster

        Retourne :
            Path : chemin de la vidéo sous-titrée générée
        """

        # Convertit les chemins en Path
        video_path = Path(video_path)
        ass_path = Path(ass_path)

        # Vérifie que la vidéo originale existe
        if not video_path.exists():
            raise FileNotFoundError(f"Vidéo introuvable : {video_path}")

        # Vérifie que le fichier ASS existe
        if not ass_path.exists():
            raise FileNotFoundError(f"Fichier ASS introuvable : {ass_path}")

        # Crée le dossier des vidéos sous-titrées
        self.subtitled_videos_dir.mkdir(parents=True, exist_ok=True)

        # Définit le chemin de sortie de la vidéo sous-titrée
        output_video_path = (
            self.subtitled_videos_dir / f"{video_path.stem}_subtitled.mp4"
        )

        # Supprime l'ancienne vidéo sous-titrée si elle existe déjà
        if output_video_path.exists():
            output_video_path.unlink()

        # Prépare le chemin ASS pour le filtre FFmpeg sous Windows
        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", r"\:")

        # Prépare la commande FFmpeg
        # -i : vidéo originale en entrée
        # -vf ass=... : incruste les sous-titres dans l'image
        # -c:a copy : conserve l'audio sans le réencoder
        command = [
            self.ffmpeg_executable or find_ffmpeg_executable(),
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"ass=filename='{ass_filter_path}'",
            "-c:a",
            "copy",
            str(output_video_path),
        ]

        # Affiche la commande pour faciliter le débogage
        print("Commande FFmpeg sous-titrage lancée :")
        print(" ".join(command))

        # Lance la création de la vidéo sous-titrée
        subprocess.run(command, check=True)

        return output_video_path


    def generate_subtitled_videos(self):
        """
        Génère les fichiers ASS, puis crée les copies vidéo sous-titrées.

        Les vidéos originales dans data/ ne sont jamais modifiées.

        Retourne :
            list[Path] : liste des vidéos sous-titrées générées
        """

        subtitled_videos = []

        # Vérifie que FFmpeg peut incruster les sous-titres ASS
        self.ensure_ffmpeg_ass_filter_available()

        # Génère tous les fichiers ASS à partir des TextGrid
        ass_files = self.generate_all_ass_files()

        # Parcourt les vidéos valides
        for video_path, metadata_path in self.valid_pairs:
            video_path = Path(video_path)

            # Le nom sans extension sert à retrouver le TextGrid et le fichier ASS
            file_stem = video_path.stem

            # Récupère le fichier ASS correspondant à la vidéo
            ass_path = ass_files.get(file_stem)

            # Si aucun fichier ASS n'existe pour cette vidéo, on l'ignore
            if ass_path is None:
                print(f"Aucun sous-titre ASS trouvé pour la vidéo : {video_path.name}")
                continue

            # Crée une copie sous-titrée de la vidéo
            output_video_path = self.create_subtitled_video(
                video_path,
                ass_path,
            )

            subtitled_videos.append(output_video_path)

        return subtitled_videos

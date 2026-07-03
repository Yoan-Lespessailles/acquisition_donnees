import json
import random

from acquisition.config_loader import load_config
CONFIG = load_config()

class CorpusManager:
    """
    Gère les données du corpus :
        - chargement des langues disponibles ;
        - chargement du JSON correspondant à une langue ;
        - mélange des listes de mots / phrases ;
        - génération de la phrase courante ;
        - consommation des mots ou phrases déjà utilisés.
    """

    def __init__(self):
        """
        Initialise le gestionnaire de corpus.
        """

        # Dossier contenant les fichiers JSON de corpus
        self.corpus_dir = CONFIG["paths"]["corpus_dir"]

        # Nombre total de phrases prévues pour une session
        self.sentence_total = 0

        # Récupère le mode choisi dans la configuration
        self.sentence_mode = CONFIG["sentence"]["mode"]

        # Compteur de phrases affichées / enregistrées
        self.sentence_count = 0

        # Liste des langues disponibles
        self.languages = []

        # Langue actuellement sélectionnée
        self.language_selected = None
        
        # Données JSON du corpus actuellement chargé
        self.corpus_data = None

        # Phrase actuellement affichée
        self.current_sentence = ""

        # Template de la phrase actuellement affichée
        self.current_template_type = None
        

    def load_languages(self):
        """
        Charge la liste des langues disponibles à partir des fichiers JSON du dossier corpus.

        Retourne :
            Une liste de listes : [[language_name, language_code, mfa_model_name], ...]
        """

        # On vide la liste pour éviter les doublons si la méthode est rappelée
        self.languages.clear()

        # Parcourt tous les fichiers .json du dossier corpus
        for json_file in self.corpus_dir.glob("*.json"):
            try:
                # Ouvre le fichier JSON en lecture
                with open(json_file, "r", encoding="utf-8") as file:
                    data = json.load(file)

                # Récupère le nom et le code de la langue
                language_name = data.get("language_name")
                language_code = data.get("language_code")
                # Nom du modèle MFA à utiliser pour l'annotation, par exemple "french_mfa"
                mfa_model_name = data.get("mfa_model_name")

                # Si les deux informations existent, on ajoute la langue
                if language_name and language_code:
                    self.languages.append([language_name, language_code, mfa_model_name])

            except json.JSONDecodeError:
                print(f"Erreur JSON dans le fichier : {json_file}")

            except Exception as error:
                print(f"Erreur lors de la lecture de {json_file} : {error}")

        # Trie les langues par ordre alphabétique du nom de langue
        self.languages.sort(key=lambda language: language[0].lower())

        # Si au moins une langue existe, on sélectionne la première par défaut
        if self.languages and self.language_selected is None:
            self.language_selected = self.languages[0]
            # print(f"Langue sélectionnée par défaut : {self.language_selected}")

        elif not self.languages:
            print("Aucune langue disponible dans le dossier corpus")

        return self.languages    
        
    
    def select_language(self, index):
        """
        Sélectionne une langue à partir de son index dans la liste des langues.

        Paramètre :
            index : position de la langue dans self.languages.
        """

        # Vérifie que l'index existe bien dans la liste
        if index < 0 or index >= len(self.languages):
            print(f"Index de langue invalide : {index}")
            return False

        # Met à jour la langue sélectionnée
        self.language_selected = self.languages[index]

        print(f"Langue sélectionnée : {self.language_selected}")

        # Charge le corpus correspondant à cette langue
        self.load_selected_language_corpus()

        return True
    
    
    def prepare_session(self):
        """
        Prépare une nouvelle session pour la langue sélectionnée.

        Cette méthode orchestre les étapes nécessaires :
            - charger le corpus ;
            - mélanger les listes ;
            - réinitialiser le compteur ;
            - préparer la première phrase.
        """

        corpus_loaded = self.load_selected_language_corpus()

        if not corpus_loaded:
            return False

        self.sentence_total = self.total_sentences()

        self.shuffle_corpus()
        self.reset_session()

        self.current_sentence = self.get_current_sentence()

        return True


    def load_selected_language_corpus(self):
        """
        Charge uniquement le corpus JSON correspondant à la langue sélectionnée.
        """

        if self.language_selected is None:
            print("Aucune langue sélectionnée")
            return False

        language_code = self.language_selected[1]

        self.corpus_data = None

        # Ouvre le fichier JSON en lecture avec l'encodage UTF-8 (pour la prise en charge des accents)
        for json_file in self.corpus_dir.glob(f"*{language_code}.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as file:
                    self.corpus_data = json.load(file)

                return True

            # Cette erreur arrive si le fichier existe mais que son contenu n'est pas un JSON valide
            except json.JSONDecodeError:
                print(f"Erreur JSON dans le fichier : {json_file}")

            # Cette sécurité permet d'afficher les autres erreurs possibles sans faire planter toute l'application
            except Exception as error:
                print(f"Erreur lors de la lecture de {json_file} : {error}")

        print(f"Aucun corpus trouvé pour la langue : {language_code}")
        return False
    

    def total_sentences(self):
        """
        Calcule le nombre total de phrases disponibles selon le mode choisi.

        Modes disponibles :
            0 : utilise le template 1 et le template 2 ;
            1 : utilise uniquement le template 1 ;
            2 : utilise uniquement le template 2.
        """

        # Si aucun corpus n'est chargé, on ne peut pas compter les phrases
        if self.corpus_data is None:
            print("Impossible de compter : aucun corpus chargé")
            return 0

        # Compte le nombre de phrases générables avec le template 1
        # On compte la liste "subject", car chaque phrase générée consomme un sujet, un verbe, un nombre et un groupe nominal
        total_template_1 = len(self.corpus_data["template_1"]["subject"])

        # Compte le nombre de phrases naturelles disponibles dans le template 2
        total_template_2 = len(self.corpus_data["template_2"]["sentences"])

        # Mode 0 : on utilise les deux templates
        if self.sentence_mode == 0:
            return total_template_1 + total_template_2

        # Mode 1 : on utilise uniquement le template 1
        if self.sentence_mode == 1:
            return total_template_1

        # Mode 2 : on utilise uniquement le template 2
        if self.sentence_mode == 2:
            return total_template_2

        # Si le mode est invalide, on évite de planter sans explication
        print(f"Mode de génération inconnu : {self.sentence_mode}")
        return 0
    

    def shuffle_corpus(self):
        """
        Mélange les listes de travail du corpus chargé selon le mode sélectionné.

        Modes disponibles :
            0 : utilise le template 1 et le template 2 ;
            1 : utilise uniquement le template 1 ;
            2 : utilise uniquement le template 2.
        """

        # Si aucun corpus n'est chargé, on ne peut pas mélanger les listes
        if self.corpus_data is None:
            print("Impossible de mélanger : aucun corpus chargé")
            return False

        # Si le mode utilise le template 1, on mélange ses quatre listes
        if self.sentence_mode in (0, 1):
            random.shuffle(self.corpus_data["template_1"]["subject"])
            random.shuffle(self.corpus_data["template_1"]["verb"])
            random.shuffle(self.corpus_data["template_1"]["number"])
            random.shuffle(self.corpus_data["template_1"]["nominal_group"])

        # Si le mode utilise le template 2, on mélange sa liste de phrases
        if self.sentence_mode in (0, 2):
            random.shuffle(self.corpus_data["template_2"]["sentences"])

        return True
    

    def reset_session(self):
        """
        Réinitialise l'état de session pour une nouvelle langue ou un nouveau passage.
        """

        self.sentence_count = 0
        self.current_sentence = ""


    def get_current_sentence(self):
        """
        Retourne la phrase courante à afficher selon le mode sélectionné.

        Modes disponibles :
            0 : utilise le template 1 puis le template 2 ;
            1 : utilise uniquement le template 1 ;
            2 : utilise uniquement le template 2.
        """

        # Vérifie qu'un corpus est chargé
        if self.corpus_data is None:
            return "Aucun corpus chargé"

        # Mode 0 ou 1 :
        # on utilise le template 1 si ce mode l'autorise et s'il reste encore des éléments disponibles
        if self.sentence_mode in (0, 1) and self.corpus_data["template_1"]["subject"]:
            self.current_sentence = self.build_template_1_sentence()
            self.current_template_type = "template_1"
            return self.current_sentence

        # Mode 0 ou 2 :
        # on utilise le template 2 si ce mode l'autorise et s'il reste encore des phrases disponibles
        if self.sentence_mode in (0, 2) and self.corpus_data["template_2"]["sentences"]:
            self.current_sentence = self.corpus_data["template_2"]["sentences"][-1]["text"]
            self.sentence_with_digit = self.corpus_data["template_2"]["sentences"][-1]["numeric"]
            self.current_template_type = "template_2"
            return self.current_sentence

        # Si aucun contenu compatible avec le mode choisi n'est disponible, la session est terminée
        self.current_sentence = "Fin de la session d'enregistrement"
        self.current_template_type = None

        return self.current_sentence


    def build_template_1_sentence(self):
        """
        Construit une phrase à partir du template 1.

        Deux versions sont produites :
            - self.sentence : phrase affichée à l'utilisateur, avec le nombre en lettres ;
            - self.sentence_with_digit : phrase avec la valeur numérique du nombre.

        Exemple :
            self.sentence = "Patrick demande dix montagnes sombres"
            self.sentence_with_digit = "Patrick demande 10 montagnes sombres"
        """

        # Récupère l'ordre syntaxique défini dans le JSON
        # Exemple : ["subject", "verb", "number", "nominal_group"]
        structure = self.corpus_data["template_1"]["structure"]  # type: ignore

        # Contient les morceaux de la phrase affichée à l'utilisateur
        display_sentence_parts = []

        # Contient les morceaux de la phrase avec les nombres en chiffres
        sentence_with_digit_parts = []

        # Parcourt chaque bloc dans l'ordre défini
        for list_name in structure:

            # Cas particulier du nombre :
            # il contient maintenant deux informations : "text" et "value" -> on veut afficher le texte mais garder la valeur numérique pour les métadonnées
            if list_name == "number":
                number_data = self.corpus_data["template_1"][list_name][-1]  # type: ignore

                # Version affichée : nombre en lettres
                display_sentence_parts.append(number_data["text"])

                # Version métadonées : valeur numérique
                sentence_with_digit_parts.append(str(number_data["value"]))

            else:
                # Pour les autres blocs, le contenu est une simple chaîne de caractères
                word = self.corpus_data["template_1"][list_name][-1]  # type: ignore

                # Même contenu pour l'affichage et pour les métadonnées
                display_sentence_parts.append(word)
                sentence_with_digit_parts.append(word)

        # Assemble la phrase affichée
        sentence = " ".join(display_sentence_parts)

        # Assemble la phrase de métadonnées
        self.sentence_with_digit = " ".join(sentence_with_digit_parts)

        # Retourne la phrase affichée à l'utilisateur
        return sentence


    def consume_current_sentence(self):
        """
        Supprime du corpus les mots ou la phrase qui viennent d'être utilisés.

        La consommation dépend du type de phrase actuellement affiché :
            - template_1 : on supprime un élément dans chaque liste du template 1 ;
            - template_2 : on supprime la phrase utilisée dans la liste du template 2.

        Le mode de session est déjà pris en compte dans get_current_sentence().
        Ici, on consomme simplement ce qui a réellement été affiché.
        """

        # Vérifie qu'un corpus est chargé
        if self.corpus_data is None:
            print("Impossible de consommer une phrase : aucun corpus chargé")
            return False

        # Si toutes les phrases ont déjà été lues, on ne consomme rien
        if self.is_session_finished():
            print("Toutes les phrases ont été lues")
            return False

        # Si la phrase courante vient du template 1, on retire le dernier élément de chaque liste utilisée pour construire la phrase
        if self.current_template_type == "template_1":
            for list_name in self.corpus_data["template_1"]["structure"]:
                self.corpus_data["template_1"][list_name].pop()

        # Si la phrase courante vient du template 2, on retire la phrase naturelle actuellement utilisée
        elif self.current_template_type == "template_2":
            self.corpus_data["template_2"]["sentences"].pop()

        # Si aucun template courant n'est défini, on évite de consommer au hasard
        else:
            print("Impossible de consommer : aucun type de template courant défini")
            return False

        # Une phrase vient d'être consommée
        self.sentence_count += 1

        # Prépare la prochaine phrase
        self.current_sentence = self.get_current_sentence()

        return True
    

    def is_session_finished(self):
        """
        Indique si toutes les phrases autorisées par le mode sélectionné
        ont été utilisées.

        Modes disponibles :
            0 : utilise le template 1 et le template 2 ;
            1 : utilise uniquement le template 1 ;
            2 : utilise uniquement le template 2.

        Retourne :
            True si la session est terminée ;
            False s'il reste encore au moins une phrase à lire.
    """

        # Si aucun corpus n'est chargé, on considère que la session est terminée
        # Ça évite d'autoriser un enregistrement sans phrase disponible
        if self.corpus_data is None:
            return True

        # Vérifie s'il reste des éléments dans le template 1
        template_1_has_sentences = bool(self.corpus_data["template_1"]["subject"])

        # Vérifie s'il reste des phrases naturelles dans le template 2
        template_2_has_sentences = bool(self.corpus_data["template_2"]["sentences"])

        # Mode 0 : la session utilise les deux templates
        # Elle est terminée uniquement quand les deux sont vides
        if self.sentence_mode == 0:
            return not template_1_has_sentences and not template_2_has_sentences

        # Mode 1 : la session utilise uniquement le template 1
        # Elle est terminée dès que le template 1 est vide
        if self.sentence_mode == 1:
            return not template_1_has_sentences

        # Mode 2 : la session utilise uniquement le template 2
        # Elle est terminée dès que le template 2 est vide
        if self.sentence_mode == 2:
            return not template_2_has_sentences

        # Si le mode est invalide, on bloque la session par sécurité
        print(f"Mode de génération inconnu : {self.sentence_mode}")
        return True
    
    
    def get_sentence_counter_text(self):
        """
        Retourne le texte du compteur affiché à l'utilisateur.

        Le compteur affiche la phrase en cours.
        Exemple :
            1/20 au début de la session.
        """

        displayed_count = min(self.sentence_count + 1,self.sentence_total)

        return f"{displayed_count}/{self.sentence_total}"

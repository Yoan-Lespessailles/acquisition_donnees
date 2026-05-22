import json
import random

from config_loader import load_config
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

        # Nombre total de phrases prévues pour une session.
        self.sentence_total = CONFIG["sentence"]["total"]

        # Compteur de phrases affichées / enregistrées.
        self.sentence_count = 0

        # Liste des langues disponibles.
        self.languages = []

        # Langue actuellement sélectionnée.
        self.language_selected = None
        
        # Données JSON du corpus actuellement chargé.
        self.corpus_data = None

        # Phrase actuellement affichée.
        self.current_sentence = ""

        # Template de la phrase actuellement affichée.
        self.current_template_type = ""
        

    def load_languages(self):
        """
        Charge la liste des langues disponibles à partir des fichiers JSON du dossier corpus.

        Retourne :
            Une liste de tuples : [(language_name, language_code), ...]
        """

        # On vide la liste pour éviter les doublons si la méthode est rappelée.
        self.languages.clear()

        # Parcourt tous les fichiers .json du dossier corpus.
        for json_file in self.corpus_dir.glob("*.json"):
            try:
                # Ouvre le fichier JSON en lecture.
                with open(json_file, "r", encoding="utf-8") as file:
                    data = json.load(file)

                # Récupère le nom et le code de la langue.
                language_name = data.get("language_name")
                language_code = data.get("language_code")

                # Si les deux informations existent, on ajoute la langue.
                if language_name and language_code:
                    self.languages.append((language_name, language_code))

            except json.JSONDecodeError:
                print(f"Erreur JSON dans le fichier : {json_file}")

            except Exception as error:
                print(f"Erreur lors de la lecture de {json_file} : {error}")

        # Si au moins une langue existe, on sélectionne la première par défaut.
        if self.languages and self.language_selected is None:
            self.language_selected = self.languages[0]
            print(f"Langue sélectionnée par défaut : {self.language_selected}")

        elif not self.languages:
            print("Aucune langue disponible dans le dossier corpus")

        return self.languages    
        
    
    def select_language(self, index):
        """
        Sélectionne une langue à partir de son index dans la liste des langues.

        Paramètre :
            index : position de la langue dans self.languages.
        """

        # Vérifie que l'index existe bien dans la liste.
        if index < 0 or index >= len(self.languages):
            print(f"Index de langue invalide : {index}")
            return False

        # Met à jour la langue sélectionnée.
        self.language_selected = self.languages[index]

        print(f"Langue sélectionnée : {self.language_selected}")

        # Charge le corpus correspondant à cette langue.
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

            # Cette erreur arrive si le fichier existe mais que son contenu n'est pas un JSON valide.
            except json.JSONDecodeError:
                print(f"Erreur JSON dans le fichier : {json_file}")

            # Cette sécurité permet d'afficher les autres erreurs possibles sans faire planter toute l'application.
            except Exception as error:
                print(f"Erreur lors de la lecture de {json_file} : {error}")

        print(f"Aucun corpus trouvé pour la langue : {language_code}")
        return False
    

    def shuffle_corpus(self):
        """
        Mélange les listes de travail du corpus chargé.
        """

        if self.corpus_data is None:
            print("Impossible de mélanger : aucun corpus chargé")
            return False

        random.shuffle(self.corpus_data["template_1"]["subject"])
        random.shuffle(self.corpus_data["template_1"]["verb"])
        random.shuffle(self.corpus_data["template_1"]["number"])
        random.shuffle(self.corpus_data["template_1"]["nominal_group"])
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
        Retourne la phrase courante à afficher.

        Priorité :
            1. Template 1 tant qu'il reste des mots.
            2. Template 2 ensuite.
            3. Message de fin si tout est consommé.
        """

        # Vérifie qu'un corpus est chargé.
        if self.corpus_data is None:
            return "Aucun corpus chargé"

        # Tant qu'il reste des éléments dans le Template 1.
        if self.corpus_data["template_1"]["subject"]:
            self.current_sentence = self.build_template_1_sentence()
            self.current_template_type = "template_1"

        # Sinon, on passe au Template 2.
        elif self.corpus_data["template_2"]["sentences"]:
            self.current_sentence = self.corpus_data["template_2"]["sentences"][-1]
            self.current_template_type = "template_2"

        # Sinon, la session est terminée.
        else:
            self.current_sentence = "Fin de la session d'enregistrement"

        return self.current_sentence


    def build_template_1_sentence(self):
        """
        Construit une phrase à partir du template 1.

        La clé 'structure' définit l'ordre des blocs.
        Exemple :
            ["subject", "verb", "number", "nominal_group"]
        """

        # Récupère l'ordre syntaxique défini dans le JSON.
        structure = self.corpus_data["template_1"]["structure"] # type: ignore

        # Stocke les morceaux de phrase dans une liste.
        sentence_parts = []

        # Parcourt chaque bloc dans l'ordre défini.
        for list_name in structure:
            sentence_parts.append(self.corpus_data["template_1"][list_name][-1]) # type: ignore

        # Assemble les morceaux avec des espaces.
        return " ".join(sentence_parts)


    def consume_current_sentence(self):
        """
        Supprime du corpus les mots ou la phrase qui viennent d'être utilisés.
        """

        # Vérifie qu'un corpus est chargé.
        if self.corpus_data is None:
            print("Impossible de consommer une phrase : aucun corpus chargé")
            return False

        # Si toutes les phrases ont déjà été lues, on ne consomme rien.
        if self.is_session_finished():
            print("Toutes les phrases ont été lues")
            return False

        # Consommation du Template 1 en priorité.
        if self.corpus_data["template_1"]["subject"]:
            for list_name in self.corpus_data["template_1"]["structure"]:
                self.corpus_data["template_1"][list_name].pop()

        # Puis consommation du Template 2.
        elif self.corpus_data["template_2"]["sentences"]:
            self.corpus_data["template_2"]["sentences"].pop()

        # Une phrase vient d'être consommée.
        self.sentence_count += 1

        # Prépare la prochaine phrase.
        self.current_sentence = self.get_current_sentence()

        return True
    

    def is_session_finished(self):
        """
        Indique si toutes les phrases du corpus ont été utilisées.

        Retourne :
            True si la session est terminée ;
            False s'il reste encore au moins une phrase à lire.
        """

        # Si aucun corpus n'est chargé, on considère que la session est terminée.
        # Cela évite d'autoriser un enregistrement sans phrase disponible.
        if self.corpus_data is None:
            return True

        # Vérifie s'il reste des éléments dans le template 1.
        template_1_has_sentences = bool(self.corpus_data["template_1"]["subject"])

        # Vérifie s'il reste des phrases naturelles dans le template 2.
        template_2_has_sentences = bool(self.corpus_data["template_2"]["sentences"])

        # La session est terminée uniquement s'il ne reste rien dans les deux templates.
        return not template_1_has_sentences and not template_2_has_sentences
    
    
    def get_sentence_counter_text(self):
        """
        Retourne le texte du compteur affiché à l'utilisateur.

        Le compteur affiche la phrase en cours.
        Exemple :
            1/20 au début de la session.
        """

        displayed_count = min(self.sentence_count + 1,self.sentence_total)

        return f"{displayed_count}/{self.sentence_total}"

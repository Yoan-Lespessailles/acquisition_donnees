# Annotation automatique avec MFA

Ce projet utilise [Montreal Forced Aligner (MFA)](https://montreal-forced-aligner.readthedocs.io/) pour aligner la phrase attendue avec l'audio d'une vidéo. Pour chaque enregistrement, MFA produit un fichier TextGrid contenant deux niveaux d'annotation : les mots et les phones.

## 1. Prérequis

Installer une distribution Conda, par exemple Miniconda ou Miniforge. Les autres outils nécessaires (`ffmpeg`, MFA et Kaldi en version CPU) seront installés dans l'environnement du projet.

Le fichier `environment.yml` utilise exclusivement le canal communautaire `conda-forge`. Les canaux Anaconda `defaults` sont désactivés pour cet environnement.

## 2. Créer l'environnement

L'environnement se nomme `annotation` et utilise Python 3.12. Choisir la procédure correspondant au système d'exploitation utilisé.

### Windows

Ouvrir PowerShell ou le terminal Conda, puis exécuter :

```powershell
cd C:\chemin\vers\acquisition_donnees\annotation_project
conda env create -f environment.yml
conda activate annotation
mfa version
ffmpeg -version
```

La commande de création doit être lancée lorsque l'invite de commande se termine par `annotation_project>` : c'est dans ce dossier que se trouve `environment.yml`.

Avec certaines installations d'Anaconda, un contrôle des conditions d'utilisation peut avoir lieu avant même la lecture de `environment.yml`. Si `CondaToSRejectedError` mentionne les canaux `pkgs/r` et `pkgs/msys2`, les accepter une fois, puis relancer la création :

```powershell
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
conda env create -f environment.yml
```

Ces canaux appartiennent à l'installation Anaconda. L'environnement du projet continuera ensuite à installer ses dépendances depuis `conda-forge`, conformément à `environment.yml`.

### Linux

Ouvrir un terminal, puis exécuter :

```bash
cd /chemin/vers/acquisition_donnees/annotation_project
conda env create -f environment.yml
conda activate annotation
mfa version
ffmpeg -version
```

### macOS

Ouvrir Terminal, puis exécuter :

```bash
cd /chemin/vers/acquisition_donnees/annotation_project
conda env create -f environment.yml
conda activate annotation
mfa version
ffmpeg -version
```

L'environnement n'a besoin d'être créé qu'une seule fois. Pour les utilisations suivantes, seule son activation est nécessaire :

```console
conda activate annotation
```

## 3. Installer le modèle acoustique MFA

Télécharger le modèle correspondant à la langue à traiter. Pour le français :

```powershell
mfa model download acoustic french_mfa
```

Les modèles configurés dans l'application sont :

| Code | Modèle acoustique |
|------|-------------------|
| `fr` | `french_mfa` |
| `en` | `english_mfa` |
| `it` | `italian_mfa` |
| `es` | `spanish_mfa` |
| `de` | `german_mfa` |

Il suffit de remplacer `french_mfa` dans la commande de téléchargement pour installer un autre de ces modèles.

## 4. Préparer les données

Glisser le dossier `data` généré par l'application **AVDataCollector** à la racine du dépôt `acquisition_donnees`. L'application d'acquisition se charge déjà de produire des données conformes au format attendu.

Le dictionnaire de prononciation personnalisé doit se trouver ici :

```text
mfa/dictionaries/fr_custom.dict
```

Un dictionnaire français est déjà présent. Pour une autre langue, créer le fichier `<code>_custom.dict`, par exemple `en_custom.dict`, et y inclure tous les mots susceptibles d'apparaître dans les phrases.

## 5. Lancer l'annotation

Depuis le dossier `annotation_project`, avec l'environnement activé, contrôler d'abord les fichiers détectés :

```powershell
python -m annotation.main --language fr --dry-run
```

Puis lancer la validation et l'alignement MFA :

```powershell
python -m annotation.main --language fr
```

Pour utiliser un dossier de données différent :

```powershell
python -m annotation.main --language fr --data-dir C:\chemin\vers\data
```

## 6. Résultats

Les fichiers produits sont enregistrés à la racine du dépôt :

```text
results/
└── fr/
    └── mfa/
        ├── input/     # fichiers WAV et LAB préparés pour MFA
        └── aligned/   # fichiers TextGrid contenant les mots et les phones
```

Les dossiers `input` et `aligned` sont recréés à chaque exécution pour éviter de conserver des résultats périmés.

Si MFA signale un mot absent du dictionnaire pendant la validation, ajouter sa prononciation au dictionnaire personnalisé, puis relancer la commande d'annotation.

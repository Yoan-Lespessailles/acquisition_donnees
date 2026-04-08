<h1> Acquisition de données pour la lecture labiale phonétique </h1>
Développement d'une solution logiciel permettant l'acquisition de données pour l'analyse de séries temporelles par apprentissage profond pour la lecture labiale phonétique.

<h3> Processus d’acquisition, validation et annotation des données : </h3>

```mermaid
flowchart TD
    A([Début]) --> B[Choix de la langue]
    B --> C[Affichage d'une phrase]
    C --> D[Enregistrement du visage et de la voix]

    D --> E{Audio conforme à la\nphrase affichée ?}
    
    E -- Non --> F[Rejeter l'enregistrement]
    F --> D
    
    E -- Oui --> G{Qualité vidéo suffisante ?}
    
    G -- Non --> H[Rejeter l'enregistrement]
    H --> D
    
    G -- Oui --> I[Valider l'enregistrement]
    I --> J[Annoter les données]
    J --> K([Fin])
```

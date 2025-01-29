# Projet d'Analyse des Données GitHub avec DBT

## Description du Projet

Ce projet utilise dbt (data build tool) pour transformer les données collectées depuis l'API GitHub en un modèle dimensionnel permettant l'analyse des issues et des contributeurs du projet Node.js.

## Architecture des Données

Le projet suit une architecture en trois couches :

1. **Sources (Raw)**
   - `contributors` : Données brutes des contributeurs GitHub
   - `issues` : Données brutes des issues GitHub

2. **Couche Nettoyée (Cleansed)**
   - `clean_contributors` : Données des contributeurs normalisées
   - `clean_issues` : Données des issues nettoyées et validées

3. **Couche Applicative (Application)**
   - `dim_contributor` : Dimension des contributeurs
   - `fact_issues` : Table de faits des issues

## Structure du Projet

```
├── models/
│   ├── application/        # Modèles dimensionnels finaux
│   │   ├── dim_contributor.sql
│   │   └── fact_issues.sql
│   ├── cleansed/          # Modèles de données nettoyées
│   │   ├── clean_contributors.sql
│   │   └── clean_issues.sql
│   ├── schema.yml         # Documentation et tests des modèles
│   └── sources.yml        # Configuration des sources
├── dbt_project.yml        # Configuration du projet dbt
└── profiles.yml          # Configuration de la connexion à la base de données
```

## Tests et Documentation

Le projet inclut :
- Tests de non-nullité sur les clés primaires
- Tests d'unicité sur les identifiants
- Tests de relations entre les tables
- Tests de validation des valeurs acceptées
- Documentation complète des modèles et colonnes

## Prérequis

- Python 3.x
- dbt Core
- DuckDB
- Bibliothèques Python : `requests`, `pyarrow`, `duckdb`, `python-dotenv`

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_REPO]
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer l'environnement dbt :
```bash
cp profiles.yml ~/.dbt/
```

## Utilisation

1. Collecter les données GitHub :
```bash
python pipeline.py
```

2. Exécuter les transformations dbt :
```bash
dbt run
```

3. Exécuter les tests :
```bash
dbt test
```

4. Générer la documentation :
```bash
dbt docs generate
dbt docs serve
```

## Visualisation et Documentation

La documentation complète du projet, incluant le DAG (Directed Acyclic Graph) des transformations, peut être consultée en local après avoir exécuté `dbt docs serve` à l'adresse : http://localhost:8080

## Maintenance

- Les modèles sont documentés dans `schema.yml` et `sources.yml`
- Les tests sont intégrés dans les fichiers de documentation
- La mise à jour des données peut être automatisée via un planificateur de tâches
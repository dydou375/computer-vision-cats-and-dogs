# Tests du Projet Cats vs Dogs Classifier

## Vue d'ensemble

Ce document liste tous les tests disponibles dans le projet et explique leur utilisation.

## Structure des Tests

```
tests/
├── README_TESTS.md              # Ce fichier de documentation
├── test_api.py                  # Tests complets de l'API
├── test_api_simple.py           # Tests rapides de l'API
├── test_metrics_api.py          # Tests des métriques
├── test_models.py               # Tests des modèles
├── test_feedback_ui.py          # Tests de l'interface feedback
├── test_feedback_ui_message.py  # Tests des messages de feedback
├── test_feedback_db.py          # Tests d'enregistrement en base
└── __pycache__/                 # Cache Python
```

## Tests Disponibles

### 1. Tests API Principaux

#### `test_api.py` - Tests Complets de l'API
- **Description** : Suite complète de tests pour l'API
- **Fonctionnalités testées** :
  - Santé de l'API (`/health`)
  - Informations de l'API (`/api/info`)
  - Prédictions d'images (`/api/predict`)
  - Feedback utilisateur (`/api/feedback`)
  - Métriques journalières (`/api/metrics/daily`)
  - Métriques 7 jours (`/api/metrics/7d`)
- **Utilisation** :
  ```bash
  python -m pytest tests/test_api.py -v -s
  ```

#### `test_api_simple.py` - Tests Rapides
- **Description** : Tests rapides pour vérifier la disponibilité de l'API
- **Fonctionnalités testées** :
  - Vérification de santé de l'API
  - État du modèle
- **Utilisation** :
  ```bash
  python -m pytest tests/test_api_simple.py -v -s
  ```

### 2. Tests de Métriques

#### `test_metrics_api.py` - Tests des Métriques
- **Description** : Tests spécifiques aux endpoints de métriques
- **Fonctionnalités testées** :
  - Métriques journalières
  - Métriques sur 7 jours
  - Agrégation des données
- **Utilisation** :
  ```bash
  python -m pytest tests/test_metrics_api.py -v -s
  ```

### 3. Tests des Modèles

#### `test_models.py` - Tests des Modèles
- **Description** : Tests des modèles de machine learning
- **Fonctionnalités testées** :
  - Chargement des modèles
  - Prédictions
- **Utilisation** :
  ```bash
  python -m pytest tests/test_models.py -v -s
  ```

### 4. Tests de l'Interface Utilisateur

#### `test_feedback_ui.py` - Tests de l'Interface Feedback
- **Description** : Tests de l'interface utilisateur pour le feedback
- **Fonctionnalités testées** :
  - Feedback positif
  - Feedback négatif
  - Gestion des erreurs
  - Tokens invalides
- **Utilisation** :
  ```bash
  python -m pytest tests/test_feedback_ui.py -v -s
  ```

#### `test_feedback_ui_message.py` - Tests des Messages de Feedback
- **Description** : Tests spécifiques aux messages de confirmation du feedback
- **Fonctionnalités testées** :
  - Messages de succès
  - Messages d'erreur
  - Validation des données
  - Authentification
- **Utilisation** :
  ```bash
  python -m pytest tests/test_feedback_ui_message.py -v -s
  ```

#### `test_feedback_db.py` - Tests d'Enregistrement en Base
- **Description** : Tests de l'enregistrement du feedback en base de données
- **Fonctionnalités testées** :
  - Insertion en base de données
  - Feedback positif et négatif
  - Vérification du flag `saved_to_db`
- **Utilisation** :
  ```bash
  python -m pytest tests/test_feedback_db.py -v -s
  ```

## Exécution des Tests

### Exécuter Tous les Tests
```bash
cd formation_alternance/Cats_&_dogs/computer-vision-cats-and-dogs
python -m pytest tests/ -v -s
```

### Exécuter un Test Spécifique
```bash
python -m pytest tests/test_api.py -v -s
python -m pytest tests/test_feedback_db.py -v -s
```

### Exécuter avec Couverture
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Exécuter en Mode Parallèle
```bash
python -m pytest tests/ -n auto
```

## Configuration des Tests

### Variables d'Environnement
Les tests utilisent la configuration définie dans `config/settings.py` :
- `BASE_URL` : URL de l'API (défaut: http://localhost:8000)
- `TOKEN` : Token d'authentification API
- `DB_CONFIG` : Configuration de la base de données

### Prérequis
- L'API doit être démarrée
- La base de données PostgreSQL doit être accessible
- Le modèle doit être chargé

## Scripts de Diagnostic

### `scripts/check_feedback_table.py`
- **Description** : Vérifie la structure de la table `feedback_user`
- **Utilisation** :
  ```bash
  python scripts/check_feedback_table.py
  ```

## Résultats des Tests

### Format de Sortie
- `-v` : Mode verbeux (affiche chaque test)
- `-s` : Affiche les print statements
- `--tb=short` : Traceback court en cas d'erreur

### Exemple de Sortie
```
tests/test_api_simple.py::test_quick_api_health PASSED
tests/test_feedback_db.py::test_feedback_database_insertion PASSED
tests/test_feedback_db.py::test_feedback_database_negative PASSED
```

## Dépannage

### Problèmes Courants

1. **API non accessible**
   - Vérifier que l'API est démarrée
   - Vérifier l'URL dans la configuration

2. **Base de données non accessible**
   - Vérifier la connexion PostgreSQL
   - Vérifier les credentials dans `config/settings.py`

3. **Modèle non chargé**
   - Vérifier que le fichier de modèle existe
   - Vérifier les permissions de lecture

### Logs de Debug
Les tests incluent des logs de debug pour faciliter le dépannage :
- Erreurs de base de données
- Réponses de l'API
- Données de test

## Maintenance

### Ajouter un Nouveau Test
1. Créer un fichier `test_*.py` dans le dossier `tests/`
2. Suivre la convention de nommage des fonctions : `test_*`
3. Documenter le test dans ce fichier README
4. Ajouter des assertions appropriées

### Mettre à Jour les Tests
- Vérifier la compatibilité avec les nouvelles versions
- Mettre à jour les données de test si nécessaire
- Tester les nouvelles fonctionnalités

## Contact

Pour toute question sur les tests, consulter la documentation du projet ou contacter l'équipe de développement.

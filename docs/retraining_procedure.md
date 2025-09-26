# Procédure de Ré-entraînement du Modèle

## Vue d'ensemble

Cette procédure décrit le processus de ré-entraînement automatique du modèle de classification Cats vs Dogs en utilisant les données de feedback des utilisateurs. Le système permet d'améliorer continuellement les performances du modèle basé sur les retours des utilisateurs.

## Architecture du Système

### Composants Principaux

1. **FeedbackDataHandler** (`src/data/feedback_handler.py`)
   - Gestion des données de feedback depuis PostgreSQL
   - Analyse des statistiques de performance
   - Préparation des données pour le ré-entraînement

2. **ModelRetrainer** (`src/models/retrainer.py`)
   - Orchestration du processus de ré-entraînement
   - Gestion des versions de modèles
   - Évaluation et déploiement des nouveaux modèles

3. **Scripts d'Exécution**
   - `scripts/retrain_model.py` : Ré-entraînement manuel
   - `scripts/retrain_scheduler.py` : Planification automatique

## Conditions de Déclenchement

Le ré-entraînement est déclenché automatiquement lorsque :

- **Nombre minimum de feedbacks** : ≥ 100 (configurable)
- **Feedbacks négatifs** : ≥ 20 (configurable)
- **Taux de satisfaction** : < 70% (configurable)
- **Période d'analyse** : 30 derniers jours (configurable)

## Procédure de Ré-entraînement

### 1. Vérification des Conditions

```bash
# Vérifier les conditions sans exécuter
python scripts/retrain_scheduler.py --check-only

# Mode simulation
python scripts/retrain_model.py --dry-run
```

### 2. Ré-entraînement Manuel

```bash
# Ré-entraînement standard
python scripts/retrain_model.py

# Avec paramètres personnalisés
python scripts/retrain_model.py \
  --days-back 60 \
  --min-feedback 200 \
  --epochs 10 \
  --learning-rate 0.0005

# Ré-entraînement forcé
python scripts/retrain_model.py --force
```

### 3. Planification Automatique

```bash
# Exécution du planificateur
python scripts/retrain_scheduler.py

# Avec fichier de configuration
python scripts/retrain_scheduler.py --config config/retrain_config.json
```

## Configuration

### Variables d'Environnement

```bash
# Configuration de base
export RETRAIN_DAYS_BACK=30
export RETRAIN_MIN_FEEDBACK=100
export RETRAIN_MIN_NEGATIVE=20
export RETRAIN_MIN_POSITIVE_RATE=0.7
export RETRAIN_EPOCHS=5
export RETRAIN_LEARNING_RATE=0.0001
export RETRAIN_CLEANUP=true
export RETRAIN_LOG_LEVEL=INFO
```

### Fichier de Configuration JSON

```json
{
  "days_back": 30,
  "min_feedback": 100,
  "min_negative_feedback": 20,
  "min_positive_rate": 0.7,
  "epochs": 5,
  "learning_rate": 0.0001,
  "cleanup": true,
  "log_level": "INFO",
  "force_retrain": false
}
```

## Processus Détaillé

### Phase 1 : Collecte des Données

1. **Récupération des feedbacks** depuis PostgreSQL
2. **Filtrage** par seuils de confiance et période
3. **Analyse statistique** des performances actuelles

### Phase 2 : Préparation

1. **Sauvegarde** du modèle actuel
2. **Chargement** des données d'entraînement existantes
3. **Intégration** des données de feedback négatif

### Phase 3 : Entraînement

1. **Configuration** des hyperparamètres
2. **Callbacks** de monitoring (early stopping, learning rate reduction)
3. **Entraînement** avec validation croisée

### Phase 4 : Évaluation

1. **Comparaison** avec l'ancien modèle
2. **Métriques** de performance (accuracy, loss)
3. **Décision** de déploiement (seuil d'amélioration : 2%)

### Phase 5 : Déploiement

1. **Remplacement** du modèle en production (si amélioration suffisante)
2. **Sauvegarde** des métriques et historique
3. **Nettoyage** des anciens modèles (optionnel)

## Monitoring et Logging

### Métriques Surveillées

- **Précision** du modèle (accuracy)
- **Perte** (loss) d'entraînement et validation
- **Temps d'inférence** moyen
- **Taux de satisfaction** des utilisateurs
- **Volume** de feedbacks par jour

### Logs Disponibles

- `logs/retrain_scheduler.log` : Logs du planificateur
- `logs/retrain_executions.jsonl` : Historique des exécutions
- `data/processed/models/retrain_metrics_*.json` : Métriques détaillées

### Dashboard

```bash
# Lancer le dashboard de monitoring
python scripts/metrics_dashboard.py
```

Accès : http://127.0.0.1:8050/

## Planification Automatique

### Cron Job (Linux/Mac)

```bash
# Ré-entraînement quotidien à 2h du matin
0 2 * * * cd /path/to/project && python scripts/retrain_scheduler.py

# Vérification toutes les 6 heures
0 */6 * * * cd /path/to/project && python scripts/retrain_scheduler.py --check-only
```

### Task Scheduler (Windows)

1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base
3. Définir le déclencheur (quotidien, 2h00)
4. Action : `python scripts/retrain_scheduler.py`

### Docker (Recommandé)

```dockerfile
# Dans Dockerfile
COPY scripts/retrain_scheduler.py /app/scripts/
RUN chmod +x /app/scripts/retrain_scheduler.py

# Dans docker-compose.yml
services:
  retrain-scheduler:
    build: .
    command: python scripts/retrain_scheduler.py
    environment:
      - RETRAIN_DAYS_BACK=30
      - RETRAIN_MIN_FEEDBACK=100
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
```

## Gestion des Erreurs

### Types d'Erreurs

1. **Erreurs de base de données** : Connexion, requêtes
2. **Erreurs de modèle** : Chargement, sauvegarde
3. **Erreurs d'entraînement** : Mémoire, convergence
4. **Erreurs de déploiement** : Permissions, espace disque

### Stratégies de Récupération

1. **Retry automatique** avec backoff exponentiel
2. **Fallback** vers l'ancien modèle
3. **Alertes** par email/logs
4. **Rollback** automatique en cas d'échec

## Sécurité et Conformité RGPD

### Données Sensibles

- **Aucune image** stockée en base de données
- **Métadonnées uniquement** (confiance, temps, succès)
- **Pseudonymisation** des identifiants utilisateur
- **Rétention limitée** (180 jours par défaut)

### Audit et Traçabilité

- **Logs complets** de toutes les opérations
- **Versioning** des modèles et métriques
- **Historique** des déploiements
- **Métriques** de performance détaillées

## Maintenance

### Nettoyage Régulier

```bash
# Nettoyage manuel
python scripts/retrain_model.py --cleanup

# Nettoyage automatique (configuré par défaut)
export RETRAIN_CLEANUP=true
```

### Surveillance

1. **Vérifier** les logs quotidiennement
2. **Monitorer** les métriques de performance
3. **Valider** les déploiements automatiques
4. **Tester** les modèles en environnement de staging

### Sauvegarde

1. **Modèles** : Sauvegardés automatiquement avant remplacement
2. **Base de données** : Sauvegarde PostgreSQL régulière
3. **Logs** : Rotation automatique des fichiers de log
4. **Configuration** : Versioning Git des fichiers de config

## Dépannage

### Problèmes Courants

1. **"Modèle non trouvé"** : Vérifier le chemin dans `config/settings.py`
2. **"Erreur de base de données"** : Vérifier la connexion PostgreSQL
3. **"Mémoire insuffisante"** : Réduire `batch_size` ou `image_size`
4. **"Aucune amélioration"** : Ajuster les seuils ou augmenter les données

### Commandes de Diagnostic

```bash
# Vérifier l'état du système
python scripts/retrain_scheduler.py --check-only

# Afficher l'historique
python scripts/retrain_model.py --history

# Mode debug
export RETRAIN_LOG_LEVEL=DEBUG
python scripts/retrain_scheduler.py
```

## Évolutions Futures

### Améliorations Prévues

1. **A/B Testing** : Comparaison de modèles en production
2. **Transfer Learning** : Utilisation de modèles pré-entraînés
3. **AutoML** : Optimisation automatique des hyperparamètres
4. **Monitoring temps réel** : Alertes automatiques
5. **Interface web** : Dashboard de gestion des ré-entraînements

### Intégrations

1. **MLflow** : Tracking des expériences
2. **Kubernetes** : Orchestration des jobs
3. **Prometheus** : Métriques de monitoring
4. **Grafana** : Dashboards avancés
5. **Slack/Teams** : Notifications automatiques

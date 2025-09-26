# Architecture du Projet - Computer Vision Cats & Dogs

## Vue d'ensemble

Le projet implémente une solution complète de classification d'images avec monitoring et feedback utilisateur.

## Schéma de l'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Web UI)                        │
├─────────────────────────────────────────────────────────────────┤
│  • Templates Jinja2 (index.html, inference.html, info.html)     │
│  • Interface utilisateur pour upload/prédiction                 │
│  • Dashboard monitoring intégré (Chart.js)                     │
│  • Feedback utilisateur (boutons +/-)                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API FASTAPI                             │
├─────────────────────────────────────────────────────────────────┤
│  • /api/predict (POST) - Prédiction avec authentification     │
│  • /api/feedback (POST) - Enregistrement feedback             │
│  • /api/metrics/daily (GET) - Métriques journalières         │
│  • /api/metrics/7d (GET) - Résumé 7 jours                     │
│  • /info - Page monitoring avec graphiques                     │
│  • Middleware: auth, monitoring, logging                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLE & INFÉRENCE                          │
├─────────────────────────────────────────────────────────────────┤
│  • CatDogPredictor (Keras/TensorFlow)                          │
│  • Monitoring temps d'inférence (metrics.py)                   │
│  • Logging CSV + base de données                               │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BASE DE DONNÉES                             │
├─────────────────────────────────────────────────────────────────┤
│  • PostgreSQL                                                  │
│  • Table: Feedback_user                                        │
│    - feedback (boolean)                                        │
│    - resultat_prediction (float)                               │
│    - input_user (text)                                         │
│    - inference_time_ms (float)                                 │
│    - success (boolean)                                         │
│    - date_feedback (date)                                      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & CI/CD                          │
├─────────────────────────────────────────────────────────────────┤
│  • Dashboard métriques (Chart.js)                              │
│  • Tests automatisés (pytest)                                 │
│  • CI/CD GitHub Actions                                        │
│  • Tests unitaires + intégration DB                           │
└─────────────────────────────────────────────────────────────────┘
```

## Composants détaillés

### 1. Frontend
- **Templates**: `src/web/templates/`
  - `base.html` - Layout principal
  - `index.html` - Page d'accueil
  - `inference.html` - Interface de prédiction + feedback
  - `info.html` - Informations modèle + dashboard monitoring
- **Fonctionnalités**:
  - Upload d'images pour prédiction
  - Affichage résultats avec confiance
  - Feedback utilisateur (positif/négatif)
  - Dashboard temps réel (latence, volume, accord)

### 2. API Backend
- **Routes principales** (`src/api/routes.py`):
  - `POST /api/predict` - Prédiction avec auth Bearer
  - `POST /api/feedback` - Enregistrement feedback en DB
  - `GET /api/metrics/daily` - Métriques journalières
  - `GET /api/metrics/7d` - Résumé 7 jours
- **Authentification**: Token Bearer (`src/api/auth.py`)
- **Monitoring**: Décorateur `@time_inference` pour métriques

### 3. Modèle ML
- **Predictor**: `src/models/predictor.py`
  - Chargement modèle Keras
  - Prédiction avec preprocessing
  - Gestion erreurs
- **Monitoring**: `src/monitoring/metrics.py`
  - Logging temps d'inférence
  - Export CSV + insertion DB

### 4. Base de données
- **Schéma**: `scripts/init-db.sql`
- **Table principale**: `Feedback_user`
  - Métadonnées d'inférence
  - Feedback utilisateur
  - Métriques de performance
- **Configuration**: Variables d'environnement DB_*

### 5. Tests automatisés
- **Tests unitaires**: `tests/test_api_simple.py`
- **Tests d'intégration**: `tests/test_api.py`
- **Tests métriques**: `tests/test_metrics_api.py`
- **Tests modèles**: `tests/test_models.py`

### 6. CI/CD
- **Pipeline**: `.github/workflows/ci.yml`
- **Jobs**:
  - Tests unitaires (sans DB)
  - Tests d'intégration (avec PostgreSQL)
- **Déclenchement**: Push sur main

### 7. Monitoring
- **Dashboard**: Intégré dans `/info`
- **Métriques**:
  - Latence p50/p90/p99
  - Volume d'inférences
  - Taux d'accord (feedback)
- **Visualisation**: Chart.js

## Flux de données

1. **Prédiction**:
   ```
   User → Upload Image → API → Model → Prediction → Response → UI
   ```

2. **Feedback**:
   ```
   User → Feedback Button → API → Database → Metrics Update
   ```

3. **Monitoring**:
   ```
   Database → API Metrics → Dashboard → Charts
   ```

## Sécurité

- **Authentification**: Token Bearer obligatoire
- **Validation**: Types de fichiers, tailles
- **RGPD**: Documentation conformité dans README
- **Variables d'environnement**: Credentials DB

## Déploiement

- **Local**: `python scripts/run_api.py`
- **Docker**: `docker-compose.yml` (PostgreSQL)
- **CI/CD**: GitHub Actions automatique
- **Monitoring**: Dashboard intégré

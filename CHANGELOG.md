# Changelog - Computer Vision Cats & Dogs

## Version 2.0 - Monitoring & Feedback Integration

### 🎯 Objectif
Ajout d'un système complet de monitoring et feedback utilisateur pour améliorer le modèle de classification d'images.

---

## 📋 Modifications apportées

### 1. **Base de données PostgreSQL**

#### Nouveau schéma (`scripts/init-db.sql`)
```sql
CREATE TABLE Feedback_user (
    id_feedback_user SERIAL PRIMARY KEY,
    feedback boolean NOT NULL,
    date_feedback DATE NOT NULL,
    resultat_prediction float NOT NULL,
    input_user text NOT NULL,
    inference_time_ms float,
    success boolean
);
```

#### Configuration DB (`config/settings.py`)
```python
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "computer-vision-cats-dogs"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
}
```

### 2. **API Backend - Nouvelles routes**

#### Route feedback (`src/api/routes.py`)
```python
@router.post("/api/feedback", response_model=FeedbackResponse)
async def feedback_api(payload: FeedbackRequest, token: str = Depends(verify_token)):
    # Insertion en base avec métriques
    # Fallback psycopg/psycopg2
    # Retour avec saved_to_db
```

#### Routes métriques
```python
@router.get("/api/metrics/daily")
async def metrics_daily():
    # Agrégats journaliers: latence p50/p90/p99, volume, feedback

@router.get("/api/metrics/7d") 
async def metrics_7d():
    # Résumé 7 jours glissants
```

#### Modèles Pydantic ajoutés
```python
class FeedbackType(str, Enum):
    positive = "positive"
    negative = "negative"

class FeedbackRequest(BaseModel):
    feedback: FeedbackType
    resultat_prediction: float
    input_user: str

class FeedbackResponse(BaseModel):
    status: str
    feedback: FeedbackType
    resultat_prediction: float
    input_user: str
    timestamp: float
    saved_to_db: bool = False
```

### 3. **Frontend - Interface utilisateur**

#### Template inference.html modifié
- **Feedback utilisateur**: Boutons +/- avec animation
- **Payload correct**: Envoi des bons champs vers `/api/feedback`
- **Gestion d'erreurs**: Messages de confirmation/erreur
- **Variables JavaScript**: `lastPredictionData` pour métriques

#### Template info.html enrichi
- **Dashboard monitoring**: Graphiques Chart.js intégrés
- **Métriques temps réel**: Latence, volume, taux d'accord
- **Scripts**: Chargement automatique des données via API

### 4. **Monitoring et métriques**

#### Module metrics.py étendu (`src/monitoring/metrics.py`)
```python
def read_last_inference_metrics():
    """Lire la dernière ligne des métriques d'inférence"""
    # Lecture CSV avec gestion d'erreurs
    # Retour dict avec timestamp, inference_time_ms, success
```

#### Dashboard autonome (`scripts/metrics_dashboard.py`)
- **FastAPI séparé**: Port 8050, interface Chart.js
- **Endpoints**: `/api/metrics/daily`, `/api/metrics/7d`
- **Visualisation**: Latence p50/p90/p99, volume, accord
- **Fallback DB**: Support psycopg et psycopg2

### 5. **Tests automatisés**

#### Nouveaux tests (`tests/test_metrics_api.py`)
```python
@pytest.mark.skipif(os.environ.get("RUN_DB_TESTS", "0") != "1")
def test_metrics_endpoints_with_data():
    # Test /api/metrics/daily et /api/metrics/7d
    # Vérification structure JSON
```

#### Tests d'intégration DB étendus (`tests/test_api.py`)
```python
def test_feedback_db_integration(self):
    # Test insertion feedback en base
    # Vérification ligne créée
    # Support RUN_DB_TESTS=1
```

### 6. **Pipeline CI/CD**

#### Workflow GitHub Actions (`.github/workflows/ci.yml`)
```yaml
jobs:
  test:
    # Tests unitaires sans DB
    - python -m pytest tests/test_api_simple.py -v -s
    
  test_db:
    # Tests avec PostgreSQL service
    services:
      postgres:
        image: postgres:15
    # Variables DB_* configurées
    # Tests d'intégration DB
```

#### Améliorations CI
- **Services PostgreSQL**: Health checks, configuration automatique
- **Variables d'environnement**: DB_HOST, DB_PORT, etc.
- **Tests conditionnels**: RUN_DB_TESTS pour tests DB
- **Dépendances**: psycopg2-binary ajouté

### 7. **Documentation et conformité**

#### README.md enrichi
- **Section RGPD**: Finalités, minimisation, conservation, droits
- **Sécurité**: Accès DB, chiffrement, sous-traitance
- **Bonnes pratiques**: Pseudonymisation, purge automatique

#### Documentation architecture (`docs/architecture.md`)
- **Schéma complet**: Diagramme architecture
- **Composants détaillés**: Frontend, API, DB, Monitoring
- **Flux de données**: Prédiction, feedback, monitoring
- **Sécurité**: Authentification, validation, RGPD

### 8. **Sécurité et robustesse**

#### Authentification renforcée
- **Token Bearer**: Obligatoire pour toutes les routes sensibles
- **Validation**: Types de fichiers, tailles d'images
- **Gestion d'erreurs**: Messages explicites, codes HTTP appropriés

#### Gestion des dépendances
- **Fallback DB**: Support psycopg et psycopg2
- **Import dynamique**: Évite les erreurs si driver manquant
- **Configuration**: Variables d'environnement pour tous les services

---

## 🚀 Nouvelles fonctionnalités

### Pour les utilisateurs
1. **Feedback sur prédictions**: Boutons +/- avec confirmation
2. **Dashboard monitoring**: Métriques temps réel sur `/info`
3. **Interface améliorée**: Animations, messages de statut

### Pour les développeurs
1. **API métriques**: Endpoints pour monitoring externe
2. **Tests complets**: Unitaires + intégration DB
3. **CI/CD robuste**: Tests automatiques avec PostgreSQL
4. **Documentation**: Architecture, RGPD, bonnes pratiques

### Pour les administrateurs
1. **Monitoring**: Latence, volume, taux d'accord
2. **Base de données**: Historique complet des feedbacks
3. **Sécurité**: Conformité RGPD, audit trail
4. **Déploiement**: Pipeline automatisé, tests de régression

---

## 🔧 Configuration requise

### Dépendances ajoutées
```bash
pip install psycopg2-binary  # ou psycopg[binary]
```

### Variables d'environnement
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=computer-vision-cats-dogs
DB_USER=postgres
DB_PASSWORD=postgres
RUN_DB_TESTS=1  # Pour tests d'intégration
```

### Services requis
- **PostgreSQL**: Base de données pour feedback
- **Python 3.11+**: Support des nouvelles fonctionnalités
- **Node.js**: Pour Chart.js (CDN utilisé)

---

## 📊 Métriques disponibles

### Temps d'inférence
- **P50**: Médiane des temps de réponse
- **P90**: 90e percentile (seuil de performance)
- **P99**: 99e percentile (cas extrêmes)

### Volume et qualité
- **Volume**: Nombre d'inférences par jour
- **Taux d'accord**: Pourcentage de feedback positif
- **Taux d'erreur**: Pourcentage d'inférences échouées

### Surveillance continue
- **Dashboard temps réel**: Mise à jour automatique
- **Historique**: 30 jours de données
- **Résumé 7j**: Vue d'ensemble hebdomadaire

---

## 🎯 Impact et bénéfices

### Amélioration du modèle
- **Données de feedback**: Base pour ré-entraînement
- **Monitoring qualité**: Détection de dérive
- **Optimisation**: Ajustements basés sur l'usage réel

### Expérience utilisateur
- **Interface intuitive**: Feedback simple et clair
- **Transparence**: Métriques visibles
- **Confiance**: Retour utilisateur pris en compte

### Maintenance et opérations
- **Monitoring proactif**: Détection précoce des problèmes
- **Tests automatisés**: Qualité de code garantie
- **Documentation**: Maintenance facilitée

---

## 🔄 Migration et déploiement

### Étapes de déploiement
1. **Base de données**: Exécuter `scripts/init-db.sql`
2. **Variables d'environnement**: Configurer DB_*
3. **Dépendances**: Installer psycopg2-binary
4. **Tests**: Vérifier avec RUN_DB_TESTS=1
5. **Monitoring**: Accéder à `/info` pour dashboard

### Rollback possible
- **API rétrocompatible**: Anciennes routes préservées
- **Base optionnelle**: Fonctionne sans DB (mode dégradé)
- **Configuration**: Variables d'environnement pour activation

---

*Version 2.0 - Décembre 2024*

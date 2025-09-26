# 🐱🐶 Cats & Dogs Classifier - Version Simple

## 📋 Description

Classification d'images de chats et chiens avec enregistrement du nom de fichier dans les feedbacks pour le réentraînement futur.

## ✨ Fonctionnalités

- **Classification d'images** : Distinction chat/chien avec score de confiance
- **API REST** : Interface simple pour les prédictions
- **Interface web** : Upload d'images via navigateur
- **Système de feedback** : Évaluation des prédictions avec nom de fichier
- **Monitoring** : Métriques de performance et feedbacks

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.8+
- PostgreSQL
- Dépendances Python (voir ci-dessous)

### 2. Installation des Dépendances
```bash
pip install fastapi uvicorn python-multipart jinja2 psycopg2-binary tensorflow pillow numpy
```

### 3. Configuration de la Base de Données
```sql
-- Créer la base de données
CREATE DATABASE "computer-vision-cats-dogs";

-- Exécuter le script de création des tables
\i scripts/setup_database.sql
```

### 4. Démarrer l'API
```bash
python scripts/run_api.py
```

### 5. Accéder à l'Application
- **Interface Web** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 📊 Utilisation

### Interface Web
1. Ouvrir http://localhost:8000
2. Cliquer sur "Essayer" pour uploader une image
3. Voir la prédiction et donner un feedback
4. Le nom de fichier est automatiquement enregistré avec le feedback

### API REST
```bash
# Prédiction
curl -X POST "http://localhost:8000/api/predict" \
     -H "Authorization: Bearer ?C@TS&D0GS!" \
     -F "file=@mon_image.jpg"

# Feedback sur une prédiction
curl -X POST "http://localhost:8000/api/feedback" \
     -H "Authorization: Bearer ?C@TS&D0GS!" \
     -H "Content-Type: application/json" \
     -d '{"feedback": "positive", "resultat_prediction": 0.85, "input_user": "test.jpg", "filename": "mon_image.jpg"}'
```

## 🗄️ Base de Données

### Table Principale
- **feedback_user** : Feedbacks des utilisateurs avec nom de fichier
  - `id_feedback_user` : ID unique
  - `feedback` : true/false (positif/négatif)
  - `date_feedback` : Date du feedback
  - `resultat_prediction` : Score de confiance
  - `input_user` : Description utilisateur
  - `filename` : **Nom du fichier image** (nouveau)
  - `inference_time_ms` : Temps d'inférence
  - `success` : Succès de la prédiction

### Structure Simple
- ✅ **Pas de stockage d'images** : Seul le nom de fichier est conservé
- ✅ **Table unique** : Tout dans `feedback_user`
- ✅ **Facile à maintenir** : Structure simple et claire

## 🔧 Configuration

### Variables d'Environnement
```bash
# Base de données
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=computer-vision-cats-dogs
export DB_USER=postgres
export DB_PASSWORD=postgres

# API
export API_TOKEN="?C@TS&D0GS!"
```

### Paramètres Modifiables
- **Taille des images** : `config/settings.py` → `MODEL_CONFIG["image_size"]`
- **Token API** : `config/settings.py` → `API_CONFIG["token"]`

## 📈 Monitoring

### Métriques Disponibles
- **Latence d'inférence** : Temps de réponse moyen
- **Volume de requêtes** : Nombre d'inférences par jour
- **Taux de satisfaction** : Pourcentage de feedbacks positifs
- **Fichiers traités** : Nombre de fichiers uniques

### Endpoints de Monitoring
- `GET /api/metrics/daily` : Métriques journalières
- `GET /api/metrics/7d` : Résumé 7 jours

## 🛠️ Structure du Projet

```
computer-vision-cats-and-dogs/
├── src/
│   ├── api/           # API FastAPI
│   ├── models/        # Modèles ML
│   ├── monitoring/    # Métriques
│   └── web/           # Templates HTML
├── scripts/
│   ├── run_api.py     # Démarrage API
│   └── setup_database.sql  # Création des tables
└── config/
    └── settings.py    # Configuration
```

## 🔄 Workflow de Réentraînement

1. **Collecte** : Noms de fichiers enregistrés avec les feedbacks
2. **Feedback** : Utilisateurs évaluent les prédictions
3. **Export** : Données disponibles pour réentraînement manuel
4. **Simplicité** : Pas de gestion complexe de fichiers

## 📝 Notes Importantes

- **Simplicité** : Pas de stockage d'images, juste les noms de fichiers
- **Performance** : Pas de gestion de fichiers lourde
- **Sécurité** : Token d'authentification requis pour l'API
- **Évolutivité** : Structure simple pour ajouts futurs

## 🆘 Dépannage

### Erreur de base de données
```bash
# Vérifier la connexion
psql -h localhost -U postgres -d computer-vision-cats-dogs

# Recréer les tables
psql -h localhost -U postgres -d computer-vision-cats-dogs -f scripts/setup_database.sql
```

### Erreur de port
```bash
# Changer le port dans scripts/run_api.py
uvicorn.run(app, host="127.0.0.1", port=8001)
```

### Erreur de dépendances
```bash
# Réinstaller
pip install --upgrade fastapi uvicorn tensorflow
```

---

**Version** : 1.0.0 - Simple  
**Auteur** : Formation IA Greta  
**Licence** : MIT

# Nettoyage des Données de Test

## 🧹 Vue d'Ensemble

Ce document explique comment nettoyer les données de test de la base de données pour éviter l'accumulation de données non pertinentes.

## 🎯 Pourquoi Nettoyer ?

### Problèmes sans Nettoyage
- **Accumulation de données** : Les tests créent des données qui s'accumulent
- **Fausses métriques** : Les données de test faussent les statistiques
- **Performance dégradée** : Plus de données = requêtes plus lentes
- **Confusion** : Mélange entre données réelles et de test

### Avantages du Nettoyage
- ✅ **Métriques précises** : Seules les données réelles sont comptées
- ✅ **Performance optimale** : Base de données légère
- ✅ **Tests reproductibles** : Environnement propre à chaque test
- ✅ **Sécurité** : Pas de données de test en production

## 🛠️ Méthodes de Nettoyage

### 1. **Nettoyage Automatique (Recommandé)**

#### A. Via Makefile
```bash
# Nettoyer les données de test
make clean-db

# Voir les statistiques
make stats-db
```

#### B. Via Script Direct
```bash
# Nettoyage intelligent (recommandé)
python scripts/cleanup_test_data.py --clean

# Voir les statistiques
python scripts/cleanup_test_data.py --stats

# Supprimer TOUTES les données (ATTENTION!)
python scripts/cleanup_test_data.py --clean-all
```

### 2. **Nettoyage Manuel**

#### A. Via SQL Direct
```sql
-- Supprimer les données de test
DELETE FROM feedback_user WHERE input_user LIKE '%test_%';
DELETE FROM feedback_user WHERE input_user LIKE '%unknown%';
DELETE FROM feedback_user WHERE input_user LIKE '%mon_image%';

-- Supprimer les données récentes (dernières 24h)
DELETE FROM feedback_user WHERE date_feedback >= CURRENT_DATE - INTERVAL '1 day';
```

#### B. Via Interface Admin
- Utiliser pgAdmin ou DBeaver
- Exécuter les requêtes SQL ci-dessus
- Vérifier les résultats

### 3. **Nettoyage Automatique dans les Tests**

Les tests nettoient automatiquement après exécution :
```python
# Dans test_feedback_db.py
def pytest_sessionfinish(session, exitstatus):
    cleanup_after_tests()
```

## 🔍 Identification des Données de Test

### Patterns de Test Détectés
- `test_*` : Tous les fichiers commençant par "test_"
- `test_image*` : Images de test
- `test_database*` : Tests de base de données
- `unknown` : Fichiers non identifiés
- `mon_image*` : Images génériques
- `test_feedback*` : Tests de feedback

### Critères Temporels
- **Dernières 2 heures** : Données récentes (probablement des tests)
- **Dernières 24 heures** : Données du jour (peuvent être des tests)

## 📊 Surveillance des Données

### Statistiques Disponibles
```bash
python scripts/cleanup_test_data.py --stats
```

**Exemple de sortie :**
```
📊 Statistiques des données:
   📈 Total des enregistrements: 150
   👍 Positif: 120
   👍 Négatif: 30
   🕐 Dernières 24h: 25
   🧪 Données de test: 20
```

### Métriques Importantes
- **Total** : Nombre total d'enregistrements
- **Par type** : Feedback positif vs négatif
- **Récentes** : Données des dernières 24h
- **Tests** : Données identifiées comme tests

## ⚙️ Configuration

### Variables d'Environnement
```bash
# Configuration de la base de données
DB_HOST=localhost
DB_PORT=5432
DB_NAME=computer-vision-cats-dogs
DB_USER=postgres
DB_PASSWORD=postgres
```

### Patterns Personnalisés
Modifiez `scripts/cleanup_test_data.py` pour ajouter vos propres patterns :
```python
test_patterns = [
    "test_",
    "test_image",
    "test_database",
    "unknown",
    "mon_image",
    "votre_pattern_ici"  # Ajoutez vos patterns
]
```

## 🚨 Sécurité et Précautions

### ⚠️ **ATTENTION : Suppression Irréversible**
- Les données supprimées ne peuvent pas être récupérées
- Toujours faire une sauvegarde avant nettoyage massif
- Tester sur un environnement de développement d'abord

### 🛡️ **Bonnes Pratiques**
1. **Sauvegarde** : Faire une sauvegarde avant nettoyage
2. **Test** : Tester sur un environnement de dev
3. **Vérification** : Vérifier les statistiques avant/après
4. **Monitoring** : Surveiller l'impact sur les performances

### 🔒 **Sauvegarde Recommandée**
```bash
# Sauvegarde avant nettoyage
pg_dump -h localhost -U postgres -d computer-vision-cats-dogs > backup_before_cleanup.sql

# Restauration si nécessaire
psql -h localhost -U postgres -d computer-vision-cats-dogs < backup_before_cleanup.sql
```

## 🔄 Automatisation

### 1. **Nettoyage Périodique**
```bash
# Crontab (Linux/Mac) - Nettoyage quotidien à 2h du matin
0 2 * * * cd /path/to/project && python scripts/cleanup_test_data.py --clean

# Task Scheduler (Windows) - Nettoyage quotidien
# Créer une tâche planifiée exécutant le script
```

### 2. **Nettoyage Post-Tests**
Les tests nettoient automatiquement après exécution (déjà configuré).

### 3. **Nettoyage CI/CD**
Le workflow GitHub Actions nettoie automatiquement après les tests.

## 📈 Monitoring et Alertes

### Seuils d'Alerte
- **> 1000 enregistrements** : Base de données volumineuse
- **> 50% de données de test** : Nettoyage nécessaire
- **> 100 enregistrements/jour** : Activité élevée

### Script de Monitoring
```bash
# Vérifier l'état de la base
python scripts/cleanup_test_data.py --stats

# Nettoyer si nécessaire
if [ $(python scripts/cleanup_test_data.py --stats | grep "Total" | cut -d: -f2) -gt 1000 ]; then
    python scripts/cleanup_test_data.py --clean
fi
```

## 🎯 Résumé des Commandes

### Commandes Essentielles
```bash
# Voir les statistiques
make stats-db
# ou
python scripts/cleanup_test_data.py --stats

# Nettoyer les données de test
make clean-db
# ou
python scripts/cleanup_test_data.py --clean

# Nettoyage complet (ATTENTION!)
python scripts/cleanup_test_data.py --clean-all
```

### Commandes de Maintenance
```bash
# Tests avec nettoyage automatique
python -m pytest tests/test_feedback_db.py -v

# Nettoyage manuel via SQL
psql -h localhost -U postgres -d computer-vision-cats-dogs -c "DELETE FROM feedback_user WHERE input_user LIKE '%test_%';"
```

## 📞 Support

En cas de problème :
1. Vérifier les logs d'erreur
2. Tester sur un environnement de développement
3. Consulter la documentation de la base de données
4. Contacter l'équipe de développement

Le nettoyage des données de test est essentiel pour maintenir un environnement propre et des métriques précises !

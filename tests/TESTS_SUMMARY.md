# Résumé des Tests - Cats vs Dogs Classifier

## Vue d'Ensemble

| Catégorie | Nombre de Tests | Fichier | Status |
|-----------|----------------|---------|--------|
| API Principale | 15+ | `test_api.py` | ✅ Actif |
| API Simple | 1 | `test_api_simple.py` | ✅ Actif |
| Métriques | 3+ | `test_metrics_api.py` | ✅ Actif |
| Modèles | 1+ | `test_models.py` | ✅ Actif |
| Feedback UI | 3 | `test_feedback_ui.py` | ✅ Actif |
| Feedback Messages | 4 | `test_feedback_ui_message.py` | ✅ Actif |
| Feedback DB | 2 | `test_feedback_db.py` | ✅ Actif |
| **TOTAL** | **29+** | **7 fichiers** | **✅ Actif** |

## Tests par Priorité

### 🔴 Critique (Doivent passer)
- `test_api_simple.py` - Vérification de base de l'API
- `test_feedback_db.py` - Enregistrement en base de données
- `test_api.py` - Fonctionnalités principales

### 🟡 Important (Recommandés)
- `test_feedback_ui.py` - Interface utilisateur
- `test_metrics_api.py` - Monitoring et métriques
- `test_feedback_ui_message.py` - Messages de confirmation

### 🟢 Optionnels (Bonus)
- `test_models.py` - Tests des modèles ML

## Commandes Rapides

### Tests Essentiels
```bash
# Vérification rapide
python -m pytest tests/test_api_simple.py -v

# Tests de base de données
python -m pytest tests/test_feedback_db.py -v

# Tests API complets
python -m pytest tests/test_api.py -v
```

### Tests Complets
```bash
# Tous les tests
python -m pytest tests/ -v -s

# Avec couverture
python -m pytest tests/ --cov=src --cov-report=html
```

### Tests Spécifiques
```bash
# Tests feedback uniquement
python -m pytest tests/test_feedback_*.py -v

# Tests métriques uniquement
python -m pytest tests/test_metrics_api.py -v
```

## Scripts d'Exécution

### Windows
```cmd
tests\run_tests.bat
```

### Linux/Mac
```bash
./tests/run_tests.sh
```

## Diagnostic

### Vérifier la Base de Données
```bash
python scripts/check_feedback_table.py
```

### Vérifier l'API
```bash
python -m pytest tests/test_api_simple.py -v -s
```

## Résultats Attendus

### Tests de Base (Doivent passer)
- ✅ API accessible
- ✅ Modèle chargé
- ✅ Feedback enregistré en base
- ✅ Métriques disponibles

### Tests Avancés (Recommandés)
- ✅ Interface utilisateur fonctionnelle
- ✅ Messages de confirmation
- ✅ Gestion des erreurs
- ✅ Authentification

## Dépannage

### Problèmes Courants

1. **API non accessible**
   ```bash
   # Vérifier que l'API est démarrée
   python scripts/run_api.py
   ```

2. **Base de données non accessible**
   ```bash
   # Vérifier la connexion
   python scripts/check_feedback_table.py
   ```

3. **Modèle non chargé**
   ```bash
   # Vérifier les logs de l'API
   # Vérifier que le fichier de modèle existe
   ```

### Logs de Debug
- Les tests incluent des logs détaillés
- Les erreurs de base de données sont affichées
- Les réponses de l'API sont loggées

## Maintenance

### Ajouter un Nouveau Test
1. Créer `test_*.py` dans le dossier `tests/`
2. Suivre la convention de nommage
3. Documenter dans `README_TESTS.md`
4. Ajouter au script d'exécution

### Mettre à Jour les Tests
- Vérifier la compatibilité
- Mettre à jour les données de test
- Tester les nouvelles fonctionnalités

## Métriques de Qualité

### Couverture de Code
- Objectif : > 80%
- Commande : `python -m pytest tests/ --cov=src --cov-report=html`

### Temps d'Exécution
- Tests rapides : < 30 secondes
- Tests complets : < 2 minutes

### Fiabilité
- Tous les tests critiques doivent passer
- Tests idempotents (peuvent être exécutés plusieurs fois)
- Gestion propre des erreurs

## Contact et Support

- Documentation : `docs/`
- Tests : `tests/`
- Scripts : `scripts/`
- Configuration : `config/`

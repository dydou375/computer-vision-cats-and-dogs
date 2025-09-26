# Makefile pour le projet Computer Vision Cats & Dogs

.PHONY: help env install train retrain retrain-check retrain-force clean test api dashboard

# Aide
help:
	@echo "Commandes disponibles:"
	@echo "  env          - Créer l'environnement virtuel et installer les dépendances"
	@echo "  install      - Installer les dépendances de base"
	@echo "  install-dev  - Installer les dépendances de développement"
	@echo "  install-prod - Installer les dépendances de production"
	@echo "  train        - Entraîner le modèle initial"
	@echo "  retrain      - Ré-entraîner le modèle avec les données de feedback"
	@echo "  retrain-check- Vérifier les conditions de ré-entraînement"
	@echo "  retrain-force- Forcer le ré-entraînement"
	@echo "  retrain-history- Afficher l'historique des ré-entraînements"
	@echo "  api          - Lancer l'API FastAPI"
	@echo "  dashboard    - Lancer le dashboard de monitoring"
	@echo "  test         - Exécuter les tests"
	@echo "  clean        - Nettoyer les fichiers temporaires"
	@echo "  clean-db     - Nettoyer les données de test de la base"
	@echo "  stats-db     - Afficher les statistiques de la base"

# Créer l'environnement virtuel et installer les dépendances
env:
	python -m venv venv
	venv\Scripts\activate
	pip install --upgrade pip
	pip install -r requirements\base.txt
	pip install -r requirements\dev.txt

# Installer les dépendances de base
install:
	pip install -r requirements\base.txt

# Installer les dépendances de développement
install-dev:
	pip install -r requirements\dev.txt

# Installer les dépendances de production
install-prod:
	pip install -r requirements\prod.txt

# Entraîner le modèle initial
train:
	python scripts\train.py

# Ré-entraîner le modèle avec les données de feedback
retrain:
	python scripts\retrain_model.py

# Vérifier les conditions de ré-entraînement
retrain-check:
	python scripts\retrain_model.py --dry-run

# Forcer le ré-entraînement
retrain-force:
	python scripts\retrain_model.py --force

# Afficher l'historique des ré-entraînements
retrain-history:
	python scripts\retrain_model.py --history

# Lancer l'API FastAPI
api:
	python scripts\run_api.py

# Lancer le dashboard de monitoring
dashboard:
	python scripts\metrics_dashboard.py

# Exécuter les tests
test:
	python -m pytest tests\ -v

# Nettoyer les fichiers temporaires
clean:
	@echo "Nettoyage des fichiers temporaires..."

# Nettoyer les données de test de la base de données
clean-db:
	python scripts\cleanup_test_data.py --clean

# Afficher les statistiques de la base de données
stats-db:
	python scripts\cleanup_test_data.py --stats
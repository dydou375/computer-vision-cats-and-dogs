# Makefile pour le projet Computer Vision Cats & Dogs

.PHONY: help env install train retrain retrain-check retrain-force clean test api dashboard

# Aide
help:
	@echo "Commandes disponibles:"
	@echo "  env          - Créer l'environnement virtuel et installer les dépendances"
	@echo "  install      - Installer les dépendances dans l'environnement actuel"
	@echo "  train        - Entraîner le modèle initial"
	@echo "  retrain      - Ré-entraîner le modèle avec les données de feedback"
	@echo "  retrain-check- Vérifier les conditions de ré-entraînement"
	@echo "  retrain-force- Forcer le ré-entraînement"
	@echo "  retrain-history- Afficher l'historique des ré-entraînements"
	@echo "  api          - Lancer l'API FastAPI"
	@echo "  dashboard    - Lancer le dashboard de monitoring"
	@echo "  test         - Exécuter les tests"
	@echo "  clean        - Nettoyer les fichiers temporaires"

# Créer l'environnement virtuel et installer les dépendances
env:
	python -m venv venv
	venv\Scripts\activate
	pip install --upgrade pip
	pip install -r requirements\base.txt
	pip install -r requirements\dev.txt

# Installer les dépendances
install:
	pip install -r requirements\base.txt

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
	@if exist "data\processed\models\backups" rmdir /s /q "data\processed\models\backups"
	@if exist "logs" rmdir /s /q "logs"
	@if exist "__pycache__" rmdir /s /q "__pycache__"
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@echo "Nettoyage terminé"
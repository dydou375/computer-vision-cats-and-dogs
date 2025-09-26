#!/usr/bin/env python3
"""
Planificateur automatique de ré-entraînement du modèle.

Ce script peut être exécuté périodiquement (via cron, task scheduler, etc.)
pour déclencher automatiquement le ré-entraînement du modèle basé sur les
données de feedback disponibles.

Usage:
    python scripts/retrain_scheduler.py [--config CONFIG_FILE]

Configuration via variables d'environnement:
    RETRAIN_DAYS_BACK=30
    RETRAIN_MIN_FEEDBACK=100
    RETRAIN_MIN_NEGATIVE=20
    RETRAIN_MIN_POSITIVE_RATE=0.7
    RETRAIN_EPOCHS=5
    RETRAIN_LEARNING_RATE=0.0001
    RETRAIN_CLEANUP=true
    RETRAIN_LOG_LEVEL=INFO
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.models.retrainer import ModelRetrainer
from src.data.feedback_handler import FeedbackDataHandler


def setup_logging(log_level: str = "INFO"):
    """Configure le système de logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(ROOT_DIR / "logs" / "retrain_scheduler.log", mode='a')
        ]
    )
    
    # Créer le répertoire de logs s'il n'existe pas
    (ROOT_DIR / "logs").mkdir(exist_ok=True)


def load_config(config_file: Path = None) -> dict:
    """Charge la configuration depuis un fichier ou les variables d'environnement."""
    config = {
        "days_back": int(os.environ.get("RETRAIN_DAYS_BACK", "30")),
        "min_feedback": int(os.environ.get("RETRAIN_MIN_FEEDBACK", "100")),
        "min_negative_feedback": int(os.environ.get("RETRAIN_MIN_NEGATIVE", "20")),
        "min_positive_rate": float(os.environ.get("RETRAIN_MIN_POSITIVE_RATE", "0.7")),
        "epochs": int(os.environ.get("RETRAIN_EPOCHS", "5")),
        "learning_rate": float(os.environ.get("RETRAIN_LEARNING_RATE", "0.0001")),
        "cleanup": os.environ.get("RETRAIN_CLEANUP", "true").lower() == "true",
        "log_level": os.environ.get("RETRAIN_LOG_LEVEL", "INFO"),
        "force_retrain": os.environ.get("RETRAIN_FORCE", "false").lower() == "true"
    }
    
    # Charger depuis un fichier de configuration si fourni
    if config_file and config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logging.warning(f"Erreur lors du chargement de la configuration {config_file}: {e}")
    
    return config


def check_retrain_conditions(config: dict) -> tuple[bool, dict]:
    """Vérifie si les conditions de ré-entraînement sont remplies."""
    feedback_handler = FeedbackDataHandler()
    
    should_retrain, stats = feedback_handler.should_retrain(
        min_feedback_count=config["min_feedback"],
        min_negative_feedback=config["min_negative_feedback"],
        min_positive_rate=config["min_positive_rate"]
    )
    
    return should_retrain or config["force_retrain"], stats


def execute_retraining(config: dict, logger: logging.Logger) -> dict:
    """Exécute le ré-entraînement du modèle."""
    retrainer = ModelRetrainer()
    
    logger.info("Début du ré-entraînement automatique")
    logger.info(f"Configuration: {config}")
    
    try:
        results = retrainer.retrain_with_feedback(
            days_back=config["days_back"],
            min_feedback_count=config["min_feedback"],
            min_negative_feedback=config["min_negative_feedback"],
            min_positive_rate=config["min_positive_rate"],
            retrain_epochs=config["epochs"],
            learning_rate=config["learning_rate"]
        )
        
        # Logging des résultats
        if results.get("status") == "completed":
            logger.info(f"Ré-entraînement terminé avec succès")
            logger.info(f"Précision finale: {results.get('final_accuracy', 0):.4f}")
            logger.info(f"Amélioration: {results.get('improvement', 0):.4f}")
            logger.info(f"Déploiement: {results.get('deployment_status', 'N/A')}")
            
            if results.get("deployment_status") == "deployed":
                logger.info("✅ Nouveau modèle déployé en production")
            else:
                logger.warning("⚠️ Nouveau modèle non déployé (amélioration insuffisante)")
        
        elif results.get("status") == "skipped":
            logger.info(f"Ré-entraînement ignoré: {results.get('reason', 'N/A')}")
        
        elif results.get("status") == "failed":
            logger.error(f"Échec du ré-entraînement: {results.get('error', 'N/A')}")
        
        # Nettoyage si configuré
        if config["cleanup"] and results.get("status") == "completed":
            logger.info("Nettoyage des anciens modèles...")
            retrainer.cleanup_old_models()
            logger.info("Nettoyage terminé")
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors du ré-entraînement: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def save_execution_log(results: dict, config: dict):
    """Sauvegarde le log d'exécution."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "results": results
    }
    
    log_file = ROOT_DIR / "logs" / "retrain_executions.jsonl"
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    """Fonction principale du planificateur."""
    parser = argparse.ArgumentParser(
        description="Planificateur automatique de ré-entraînement",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Fichier de configuration JSON (optionnel)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode simulation sans exécution réelle"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Vérifier seulement les conditions sans exécuter le ré-entraînement"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    config = load_config(args.config)
    
    # Configurer le logging
    setup_logging(config["log_level"])
    logger = logging.getLogger(__name__)
    
    logger.info("=== DÉMARRAGE DU PLANIFICATEUR DE RÉ-ENTRAÎNEMENT ===")
    logger.info(f"Configuration: {config}")
    
    try:
        # Vérifier les conditions de ré-entraînement
        should_retrain, stats = check_retrain_conditions(config)
        
        logger.info(f"Statistiques des feedbacks: {stats}")
        logger.info(f"Ré-entraînement nécessaire: {'OUI' if should_retrain else 'NON'}")
        
        if args.check_only:
            logger.info("Mode vérification uniquement - arrêt")
            return
        
        if not should_retrain:
            logger.info("Conditions de ré-entraînement non remplies - arrêt")
            results = {
                "status": "skipped",
                "reason": "Conditions non remplies",
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
        else:
            if args.dry_run:
                logger.info("Mode simulation - arrêt")
                results = {
                    "status": "simulated",
                    "reason": "Mode simulation",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Exécuter le ré-entraînement
                results = execute_retraining(config, logger)
        
        # Sauvegarder le log d'exécution
        save_execution_log(results, config)
        
        logger.info("=== FIN DU PLANIFICATEUR ===")
        
        # Code de sortie basé sur le statut
        if results.get("status") == "failed":
            sys.exit(1)
        elif results.get("status") == "skipped":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

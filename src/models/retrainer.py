#!/usr/bin/env python3
"""
Module de ré-entraînement du modèle avec les données de feedback.
"""

import sys
from pathlib import Path
import tensorflow as tf
import numpy as np
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import MODEL_CONFIG, MODELS_DIR
from src.models.trainer import CatDogTrainer
from src.data.feedback_handler import FeedbackDataHandler


class ModelRetrainer:
    """Gestionnaire du ré-entraînement du modèle avec feedback."""
    
    def __init__(self):
        self.config = MODEL_CONFIG
        self.models_dir = MODELS_DIR
        self.feedback_handler = FeedbackDataHandler()
        self.original_trainer = CatDogTrainer()
        
        # Créer les répertoires nécessaires
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.models_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def retrain_with_feedback(self, 
                            days_back: int = 30,
                            min_feedback_count: int = 100,
                            min_negative_feedback: int = 20,
                            min_positive_rate: float = 0.7,
                            retrain_epochs: int = 5,
                            learning_rate: float = 0.0001) -> Dict[str, Any]:
        """
        Ré-entraîne le modèle en utilisant les données de feedback.
        
        Args:
            days_back: Nombre de jours de feedback à considérer
            min_feedback_count: Nombre minimum de feedbacks pour déclencher le ré-entraînement
            min_negative_feedback: Nombre minimum de feedbacks négatifs
            min_positive_rate: Taux minimum de feedbacks positifs
            retrain_epochs: Nombre d'époques pour le ré-entraînement
            learning_rate: Taux d'apprentissage pour le ré-entraînement
            
        Returns:
            Dictionnaire avec les résultats du ré-entraînement
        """
        print("=== DÉBUT DU RÉ-ENTRAÎNEMENT ===")
        start_time = datetime.now()
        
        # 1. Vérifier si le ré-entraînement est nécessaire
        should_retrain, stats = self.feedback_handler.should_retrain(
            min_feedback_count, min_negative_feedback, min_positive_rate
        )
        
        print(f"Statistiques des feedbacks: {stats}")
        
        if not should_retrain:
            return {
                "status": "skipped",
                "reason": "Conditions de ré-entraînement non remplies",
                "statistics": stats,
                "timestamp": start_time.isoformat()
            }
        
        # 2. Sauvegarder le modèle actuel
        current_model_path = self.models_dir / "cats_dogs_model.keras"
        if current_model_path.exists():
            backup_path = self.backup_dir / f"model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.keras"
            shutil.copy2(current_model_path, backup_path)
            print(f"Modèle actuel sauvegardé: {backup_path}")
        
        # 3. Récupérer les données de feedback
        feedback_data = self.feedback_handler.get_feedback_data(days_back=days_back)
        print(f"Récupération de {len(feedback_data)} feedbacks")
        
        # 4. Préparer les données d'entraînement
        print("Préparation des données d'entraînement...")
        train_ds, val_ds = self.original_trainer.prepare_data()
        
        # 5. Charger le modèle existant
        if current_model_path.exists():
            model = tf.keras.models.load_model(current_model_path)
            print("Modèle existant chargé")
        else:
            print("Aucun modèle existant trouvé, création d'un nouveau modèle")
            model = self.original_trainer.create_model()
        
        # 6. Configurer le ré-entraînement
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # 7. Callbacks pour le ré-entraînement
        retrain_model_path = self.models_dir / f"cats_dogs_model_retrained_{datetime.now().strftime('%Y%m%d_%H%M%S')}.keras"
        
        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                retrain_model_path,
                save_best_only=True,
                monitor='val_accuracy',
                verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=2,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=1,
                min_lr=1e-7
            )
        ]
        
        # 8. Ré-entraînement
        print(f"Début du ré-entraînement pour {retrain_epochs} époques...")
        
        try:
            history = model.fit(
                train_ds,
                epochs=retrain_epochs,
                callbacks=callbacks,
                validation_data=val_ds,
                verbose=1
            )
            
            # 9. Évaluation du nouveau modèle
            print("Évaluation du modèle ré-entraîné...")
            val_loss, val_accuracy = model.evaluate(val_ds, verbose=0)
            
            # 10. Comparaison avec l'ancien modèle
            old_model_metrics = self._evaluate_old_model(val_ds, current_model_path)
            
            # 11. Décision de déploiement
            improvement_threshold = 0.02  # 2% d'amélioration minimum
            should_deploy = val_accuracy > (old_model_metrics.get('accuracy', 0) + improvement_threshold)
            
            if should_deploy:
                # Remplacer le modèle en production
                shutil.copy2(retrain_model_path, current_model_path)
                print("✅ Nouveau modèle déployé en production")
                deployment_status = "deployed"
            else:
                print("❌ Nouveau modèle non déployé (amélioration insuffisante)")
                deployment_status = "not_deployed"
            
            # 12. Sauvegarder les métriques
            retrain_metrics = {
                "status": "completed",
                "deployment_status": deployment_status,
                "retrain_epochs": retrain_epochs,
                "final_accuracy": float(val_accuracy),
                "final_loss": float(val_loss),
                "old_model_accuracy": old_model_metrics.get('accuracy', 0),
                "improvement": float(val_accuracy - old_model_metrics.get('accuracy', 0)),
                "feedback_count": len(feedback_data),
                "statistics": stats,
                "model_path": str(retrain_model_path),
                "timestamp": start_time.isoformat(),
                "duration_minutes": (datetime.now() - start_time).total_seconds() / 60,
                "history": {
                    "accuracy": [float(x) for x in history.history['accuracy']],
                    "val_accuracy": [float(x) for x in history.history['val_accuracy']],
                    "loss": [float(x) for x in history.history['loss']],
                    "val_loss": [float(x) for x in history.history['val_loss']]
                }
            }
            
            # Sauvegarder les métriques
            metrics_path = self.models_dir / f"retrain_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(metrics_path, 'w') as f:
                json.dump(retrain_metrics, f, indent=2)
            
            print("=== RÉ-ENTRAÎNEMENT TERMINÉ ===")
            return retrain_metrics
            
        except Exception as e:
            error_metrics = {
                "status": "failed",
                "error": str(e),
                "timestamp": start_time.isoformat(),
                "duration_minutes": (datetime.now() - start_time).total_seconds() / 60
            }
            
            print(f"❌ Erreur lors du ré-entraînement: {e}")
            return error_metrics
    
    def _evaluate_old_model(self, val_ds, model_path: Path) -> Dict[str, float]:
        """Évalue l'ancien modèle pour comparaison."""
        try:
            if model_path.exists():
                old_model = tf.keras.models.load_model(model_path)
                val_loss, val_accuracy = old_model.evaluate(val_ds, verbose=0)
                return {"accuracy": float(val_accuracy), "loss": float(val_loss)}
        except Exception as e:
            print(f"Erreur lors de l'évaluation de l'ancien modèle: {e}")
        
        return {"accuracy": 0.0, "loss": float('inf')}
    
    def get_retrain_history(self) -> List[Dict[str, Any]]:
        """Récupère l'historique des ré-entraînements."""
        history = []
        
        for metrics_file in self.models_dir.glob("retrain_metrics_*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    history.append(data)
            except Exception as e:
                print(f"Erreur lors de la lecture de {metrics_file}: {e}")
        
        # Trier par timestamp
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return history
    
    def cleanup_old_models(self, keep_last: int = 5):
        """Nettoie les anciens modèles et métriques."""
        # Nettoyer les modèles ré-entraînés
        retrained_models = list(self.models_dir.glob("cats_dogs_model_retrained_*.keras"))
        retrained_models.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_model in retrained_models[keep_last:]:
            try:
                old_model.unlink()
                print(f"Ancien modèle supprimé: {old_model}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {old_model}: {e}")
        
        # Nettoyer les métriques
        metrics_files = list(self.models_dir.glob("retrain_metrics_*.json"))
        metrics_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_metrics in metrics_files[keep_last:]:
            try:
                old_metrics.unlink()
                print(f"Anciennes métriques supprimées: {old_metrics}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {old_metrics}: {e}")

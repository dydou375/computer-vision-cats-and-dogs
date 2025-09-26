#!/usr/bin/env python3
"""
Gestionnaire des données de feedback pour le ré-entraînement du modèle.
"""

import sys
from pathlib import Path
import importlib
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import io
import base64

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG, MODEL_CONFIG


class FeedbackDataHandler:
    """Gestionnaire des données de feedback pour le ré-entraînement."""
    
    def __init__(self):
        self.db_config = DB_CONFIG
        self.image_size = MODEL_CONFIG["image_size"]
        self._connect_db = self._get_db_connection()
    
    def _get_db_connection(self):
        """Récupère la fonction de connexion à la base de données."""
        try:
            dbmod = importlib.import_module("psycopg")
            return dbmod.connect
        except Exception:
            dbmod = importlib.import_module("psycopg2")
            return dbmod.connect
    
    def get_feedback_data(self, 
                         days_back: int = 30, 
                         min_confidence_threshold: float = 0.7,
                         include_negative_feedback: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les données de feedback depuis la base de données.
        
        Args:
            days_back: Nombre de jours à remonter pour récupérer les données
            min_confidence_threshold: Seuil de confiance minimum pour inclure les données
            include_negative_feedback: Inclure les feedbacks négatifs
            
        Returns:
            Liste des données de feedback formatées
        """
        query = """
        SELECT 
            id_feedback_user,
            feedback,
            date_feedback,
            resultat_prediction,
            input_user,
            inference_time_ms,
            success
        FROM Feedback_user 
        WHERE date_feedback >= %s
        AND resultat_prediction >= %s
        ORDER BY date_feedback DESC
        """
        
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (cutoff_date, min_confidence_threshold))
                cols = [c[0] for c in cur.description]
                rows = cur.fetchall()
                
                feedback_data = []
                for row in rows:
                    item = dict(zip(cols, row))
                    
                    # Filtrer les feedbacks négatifs si demandé
                    if not include_negative_feedback and not item['feedback']:
                        continue
                    
                    feedback_data.append(item)
        
        return feedback_data
    
    def get_feedback_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Récupère les statistiques des feedbacks.
        
        Args:
            days_back: Nombre de jours à analyser
            
        Returns:
            Dictionnaire avec les statistiques
        """
        query = """
        SELECT 
            COUNT(*) as total_feedback,
            SUM(CASE WHEN feedback = true THEN 1 ELSE 0 END) as positive_feedback,
            SUM(CASE WHEN feedback = false THEN 1 ELSE 0 END) as negative_feedback,
            AVG(resultat_prediction) as avg_confidence,
            AVG(inference_time_ms) as avg_inference_time,
            MIN(date_feedback) as earliest_feedback,
            MAX(date_feedback) as latest_feedback
        FROM Feedback_user 
        WHERE date_feedback >= %s
        """
        
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (cutoff_date,))
                row = cur.fetchone()
                
                if row:
                    return {
                        'total_feedback': row[0],
                        'positive_feedback': row[1],
                        'negative_feedback': row[2],
                        'avg_confidence': float(row[3]) if row[3] else 0.0,
                        'avg_inference_time': float(row[4]) if row[4] else 0.0,
                        'earliest_feedback': row[5].isoformat() if row[5] else None,
                        'latest_feedback': row[6].isoformat() if row[6] else None,
                        'positive_rate': row[1] / row[0] if row[0] > 0 else 0.0
                    }
        
        return {}
    
    def prepare_training_data_from_feedback(self, 
                                          feedback_data: List[Dict[str, Any]],
                                          data_dir: Path) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prépare les données d'entraînement à partir des feedbacks.
        
        Args:
            feedback_data: Données de feedback
            data_dir: Répertoire de données existant
            
        Returns:
            Tuple (images, labels) pour l'entraînement
        """
        images = []
        labels = []
        
        # Charger les données existantes
        import tensorflow as tf
        train_ds, _ = tf.keras.utils.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            subset="training",
            seed=1337,
            image_size=self.image_size,
            batch_size=1,  # Un par un pour traiter les feedbacks
        )
        
        # Convertir en listes pour manipulation
        existing_images = []
        existing_labels = []
        
        for batch_images, batch_labels in train_ds:
            for img, label in zip(batch_images, batch_labels):
                existing_images.append(img.numpy())
                existing_labels.append(label.numpy())
        
        # Ajouter les données existantes
        images.extend(existing_images)
        labels.extend(existing_labels)
        
        # Traiter les feedbacks négatifs comme données d'entraînement supplémentaires
        negative_feedbacks = [f for f in feedback_data if not f['feedback']]
        
        print(f"Traitement de {len(negative_feedbacks)} feedbacks négatifs...")
        
        for feedback in negative_feedbacks:
            try:
                # Pour les feedbacks négatifs, on inverse la prédiction
                # Si le modèle a prédit "dog" avec confiance élevée mais c'était "cat"
                predicted_class = "dog" if feedback['resultat_prediction'] > 0.5 else "cat"
                correct_class = "cat" if predicted_class == "dog" else "dog"
                
                # Créer une image synthétique basée sur la classe correcte
                # (Dans un vrai système, on aurait l'image originale)
                synthetic_image = self._create_synthetic_image(correct_class)
                
                images.append(synthetic_image)
                labels.append(1 if correct_class == "dog" else 0)  # 1 pour dog, 0 pour cat
                
            except Exception as e:
                print(f"Erreur lors du traitement du feedback {feedback['id_feedback_user']}: {e}")
                continue
        
        return np.array(images), np.array(labels)
    
    def _create_synthetic_image(self, class_name: str) -> np.ndarray:
        """
        Crée une image synthétique pour la classe donnée.
        Dans un vrai système, on récupérerait l'image originale.
        """
        # Créer une image aléatoire avec des patterns différents selon la classe
        if class_name == "dog":
            # Pattern pour chien (plus de contrastes)
            image = np.random.randint(0, 255, (*self.image_size, 3), dtype=np.uint8)
            # Ajouter des patterns spécifiques aux chiens
            image[20:40, 20:40] = [255, 200, 100]  # Zone "museau"
            image[60:80, 60:80] = [100, 50, 25]    # Zone "corps"
        else:  # cat
            # Pattern pour chat (plus doux)
            image = np.random.randint(50, 200, (*self.image_size, 3), dtype=np.uint8)
            # Ajouter des patterns spécifiques aux chats
            image[30:50, 30:50] = [200, 150, 100]  # Zone "museau"
            image[70:90, 70:90] = [150, 100, 75]   # Zone "corps"
        
        return image.astype(np.float32) / 255.0
    
    def should_retrain(self, 
                      min_feedback_count: int = 100,
                      min_negative_feedback: int = 20,
                      min_positive_rate: float = 0.7) -> Tuple[bool, Dict[str, Any]]:
        """
        Détermine si le modèle doit être ré-entraîné.
        
        Args:
            min_feedback_count: Nombre minimum de feedbacks
            min_negative_feedback: Nombre minimum de feedbacks négatifs
            min_positive_rate: Taux minimum de feedbacks positifs
            
        Returns:
            Tuple (should_retrain, statistics)
        """
        stats = self.get_feedback_statistics()
        
        should_retrain = (
            stats.get('total_feedback', 0) >= min_feedback_count and
            stats.get('negative_feedback', 0) >= min_negative_feedback and
            stats.get('positive_rate', 1.0) < min_positive_rate
        )
        
        return should_retrain, stats

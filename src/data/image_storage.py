#!/usr/bin/env python3
"""
Gestionnaire de stockage des images d'utilisateurs pour le réentraînement.
"""

import sys
from pathlib import Path
import importlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
import uuid
import shutil
from PIL import Image
import io
import base64

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG


class ImageStorageManager:
    """Gestionnaire de stockage des images d'utilisateurs."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.db_config = DB_CONFIG
        self.storage_dir = storage_dir or ROOT_DIR / "data" / "user_images"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._connect_db = self._get_db_connection()
    
    def _get_db_connection(self):
        """Récupère la fonction de connexion à la base de données."""
        try:
            dbmod = importlib.import_module("psycopg")
            return dbmod.connect
        except Exception:
            dbmod = importlib.import_module("psycopg2")
            return dbmod.connect
    
    def store_user_image(self, 
                        image_data: bytes, 
                        filename: str,
                        user_id: Optional[str] = None,
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stocke une image d'utilisateur sur le disque et en base de données.
        
        Args:
            image_data: Données binaires de l'image
            filename: Nom du fichier original
            user_id: ID de l'utilisateur (optionnel)
            session_id: ID de session (optionnel)
            
        Returns:
            Dictionnaire avec les métadonnées de l'image stockée
        """
        try:
            # Générer un nom de fichier unique
            file_hash = hashlib.md5(image_data).hexdigest()
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{file_hash}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            # Chemin de stockage
            file_path = self.storage_dir / unique_filename
            
            # Charger et analyser l'image
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Sauvegarder l'image
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Enregistrer en base de données
            with self._connect_db(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO user_images 
                        (filename, file_path, file_size, image_width, image_height, user_id, session_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_image, uploaded_at
                        """,
                        (
                            filename,
                            str(file_path),
                            len(image_data),
                            width,
                            height,
                            user_id,
                            session_id
                        )
                    )
                    result = cur.fetchone()
                    conn.commit()
                    
                    return {
                        'id_image': result[0],
                        'filename': filename,
                        'file_path': str(file_path),
                        'file_size': len(image_data),
                        'image_width': width,
                        'image_height': height,
                        'uploaded_at': result[1].isoformat(),
                        'user_id': user_id,
                        'session_id': session_id
                    }
                    
        except Exception as e:
            # Nettoyer le fichier en cas d'erreur
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise Exception(f"Erreur lors du stockage de l'image: {e}")
    
    def link_image_to_feedback(self, image_id: int, feedback_id: int) -> bool:
        """
        Lie une image à un feedback.
        
        Args:
            image_id: ID de l'image
            feedback_id: ID du feedback
            
        Returns:
            True si la liaison a réussi
        """
        try:
            with self._connect_db(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO image_feedback_link (id_image, id_feedback_user)
                        VALUES (%s, %s)
                        ON CONFLICT (id_image, id_feedback_user) DO NOTHING
                        """,
                        (image_id, feedback_id)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Erreur lors de la liaison image-feedback: {e}")
            return False
    
    def get_images_for_retraining(self, 
                                 days_back: int = 30,
                                 min_confidence: float = 0.7,
                                 include_negative_feedback: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les images pour le réentraînement.
        
        Args:
            days_back: Nombre de jours à remonter
            min_confidence: Seuil de confiance minimum
            include_negative_feedback: Inclure les feedbacks négatifs
            
        Returns:
            Liste des images avec leurs métadonnées
        """
        query = """
        SELECT 
            ui.id_image,
            ui.filename,
            ui.file_path,
            ui.file_size,
            ui.image_width,
            ui.image_height,
            ui.uploaded_at,
            ui.user_id,
            ui.session_id,
            fu.feedback,
            fu.resultat_prediction,
            fu.date_feedback
        FROM user_images ui
        JOIN image_feedback_link ifl ON ui.id_image = ifl.id_image
        JOIN feedback_user fu ON ifl.id_feedback_user = fu.id_feedback_user
        WHERE ui.uploaded_at >= %s
        AND fu.resultat_prediction >= %s
        """
        
        if not include_negative_feedback:
            query += " AND fu.feedback = true"
        
        query += " ORDER BY ui.uploaded_at DESC"
        
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (cutoff_date, min_confidence))
                cols = [c[0] for c in cur.description]
                rows = cur.fetchall()
                
                images = []
                for row in rows:
                    item = dict(zip(cols, row))
                    # Convertir les dates en string
                    if item.get('uploaded_at'):
                        item['uploaded_at'] = item['uploaded_at'].isoformat()
                    if item.get('date_feedback'):
                        item['date_feedback'] = item['date_feedback'].isoformat()
                    images.append(item)
                
                return images
    
    def get_image_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère une image par son ID.
        
        Args:
            image_id: ID de l'image
            
        Returns:
            Métadonnées de l'image ou None
        """
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM user_images WHERE id_image = %s",
                    (image_id,)
                )
                row = cur.fetchone()
                
                if row:
                    cols = [c[0] for c in cur.description]
                    item = dict(zip(cols, row))
                    if item.get('uploaded_at'):
                        item['uploaded_at'] = item['uploaded_at'].isoformat()
                    return item
                
                return None
    
    def load_image_data(self, image_id: int) -> Optional[bytes]:
        """
        Charge les données binaires d'une image.
        
        Args:
            image_id: ID de l'image
            
        Returns:
            Données binaires de l'image ou None
        """
        image_info = self.get_image_by_id(image_id)
        if not image_info:
            return None
        
        file_path = Path(image_info['file_path'])
        if not file_path.exists():
            return None
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def mark_image_processed(self, image_id: int, status: str = 'processed') -> bool:
        """
        Marque une image comme traitée.
        
        Args:
            image_id: ID de l'image
            status: Statut de traitement (processed, error)
            
        Returns:
            True si la mise à jour a réussi
        """
        try:
            with self._connect_db(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE user_images 
                        SET is_processed = %s, processing_status = %s
                        WHERE id_image = %s
                        """,
                        (status == 'processed', status, image_id)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {e}")
            return False
    
    def cleanup_old_images(self, days_old: int = 90) -> int:
        """
        Nettoie les anciennes images.
        
        Args:
            days_old: Âge minimum des images à supprimer (en jours)
            
        Returns:
            Nombre d'images supprimées
        """
        cutoff_date = datetime.now().date() - timedelta(days=days_old)
        deleted_count = 0
        
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                # Récupérer les images à supprimer
                cur.execute(
                    "SELECT id_image, file_path FROM user_images WHERE uploaded_at < %s",
                    (cutoff_date,)
                )
                old_images = cur.fetchall()
                
                for image_id, file_path in old_images:
                    try:
                        # Supprimer le fichier
                        if Path(file_path).exists():
                            Path(file_path).unlink()
                        
                        # Supprimer de la base de données
                        cur.execute("DELETE FROM user_images WHERE id_image = %s", (image_id,))
                        deleted_count += 1
                        
                    except Exception as e:
                        print(f"Erreur lors de la suppression de l'image {image_id}: {e}")
                
                conn.commit()
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de stockage.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        with self._connect_db(
            host=self.db_config["host"],
            port=self.db_config["port"],
            dbname=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        COUNT(*) as total_images,
                        SUM(file_size) as total_size,
                        AVG(file_size) as avg_size,
                        COUNT(CASE WHEN is_processed = TRUE THEN 1 END) as processed_images,
                        COUNT(CASE WHEN processing_status = 'error' THEN 1 END) as error_images
                    FROM user_images
                    """
                )
                row = cur.fetchone()
                
                if row:
                    return {
                        'total_images': row[0],
                        'total_size_bytes': row[1] or 0,
                        'total_size_mb': (row[1] or 0) / (1024 * 1024),
                        'avg_size_bytes': row[2] or 0,
                        'processed_images': row[3],
                        'error_images': row[4],
                        'storage_directory': str(self.storage_dir)
                    }
                
                return {}

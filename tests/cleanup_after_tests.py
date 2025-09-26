#!/usr/bin/env python3
"""Script de nettoyage automatique après les tests"""

import sys
from pathlib import Path
import importlib
from datetime import datetime, timedelta

# Configuration
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG

def cleanup_after_tests():
    """Nettoie automatiquement les données après les tests"""
    try:
        # Connexion à la base de données
        try:
            dbmod = importlib.import_module("psycopg")
            connect = dbmod.connect
        except Exception:
            dbmod = importlib.import_module("psycopg2")
            connect = dbmod.connect

        with connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        ) as conn:
            with conn.cursor() as cur:
                # Supprimer les données de test récentes (dernières 2 heures)
                two_hours_ago = datetime.now() - timedelta(hours=2)
                cur.execute(
                    "DELETE FROM feedback_user WHERE date_feedback >= %s",
                    (two_hours_ago,)
                )
                deleted_count = cur.rowcount
                
                # Supprimer les données avec des patterns de test
                test_patterns = [
                    "test_",
                    "test_image",
                    "test_database",
                    "test_success",
                    "test_error",
                    "unknown",
                    "mon_image",
                    "test_feedback"
                ]
                
                for pattern in test_patterns:
                    cur.execute(
                        "DELETE FROM feedback_user WHERE input_user LIKE %s",
                        (f"%{pattern}%",)
                    )
                    deleted_count += cur.rowcount
                
                conn.commit()
                
                if deleted_count > 0:
                    print(f"🧹 Nettoyage automatique: {deleted_count} enregistrements supprimés")
                else:
                    print("✅ Aucune donnée de test à nettoyer")
                
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage automatique: {e}")
        # Ne pas faire échouer les tests pour un problème de nettoyage

if __name__ == "__main__":
    cleanup_after_tests()

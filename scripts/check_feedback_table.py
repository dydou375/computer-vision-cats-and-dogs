#!/usr/bin/env python3
"""Script pour vérifier la structure de la table feedback_user"""

import sys
from pathlib import Path
import importlib

# Configuration
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG

def check_feedback_table():
    """Vérifier la structure de la table feedback_user"""
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
                # Vérifier la structure de la table
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'feedback_user'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                
                print("=== Structure de la table feedback_user ===")
                if columns:
                    for col in columns:
                        print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                else:
                    print("  Table feedback_user non trouvée!")
                
                # Vérifier les données existantes
                cur.execute("SELECT COUNT(*) FROM feedback_user;")
                count = cur.fetchone()[0]
                print(f"\n=== Nombre d'enregistrements ===")
                print(f"  Total: {count}")
                
                # Afficher les 5 derniers enregistrements
                if count > 0:
                    cur.execute("""
                        SELECT id_feedback_user, feedback, date_feedback, resultat_prediction, input_user, inference_time_ms, success
                        FROM feedback_user 
                        ORDER BY id_feedback_user DESC 
                        LIMIT 5;
                    """)
                    
                    records = cur.fetchall()
                    print(f"\n=== 5 derniers enregistrements ===")
                    for record in records:
                        print(f"  ID: {record[0]}, Feedback: {record[1]}, Date: {record[2]}, Confidence: {record[3]}, Input: {record[4]}, Time: {record[5]}, Success: {record[6]}")
                
    except Exception as e:
        print(f"Erreur lors de la vérification de la base de données: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_feedback_table()

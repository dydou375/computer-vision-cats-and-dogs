#!/usr/bin/env python3
"""Script pour nettoyer les données de test de la base de données"""

import sys
from pathlib import Path
import importlib
from datetime import datetime, timedelta

# Configuration
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG

def cleanup_test_data():
    """Nettoie les données de test de la base de données"""
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
                print("🧹 Nettoyage des données de test...")
                
                # Compter les données avant nettoyage
                cur.execute("SELECT COUNT(*) FROM feedback_user;")
                count_before = cur.fetchone()[0]
                print(f"   📊 Données avant nettoyage: {count_before}")
                
                # Supprimer les données de test (basées sur des patterns)
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
                
                deleted_count = 0
                for pattern in test_patterns:
                    cur.execute(
                        "DELETE FROM feedback_user WHERE input_user LIKE %s",
                        (f"%{pattern}%",)
                    )
                    deleted_count += cur.rowcount
                
                # Supprimer les données récentes (moins de 24h) qui pourraient être des tests
                yesterday = datetime.now() - timedelta(days=1)
                cur.execute(
                    "DELETE FROM feedback_user WHERE date_feedback >= %s",
                    (yesterday,)
                )
                deleted_count += cur.rowcount
                
                # Compter les données après nettoyage
                cur.execute("SELECT COUNT(*) FROM feedback_user;")
                count_after = cur.fetchone()[0]
                
                conn.commit()
                
                print(f"   ✅ Données supprimées: {deleted_count}")
                print(f"   📊 Données restantes: {count_after}")
                print("   🎉 Nettoyage terminé avec succès!")
                
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()

def cleanup_all_data():
    """Supprime TOUTES les données (ATTENTION: destructif!)"""
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
                print("⚠️  ATTENTION: Suppression de TOUTES les données!")
                
                # Compter les données avant suppression
                cur.execute("SELECT COUNT(*) FROM feedback_user;")
                count_before = cur.fetchone()[0]
                print(f"   📊 Données à supprimer: {count_before}")
                
                # Supprimer toutes les données
                cur.execute("DELETE FROM feedback_user;")
                deleted_count = cur.rowcount
                
                conn.commit()
                
                print(f"   ✅ Données supprimées: {deleted_count}")
                print("   🎉 Suppression terminée!")
                
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        import traceback
        traceback.print_exc()

def show_data_stats():
    """Affiche les statistiques des données"""
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
                print("📊 Statistiques des données:")
                
                # Total des données
                cur.execute("SELECT COUNT(*) FROM feedback_user;")
                total = cur.fetchone()[0]
                print(f"   📈 Total des enregistrements: {total}")
                
                # Données par type de feedback
                cur.execute("""
                    SELECT 
                        CASE WHEN feedback = true THEN 'Positif' ELSE 'Négatif' END as type,
                        COUNT(*) as count
                    FROM feedback_user 
                    GROUP BY feedback
                """)
                feedback_stats = cur.fetchall()
                for stat in feedback_stats:
                    print(f"   👍 {stat[0]}: {stat[1]}")
                
                # Données récentes (dernières 24h)
                yesterday = datetime.now() - timedelta(days=1)
                cur.execute(
                    "SELECT COUNT(*) FROM feedback_user WHERE date_feedback >= %s",
                    (yesterday,)
                )
                recent = cur.fetchone()[0]
                print(f"   🕐 Dernières 24h: {recent}")
                
                # Données de test (basées sur des patterns)
                test_patterns = ["test_", "test_image", "test_database", "unknown"]
                test_count = 0
                for pattern in test_patterns:
                    cur.execute(
                        "SELECT COUNT(*) FROM feedback_user WHERE input_user LIKE %s",
                        (f"%{pattern}%",)
                    )
                    test_count += cur.fetchone()[0]
                print(f"   🧪 Données de test: {test_count}")
                
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des statistiques: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nettoyage des données de test")
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques")
    parser.add_argument("--clean", action="store_true", help="Nettoyer les données de test")
    parser.add_argument("--clean-all", action="store_true", help="Supprimer TOUTES les données (ATTENTION!)")
    
    args = parser.parse_args()
    
    if args.stats:
        show_data_stats()
    elif args.clean:
        cleanup_test_data()
    elif args.clean_all:
        print("⚠️  ATTENTION: Cette action va supprimer TOUTES les données!")
        confirm = input("Êtes-vous sûr? (tapez 'OUI' pour confirmer): ")
        if confirm == "OUI":
            cleanup_all_data()
        else:
            print("❌ Opération annulée")
    else:
        print("Utilisation:")
        print("  python scripts/cleanup_test_data.py --stats     # Afficher les statistiques")
        print("  python scripts/cleanup_test_data.py --clean     # Nettoyer les données de test")
        print("  python scripts/cleanup_test_data.py --clean-all # Supprimer TOUTES les données")

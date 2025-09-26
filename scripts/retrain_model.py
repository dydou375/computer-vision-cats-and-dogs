#!/usr/bin/env python3
"""
Script de ré-entraînement du modèle avec les données de feedback.

Usage:
    python scripts/retrain_model.py [--days-back DAYS] [--min-feedback MIN] [--epochs EPOCHS]

Exemples:
    # Ré-entraînement standard
    python scripts/retrain_model.py
    
    # Ré-entraînement avec paramètres personnalisés
    python scripts/retrain_model.py --days-back 60 --min-feedback 200 --epochs 10
    
    # Ré-entraînement forcé (ignore les conditions)
    python scripts/retrain_model.py --force
"""

import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.models.retrainer import ModelRetrainer
from src.data.feedback_handler import FeedbackDataHandler


def main():
    """Fonction principale du script de ré-entraînement."""
    parser = argparse.ArgumentParser(
        description="Ré-entraînement du modèle Cats vs Dogs avec données de feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python scripts/retrain_model.py
  python scripts/retrain_model.py --days-back 60 --min-feedback 200
  python scripts/retrain_model.py --force --epochs 10
  python scripts/retrain_model.py --dry-run
        """
    )
    
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="Nombre de jours de feedback à considérer (défaut: 30)"
    )
    
    parser.add_argument(
        "--min-feedback",
        type=int,
        default=100,
        help="Nombre minimum de feedbacks pour déclencher le ré-entraînement (défaut: 100)"
    )
    
    parser.add_argument(
        "--min-negative-feedback",
        type=int,
        default=20,
        help="Nombre minimum de feedbacks négatifs (défaut: 20)"
    )
    
    parser.add_argument(
        "--min-positive-rate",
        type=float,
        default=0.7,
        help="Taux minimum de feedbacks positifs (défaut: 0.7)"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Nombre d'époques pour le ré-entraînement (défaut: 5)"
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.0001,
        help="Taux d'apprentissage pour le ré-entraînement (défaut: 0.0001)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcer le ré-entraînement même si les conditions ne sont pas remplies"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulation sans exécution réelle"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Nettoyer les anciens modèles après le ré-entraînement"
    )
    
    parser.add_argument(
        "--history",
        action="store_true",
        help="Afficher l'historique des ré-entraînements"
    )
    
    args = parser.parse_args()
    
    # Afficher l'historique si demandé
    if args.history:
        retrainer = ModelRetrainer()
        history = retrainer.get_retrain_history()
        
        print("=== HISTORIQUE DES RÉ-ENTRAÎNEMENTS ===")
        if not history:
            print("Aucun ré-entraînement trouvé.")
        else:
            for i, record in enumerate(history, 1):
                print(f"\n--- Ré-entraînement #{i} ---")
                print(f"Date: {record.get('timestamp', 'N/A')}")
                print(f"Statut: {record.get('status', 'N/A')}")
                print(f"Déploiement: {record.get('deployment_status', 'N/A')}")
                print(f"Précision finale: {record.get('final_accuracy', 0):.4f}")
                print(f"Amélioration: {record.get('improvement', 0):.4f}")
                print(f"Nombre de feedbacks: {record.get('feedback_count', 0)}")
                print(f"Durée: {record.get('duration_minutes', 0):.1f} minutes")
        return
    
    # Mode simulation
    if args.dry_run:
        print("=== MODE SIMULATION ===")
        feedback_handler = FeedbackDataHandler()
        
        # Vérifier les conditions
        should_retrain, stats = feedback_handler.should_retrain(
            args.min_feedback, args.min_negative_feedback, args.min_positive_rate
        )
        
        print(f"Statistiques des feedbacks ({args.days_back} derniers jours):")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\nConditions de ré-entraînement:")
        print(f"  Nombre minimum de feedbacks: {args.min_feedback}")
        print(f"  Nombre minimum de feedbacks négatifs: {args.min_negative_feedback}")
        print(f"  Taux minimum de feedbacks positifs: {args.min_positive_rate}")
        print(f"  Ré-entraînement nécessaire: {'OUI' if should_retrain else 'NON'}")
        
        if should_retrain or args.force:
            print(f"\nParamètres du ré-entraînement:")
            print(f"  Époques: {args.epochs}")
            print(f"  Taux d'apprentissage: {args.learning_rate}")
            print(f"  Jours de feedback: {args.days_back}")
        else:
            print("\n❌ Ré-entraînement non nécessaire selon les conditions actuelles.")
            print("   Utilisez --force pour forcer le ré-entraînement.")
        
        return
    
    # Ré-entraînement réel
    print("=== RÉ-ENTRAÎNEMENT DU MODÈLE ===")
    print(f"Paramètres:")
    print(f"  Jours de feedback: {args.days_back}")
    print(f"  Feedback minimum: {args.min_feedback}")
    print(f"  Feedback négatif minimum: {args.min_negative_feedback}")
    print(f"  Taux positif minimum: {args.min_positive_rate}")
    print(f"  Époques: {args.epochs}")
    print(f"  Taux d'apprentissage: {args.learning_rate}")
    print(f"  Mode forcé: {'OUI' if args.force else 'NON'}")
    print()
    
    retrainer = ModelRetrainer()
    
    try:
        # Ajuster les paramètres si mode forcé
        if args.force:
            args.min_feedback = 1
            args.min_negative_feedback = 0
            args.min_positive_rate = 0.0
        
        # Exécuter le ré-entraînement
        results = retrainer.retrain_with_feedback(
            days_back=args.days_back,
            min_feedback_count=args.min_feedback,
            min_negative_feedback=args.min_negative_feedback,
            min_positive_rate=args.min_positive_rate,
            retrain_epochs=args.epochs,
            learning_rate=args.learning_rate
        )
        
        # Afficher les résultats
        print("\n=== RÉSULTATS ===")
        print(f"Statut: {results.get('status', 'N/A')}")
        
        if results.get('status') == 'completed':
            print(f"Déploiement: {results.get('deployment_status', 'N/A')}")
            print(f"Précision finale: {results.get('final_accuracy', 0):.4f}")
            print(f"Précision ancien modèle: {results.get('old_model_accuracy', 0):.4f}")
            print(f"Amélioration: {results.get('improvement', 0):.4f}")
            print(f"Nombre de feedbacks traités: {results.get('feedback_count', 0)}")
            print(f"Durée: {results.get('duration_minutes', 0):.1f} minutes")
            
            if results.get('deployment_status') == 'deployed':
                print("✅ Nouveau modèle déployé avec succès!")
            else:
                print("⚠️  Nouveau modèle non déployé (amélioration insuffisante)")
        
        elif results.get('status') == 'skipped':
            print(f"Raison: {results.get('reason', 'N/A')}")
            print("ℹ️  Ré-entraînement non nécessaire")
        
        elif results.get('status') == 'failed':
            print(f"Erreur: {results.get('error', 'N/A')}")
            print("❌ Échec du ré-entraînement")
            sys.exit(1)
        
        # Nettoyage si demandé
        if args.cleanup and results.get('status') == 'completed':
            print("\n=== NETTOYAGE ===")
            retrainer.cleanup_old_models()
            print("Nettoyage terminé")
        
        # Sauvegarder les résultats
        results_file = ROOT_DIR / "data" / "processed" / f"retrain_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nRésultats sauvegardés: {results_file}")
        
    except KeyboardInterrupt:
        print("\n❌ Ré-entraînement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors du ré-entraînement: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

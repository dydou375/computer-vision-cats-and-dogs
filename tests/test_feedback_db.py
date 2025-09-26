#!/usr/bin/env python3
"""Test pour vérifier l'enregistrement du feedback en base de données"""

import pytest
import requests
import sys
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import API_CONFIG

# Configuration des tests
BASE_URL = "http://localhost:8000"
TOKEN = API_CONFIG["token"]

def test_feedback_database_insertion():
    """Test que le feedback s'enregistre correctement en base de données"""
    try:
        payload = {
            "feedback": "positive",
            "resultat_prediction": 0.95,
            "input_user": "test_database.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            },
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["feedback"] == "positive"
        assert data["resultat_prediction"] == 0.95
        assert data["input_user"] == "test_database.jpg"
        
        # Vérifier que saved_to_db est True
        assert data["saved_to_db"] == True, f"Le feedback n'a pas été sauvegardé en base. saved_to_db = {data.get('saved_to_db')}"
        
        print(f"\n✅ Test enregistrement en base réussi")
        print(f"   - Status: {data['status']}")
        print(f"   - Feedback: {data['feedback']}")
        print(f"   - Confidence: {data['resultat_prediction']}")
        print(f"   - Input User: {data['input_user']}")
        print(f"   - Saved to DB: {data['saved_to_db']}")
        print(f"   - Timestamp: {data['timestamp']}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test d'enregistrement en base: {e}")

def test_feedback_database_negative():
    """Test que le feedback négatif s'enregistre correctement en base de données"""
    try:
        payload = {
            "feedback": "negative",
            "resultat_prediction": 0.25,
            "input_user": "test_database_negative.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}"
            },
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["feedback"] == "negative"
        assert data["resultat_prediction"] == 0.25
        assert data["input_user"] == "test_database_negative.jpg"
        
        # Vérifier que saved_to_db est True
        assert data["saved_to_db"] == True, f"Le feedback n'a pas été sauvegardé en base. saved_to_db = {data.get('saved_to_db')}"
        
        print(f"\n📝 Test enregistrement feedback négatif réussi")
        print(f"   - Status: {data['status']}")
        print(f"   - Feedback: {data['feedback']}")
        print(f"   - Confidence: {data['resultat_prediction']}")
        print(f"   - Input User: {data['input_user']}")
        print(f"   - Saved to DB: {data['saved_to_db']}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test d'enregistrement feedback négatif: {e}")

# Nettoyage automatique après les tests
def pytest_sessionfinish(session, exitstatus):
    """Nettoyage automatique après les tests"""
    try:
        from tests.cleanup_after_tests import cleanup_after_tests
        cleanup_after_tests()
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage automatique: {e}")

# Permet l'exécution directe du fichier
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

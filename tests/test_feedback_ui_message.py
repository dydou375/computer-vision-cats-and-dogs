#!/usr/bin/env python3
"""Test pour vérifier la fonctionnalité de feedback UI avec messages de confirmation"""

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

def test_feedback_ui_success_message():
    """Test que le feedback positif affiche un message de confirmation"""
    try:
        payload = {
            "feedback": "positive",
            "resultat_prediction": 0.92,
            "input_user": "test_success.jpg"
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
        assert data["resultat_prediction"] == 0.92
        assert data["input_user"] == "test_success.jpg"
        
        print(f"\n✅ Test feedback positif réussi")
        print(f"   - Status: {data['status']}")
        print(f"   - Feedback: {data['feedback']}")
        print(f"   - Confidence: {data['resultat_prediction']}")
        print(f"   - Saved to DB: {data.get('saved_to_db')}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de feedback positif: {e}")

def test_feedback_ui_error_message():
    """Test que le feedback négatif affiche un message de confirmation"""
    try:
        payload = {
            "feedback": "negative",
            "resultat_prediction": 0.35,
            "input_user": "test_error.jpg"
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
        assert data["resultat_prediction"] == 0.35
        assert data["input_user"] == "test_error.jpg"
        
        print(f"\n📝 Test feedback négatif réussi")
        print(f"   - Status: {data['status']}")
        print(f"   - Feedback: {data['feedback']}")
        print(f"   - Confidence: {data['resultat_prediction']}")
        print(f"   - Saved to DB: {data.get('saved_to_db')}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de feedback négatif: {e}")

def test_feedback_ui_invalid_data():
    """Test avec des données invalides"""
    try:
        payload = {
            "feedback": "invalid_feedback",
            "resultat_prediction": "not_a_number",
            "input_user": ""
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
        
        # Devrait retourner une erreur 422 (validation error)
        assert response.status_code == 422
        
        print(f"\n⚠️ Test données invalides réussi - erreur 422 retournée")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de données invalides: {e}")

def test_feedback_ui_no_token():
    """Test sans token d'autorisation"""
    try:
        payload = {
            "feedback": "positive",
            "resultat_prediction": 0.85,
            "input_user": "test_no_token.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        # Devrait retourner une erreur 401 (unauthorized)
        assert response.status_code == 401
        
        print(f"\n🔒 Test sans token réussi - erreur 401 retournée")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test sans token: {e}")

# Permet l'exécution directe du fichier
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

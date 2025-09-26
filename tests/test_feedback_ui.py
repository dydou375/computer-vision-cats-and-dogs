#!/usr/bin/env python3
"""Test pour vérifier la fonctionnalité de feedback UI"""

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

def test_feedback_positive():
    """Test du feedback positif"""
    try:
        payload = {
            "feedback": "positive",
            "resultat_prediction": 0.85,
            "input_user": "test_image.jpg"
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
        assert data["resultat_prediction"] == 0.85
        assert data["input_user"] == "test_image.jpg"
        
        print(f"\nFeedback positif envoyé avec succès")
        print(f"Timestamp: {data.get('timestamp')}")
        print(f"Saved to DB: {data.get('saved_to_db')}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de feedback: {e}")

def test_feedback_negative():
    """Test du feedback négatif"""
    try:
        payload = {
            "feedback": "negative",
            "resultat_prediction": 0.45,
            "input_user": "test_image2.jpg"
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
        assert data["resultat_prediction"] == 0.45
        assert data["input_user"] == "test_image2.jpg"
        
        print(f"\nFeedback négatif envoyé avec succès")
        print(f"Timestamp: {data.get('timestamp')}")
        print(f"Saved to DB: {data.get('saved_to_db')}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de feedback: {e}")

def test_feedback_invalid_token():
    """Test avec un token invalide"""
    try:
        payload = {
            "feedback": "positive",
            "resultat_prediction": 0.85,
            "input_user": "test_image.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid_token"
            },
            timeout=5
        )
        
        # Devrait retourner une erreur 401
        assert response.status_code == 401
        
        print(f"\nTest token invalide réussi - erreur 401 retournée")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur lors du test de token invalide: {e}")

# Permet l'exécution directe du fichier
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

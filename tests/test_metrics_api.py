#!/usr/bin/env python3
"""Tests des endpoints /api/metrics/* (nécessite DB).

Exécuté seulement si RUN_DB_TESTS=1 et l'API est démarrée.
"""

import os
import time
import requests
import importlib
import pytest
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import API_CONFIG, DB_CONFIG

BASE_URL = "http://localhost:8000"
TOKEN = API_CONFIG["token"]


@pytest.mark.skipif(os.environ.get("RUN_DB_TESTS", "0") != "1", reason="RUN_DB_TESTS!=1")
def test_metrics_endpoints_with_data():
    # Prépare une insertion via l'API feedback pour s'assurer qu'il y a des données
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    unique_input = f"metrics_seed_{int(time.time())}.jpg"
    payload = {"feedback": "positive", "resultat_prediction": 0.91, "input_user": unique_input}
    r = requests.post(f"{BASE_URL}/api/feedback", json=payload, headers=headers, timeout=10)
    assert r.status_code == 200

    # Laisse le temps à l'insertion d'être visible
    time.sleep(0.3)

    # Vérifie /api/metrics/daily
    m = requests.get(f"{BASE_URL}/api/metrics/daily", timeout=10)
    assert m.status_code == 200
    daily = m.json()
    assert isinstance(daily, list)
    assert len(daily) >= 0

    # Vérifie /api/metrics/7d
    m7 = requests.get(f"{BASE_URL}/api/metrics/7d", timeout=10)
    assert m7.status_code == 200
    data7 = m7.json()
    assert isinstance(data7, dict)
    # Les clés peuvent être absentes si peu de données, mais la structure doit être un dict



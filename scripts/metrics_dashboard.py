#!/usr/bin/env python3
"""Mini dashboard FastAPI + Chart.js basé sur les métriques en base.

Lancez:
python scripts/metrics_dashboard.py

Puis ouvrez:
http://127.0.0.1:8050/
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import importlib
from typing import Any, Dict, List
from datetime import date

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import DB_CONFIG


def get_db_connect():
    try:
        dbmod = importlib.import_module("psycopg")
        return dbmod.connect
    except Exception:
        dbmod = importlib.import_module("psycopg2")
        return dbmod.connect


app = FastAPI(title="Metrics Dashboard", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def dashboard_page():
    html = """
<!DOCTYPE html>
<html lang=\"fr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Metrics Dashboard</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }
    .row { display: grid; grid-template-columns: 1fr; gap: 24px; }
    @media (min-width: 1000px) { .row { grid-template-columns: 1fr 1fr; } }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    h2 { margin: 0 0 16px; font-size: 18px; }
    canvas { max-height: 360px; }
  </style>
  </head>
  <body>
    <h1>Dashboard - Inference & Feedback</h1>
    <div class=\"row\">
      <div class=\"card\">
        <h2>Latence (p50/p90/p99) par jour</h2>
        <canvas id=\"latencyChart\"></canvas>
      </div>
      <div class=\"card\">
        <h2>Volume & Taux d'accord</h2>
        <canvas id=\"volumeChart\"></canvas>
      </div>
      <div class=\"card\">
        <h2>Résumé 7 jours</h2>
        <pre id=\"summary7d\"></pre>
      </div>
    </div>

    <script>
      async function fetchJSON(url) {
        const r = await fetch(url);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }

      function toDateLabel(d) { return d; }

      async function load() {
        const daily = await fetchJSON('/api/metrics/daily');
        const m7d = await fetchJSON('/api/metrics/7d');

        // Latency chart
        const labels = daily.map(x => toDateLabel(x.day));
        const p50 = daily.map(x => x.inf_latency_p50_ms);
        const p90 = daily.map(x => x.inf_latency_p90_ms);
        const p99 = daily.map(x => x.inf_latency_p99_ms);

        new Chart(document.getElementById('latencyChart'), {
          type: 'line',
          data: {
            labels,
            datasets: [
              { label: 'p50 (ms)', data: p50, borderColor: '#22c55e', tension: 0.2 },
              { label: 'p90 (ms)', data: p90, borderColor: '#f59e0b', tension: 0.2 },
              { label: 'p99 (ms)', data: p99, borderColor: '#ef4444', tension: 0.2 }
            ]
          },
          options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });

        // Volume & agreement
        const volume = daily.map(x => x.inf_count);
        const agreeRate = daily.map(x => {
          const pos = x.feedback_pos || 0; const neg = x.feedback_neg || 0;
          const tot = pos + neg; return tot > 0 ? (pos / tot * 100).toFixed(1) : null;
        });

        new Chart(document.getElementById('volumeChart'), {
          type: 'bar',
          data: {
            labels,
            datasets: [
              { label: 'Volume', data: volume, backgroundColor: '#60a5fa' },
              { label: 'Taux accord (%)', data: agreeRate, type: 'line', yAxisID: 'y1', borderColor: '#8b5cf6' }
            ]
          },
          options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            scales: { y: { beginAtZero: true }, y1: { beginAtZero: true, position: 'right' } },
            plugins: { legend: { position: 'bottom' } }
          }
        });

        document.getElementById('summary7d').textContent = JSON.stringify(m7d, null, 2);
      }

      load().catch(e => {
        document.getElementById('summary7d').textContent = 'Erreur chargement: ' + e;
      });
    </script>
  </body>
</html>
"""
    return HTMLResponse(content=html)


@app.get("/api/metrics/daily", response_class=JSONResponse)
async def metrics_daily() -> List[Dict[str, Any]]:
    connect = get_db_connect()
    query = (
        """
        SELECT
          date_feedback AS day,
          COUNT(*) AS inf_count,
          SUM(CASE WHEN success IS TRUE THEN 1 ELSE 0 END) AS inf_success,
          SUM(CASE WHEN success IS FALSE THEN 1 ELSE 0 END) AS inf_errors,
          AVG(inference_time_ms) AS inf_latency_avg_ms,
          percentile_cont(0.5) WITHIN GROUP (ORDER BY inference_time_ms) AS inf_latency_p50_ms,
          percentile_cont(0.9) WITHIN GROUP (ORDER BY inference_time_ms) AS inf_latency_p90_ms,
          percentile_cont(0.99) WITHIN GROUP (ORDER BY inference_time_ms) AS inf_latency_p99_ms,
          SUM(CASE WHEN feedback IS TRUE THEN 1 ELSE 0 END) AS feedback_pos,
          SUM(CASE WHEN feedback IS FALSE THEN 1 ELSE 0 END) AS feedback_neg
        FROM Feedback_user
        GROUP BY day
        ORDER BY day DESC
        LIMIT 30
        """
    )
    rows: List[Dict[str, Any]] = []
    with connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            cols = [c[0] for c in cur.description]
            for r in cur.fetchall():
                item = {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in zip(cols, r)}
                if isinstance(item.get("day"), (date,)):
                    item["day"] = item["day"].isoformat()
                rows.append(item)
    return JSONResponse(content=rows)


@app.get("/api/metrics/7d", response_class=JSONResponse)
async def metrics_7d() -> Dict[str, Any]:
    connect = get_db_connect()
    query = (
        """
        SELECT
          CURRENT_DATE AS as_of,
          COUNT(*) FILTER (WHERE date_feedback >= CURRENT_DATE - INTERVAL '7 days') AS inf_7d,
          AVG(inference_time_ms) FILTER (WHERE date_feedback >= CURRENT_DATE - INTERVAL '7 days') AS latency_avg_ms_7d,
          percentile_cont(0.9) WITHIN GROUP (ORDER BY inference_time_ms)
            FILTER (WHERE date_feedback >= CURRENT_DATE - INTERVAL '7 days') AS latency_p90_ms_7d,
          SUM(CASE WHEN feedback IS TRUE THEN 1 ELSE 0 END)
            FILTER (WHERE date_feedback >= CURRENT_DATE - INTERVAL '7 days') AS fb_pos_7d,
          SUM(CASE WHEN feedback IS FALSE THEN 1 ELSE 0 END)
            FILTER (WHERE date_feedback >= CURRENT_DATE - INTERVAL '7 days') AS fb_neg_7d
        FROM Feedback_user
        """
    )
    item: Dict[str, Any] = {}
    with connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            cols = [c[0] for c in cur.description]
            r = cur.fetchone()
            if r:
                item = {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in zip(cols, r)}
                if isinstance(item.get("as_of"), (date,)):
                    item["as_of"] = item["as_of"].isoformat()
    return JSONResponse(content=item)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8050, reload=True)



from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
from pathlib import Path
import time
from enum import Enum
from pydantic import BaseModel
import importlib

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from .auth import verify_token
from src.models.predictor import CatDogPredictor
from src.monitoring.metrics import time_inference, log_inference_time, read_last_inference_metrics
from config.settings import DB_CONFIG

# Configuration des templates
TEMPLATES_DIR = ROOT_DIR / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

# Initialisation du prédicteur
predictor = CatDogPredictor()

@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    """Page d'accueil avec interface web"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.get("/info", response_class=HTMLResponse)
async def info_page(request: Request):
    """Page d'informations"""
    model_info = {
        "name": "Cats vs Dogs Classifier",
        "version": "1.0.0",
        "description": "Modèle CNN pour classification chats/chiens",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0,
        "classes": ["Cat", "Dog"],
        "input_size": f"{predictor.image_size[0]}x{predictor.image_size[1]}",
        "model_loaded": predictor.is_loaded()
    }
    return templates.TemplateResponse("info.html", {
        "request": request, 
        "model_info": model_info
    })

@router.get("/inference", response_class=HTMLResponse)
async def inference_page(request: Request):
    """Page d'inférence"""
    return templates.TemplateResponse("inference.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.post("/api/predict")
@time_inference  # Décorateur de monitoring
async def predict_api(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """API de prédiction avec monitoring"""
    if not predictor.is_loaded():
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Format d'image invalide")
    
    try:
        image_data = await file.read()
        result = predictor.predict(image_data)

        response_data = {
            "filename": file.filename,
            "prediction": result["prediction"],
            "confidence": f"{result['confidence']:.2%}",
            "probabilities": {
                "cat": f"{result['probabilities']['cat']:.2%}",
                "dog": f"{result['probabilities']['dog']:.2%}"
            }
        }

        return response_data

    except Exception as e:
        # Simple gestion d'erreur sans code unreachable
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@router.get("/api/info")
async def api_info():
    """Informations API JSON"""
    return {
        "model_loaded": predictor.is_loaded(),
        "model_path": str(predictor.model_path),
        "version": "1.0.0",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0
    }

@router.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_loaded()
    }
    
class FeedbackType(str, Enum):
    positive = "positive"
    negative = "negative"


class FeedbackRequest(BaseModel):
    feedback: FeedbackType
    resultat_prediction: float
    input_user: str


class FeedbackResponse(BaseModel):
    status: str
    feedback: FeedbackType
    resultat_prediction: float
    input_user: str
    timestamp: float
    saved_to_db: bool = False


@router.post("/api/feedback", response_model=FeedbackResponse)
async def feedback_api(payload: FeedbackRequest, token: str = Depends(verify_token)):
    """Endpoint de feedback utilisateur pour confirmer/infirmer la prédiction.

    Actuellement, l'API accuse réception et retourne l'écho des données.
    (Point d'extension: persister le feedback en base ou le logger.)
    """
    # Optionnel: récupérer la dernière métrique d'inférence
    last_metrics = read_last_inference_metrics()

    # Insérer en base (PostgreSQL)
    saved_to_db = False
    try:
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
                # Préparer métriques si présentes
                inference_time_ms = None
                success = None
                if last_metrics:
                    inference_time_ms = float(last_metrics.get("inference_time_ms")) if last_metrics.get("inference_time_ms") is not None else None
                    success = bool(last_metrics.get("success")) if last_metrics.get("success") is not None else None

                cur.execute(
                    """
                    INSERT INTO feedback_user (feedback, date_feedback, resultat_prediction, input_user, inference_time_ms, success)
                    VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                    """,
                    (
                        True if payload.feedback == FeedbackType.positive else False,
                        float(payload.resultat_prediction),
                        payload.input_user,
                        inference_time_ms,
                        success,
                    ),
                )
                conn.commit()
                saved_to_db = True
    except Exception as e:
        # Ne pas bloquer la réponse si la DB échoue; on répond quand même
        pass

    return FeedbackResponse(
        status="received",
        feedback=payload.feedback,
        resultat_prediction=payload.resultat_prediction,
        input_user=payload.input_user,
        timestamp=time.time(),
        saved_to_db=saved_to_db,
    )


@router.get("/api/metrics/daily")
async def metrics_daily():
    """Agrégats journaliers: volume, latences, feedback."""
    # Fallback import pour psycopg/psycopg2
    try:
        try:
            dbmod = importlib.import_module("psycopg")
            connect = dbmod.connect
        except Exception:
            dbmod = importlib.import_module("psycopg2")
            connect = dbmod.connect

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

        rows = []
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
                    if hasattr(item.get("day"), "isoformat"):
                        item["day"] = item["day"].isoformat()
                    rows.append(item)
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur métriques: {e}")


@router.get("/api/metrics/7d")
async def metrics_7d():
    """Résumé 7 jours glissants."""
    try:
        try:
            dbmod = importlib.import_module("psycopg")
            connect = dbmod.connect
        except Exception:
            dbmod = importlib.import_module("psycopg2")
            connect = dbmod.connect

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
                    if hasattr(item.get("as_of"), "isoformat"):
                        item["as_of"] = item["as_of"].isoformat()
                    return item
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur métriques: {e}")

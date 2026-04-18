from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
import os
import numpy as np
import traceback

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH  = os.path.join(BASE_DIR, 'models', 'saved_models', 'gradient_boosting.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'scaler.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'feature_names.pkl')

# ── Load once at import time ──────────────────────────────────────────────────
_model = None
_scaler = None
_feature_names = None
_load_error = None

try:
    _model        = joblib.load(MODEL_PATH)
    _scaler       = joblib.load(SCALER_PATH)
    _feature_names = joblib.load(FEATURES_PATH)
except Exception as e:
    _load_error = traceback.format_exc()
    print(f"[predict.py] Model load failed:\n{_load_error}")
# ─────────────────────────────────────────────────────────────────────────────


class PredictionInput(BaseModel):
    gre_score: float
    toefl_score: float
    university_rating: float
    sop: float
    lor: float
    cgpa: float
    research: int


@router.get("/health")
def predict_health():
    """Debug endpoint — shows whether models loaded successfully."""
    if _load_error:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error": _load_error,
            "paths": {
                "model":    MODEL_PATH,
                "scaler":   SCALER_PATH,
                "features": FEATURES_PATH,
                "model_exists":    os.path.exists(MODEL_PATH),
                "scaler_exists":   os.path.exists(SCALER_PATH),
                "features_exists": os.path.exists(FEATURES_PATH),
            }
        })
    return {
        "status": "ok",
        "model_type": type(_model).__name__,
        "features": _feature_names,
    }


@router.post("/")
async def predict_chance(data: PredictionInput):
    if _load_error:
        raise HTTPException(
            status_code=503,
            detail=f"Models failed to load at startup: {_load_error[:300]}"
        )
    if _model is None or _scaler is None:
        raise HTTPException(status_code=503, detail="Models not available.")

    try:
        input_values = [
            data.gre_score,
            data.toefl_score,
            data.university_rating,
            data.sop,
            data.lor,
            data.cgpa,
            float(data.research),
        ]
        input_data = np.array([input_values], dtype=np.float64)
        scaled_data = _scaler.transform(input_data)
        prediction = float(_model.predict(scaled_data)[0])

        # Feature importance as proxy for SHAP — always works with GBR
        contributions = []
        try:
            importances = _model.feature_importances_
            direction = prediction - 0.5
            for i, feature in enumerate(_feature_names):
                contributions.append({
                    "feature": feature,
                    "contribution": float(importances[i] * direction),
                    "actual_value": float(input_values[i])
                })
        except Exception:
            for i, feature in enumerate(_feature_names):
                contributions.append({
                    "feature": feature,
                    "contribution": 0.0,
                    "actual_value": float(input_values[i])
                })

        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        chance = prediction * 100
        category = "Safe" if chance >= 85 else "Moderate" if chance >= 65 else "Reach"

        return {
            "chance_of_admit": min(max(prediction, 0.0), 1.0),
            "percentage":      min(max(chance,      0.0), 100.0),
            "category":        category,
            "base_value":      0.5,
            "shap_contributions": contributions,
        }

    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())

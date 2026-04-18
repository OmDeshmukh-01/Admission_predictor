from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
import os
import sys
import numpy as np
import traceback

router = APIRouter()

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH    = os.path.join(BASE_DIR, 'models', 'saved_models', 'gradient_boosting.pkl')
SCALER_PATH   = os.path.join(BASE_DIR, 'models', 'saved_models', 'scaler.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'feature_names.pkl')
TRAIN_SCRIPT  = os.path.join(BASE_DIR, 'models', 'train_all.py')


def _retrain():
    """Run train_all.py inline to regenerate all .pkl files."""
    print("[predict.py] Retraining models with current sklearn version...")
    train_globals = {"__file__": TRAIN_SCRIPT, "__name__": "__main__"}
    with open(TRAIN_SCRIPT) as f:
        exec(compile(f.read(), TRAIN_SCRIPT, 'exec'), train_globals)
    print("[predict.py] Retraining complete.")


def _load_models():
    """Load models; retrain automatically if pkl is incompatible."""
    global _model, _scaler, _feature_names, _load_error

    # ── First attempt ────────────────────────────────────────────────────────
    try:
        m  = joblib.load(MODEL_PATH)
        sc = joblib.load(SCALER_PATH)
        fn = joblib.load(FEATURES_PATH)
        # Smoke-test: make sure predict() actually works
        m.predict(sc.transform([[310, 105, 3, 3.5, 3.5, 8.5, 0]]))
        _model, _scaler, _feature_names, _load_error = m, sc, fn, None
        print("[predict.py] Models loaded OK.")
        return
    except Exception as first_err:
        print(f"[predict.py] Initial load failed ({first_err}). Retraining...")

    # ── Retrain then try again ────────────────────────────────────────────────
    try:
        _retrain()
        m  = joblib.load(MODEL_PATH)
        sc = joblib.load(SCALER_PATH)
        fn = joblib.load(FEATURES_PATH)
        m.predict(sc.transform([[310, 105, 3, 3.5, 3.5, 8.5, 0]]))
        _model, _scaler, _feature_names, _load_error = m, sc, fn, None
        print("[predict.py] Models loaded OK after retraining.")
    except Exception as retry_err:
        _load_error = traceback.format_exc()
        print(f"[predict.py] Retrain also failed:\n{_load_error}")


# ── Module-level state ────────────────────────────────────────────────────────
_model         = None
_scaler        = None
_feature_names = None
_load_error    = None

_load_models()   # runs once when the module is imported
# ─────────────────────────────────────────────────────────────────────────────


class PredictionInput(BaseModel):
    gre_score:         float
    toefl_score:       float
    university_rating: float
    sop:               float
    lor:               float
    cgpa:              float
    research:          int


@router.get("/health")
def predict_health():
    """Debug: shows model load status."""
    if _load_error:
        return JSONResponse(status_code=500, content={"status": "error", "error": _load_error})
    return {"status": "ok", "model": type(_model).__name__, "features": _feature_names}


@router.post("/")
async def predict_chance(data: PredictionInput):
    if _load_error or _model is None:
        raise HTTPException(status_code=503, detail=f"Models unavailable: {str(_load_error)[:400]}")

    try:
        input_values = [
            data.gre_score, data.toefl_score, data.university_rating,
            data.sop, data.lor, data.cgpa, float(data.research),
        ]
        input_data  = np.array([input_values], dtype=np.float64)
        scaled_data = _scaler.transform(input_data)
        prediction  = float(_model.predict(scaled_data)[0])

        # Feature importance as proxy for SHAP (no extra dependencies)
        contributions = []
        try:
            importances = _model.feature_importances_
            direction   = prediction - 0.5
            for i, feat in enumerate(_feature_names):
                contributions.append({
                    "feature":      feat,
                    "contribution": float(importances[i] * direction),
                    "actual_value": float(input_values[i]),
                })
        except Exception:
            for i, feat in enumerate(_feature_names):
                contributions.append({"feature": feat, "contribution": 0.0,
                                      "actual_value": float(input_values[i])})

        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        chance   = prediction * 100
        category = "Safe" if chance >= 85 else "Moderate" if chance >= 65 else "Reach"

        return {
            "chance_of_admit":   min(max(prediction, 0.0), 1.0),
            "percentage":        min(max(chance,     0.0), 100.0),
            "category":          category,
            "base_value":        0.5,
            "shap_contributions": contributions,
        }

    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())

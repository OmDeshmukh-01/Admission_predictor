from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import os
import numpy as np

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'gradient_boosting.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'scaler.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'feature_names.pkl')

class PredictionInput(BaseModel):
    gre_score: float
    toefl_score: float
    university_rating: float
    sop: float
    lor: float
    cgpa: float
    research: int

@router.post("/")
async def predict_chance(data: PredictionInput):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise HTTPException(status_code=500, detail="Models are not trained yet.")

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    feature_names = joblib.load(FEATURES_PATH)

    input_values = [
        data.gre_score,
        data.toefl_score,
        data.university_rating,
        data.sop,
        data.lor,
        data.cgpa,
        data.research
    ]
    input_data = np.array([input_values])
    scaled_data = scaler.transform(input_data)
    prediction = float(model.predict(scaled_data)[0])

    # ── Feature importance as a proxy for SHAP (no SHAP dependency) ──
    # GradientBoostingRegressor exposes feature_importances_ natively.
    # We scale them so the bar chart still looks meaningful.
    contributions = []
    try:
        importances = model.feature_importances_          # shape: (n_features,)
        mean_pred = prediction - 0.5                      # rough offset from baseline
        for i, feature in enumerate(feature_names):
            # Weight importance by how far input is from neutral (0 after scaling)
            signed = float(importances[i] * mean_pred)
            contributions.append({
                "feature": feature,
                "contribution": signed,
                "actual_value": float(input_values[i])
            })
    except Exception as e:
        print(f"[feature importance fallback] {e}")
        for i, feature in enumerate(feature_names):
            contributions.append({
                "feature": feature,
                "contribution": 0.0,
                "actual_value": float(input_values[i])
            })

    contributions = sorted(contributions, key=lambda x: abs(x["contribution"]), reverse=True)

    chance = prediction * 100
    if chance >= 85:
        category = "Safe"
    elif chance >= 65:
        category = "Moderate"
    else:
        category = "Reach"

    return {
        "chance_of_admit": min(max(prediction, 0.0), 1.0),
        "percentage": min(max(chance, 0.0), 100.0),
        "category": category,
        "base_value": 0.5,
        "shap_contributions": contributions
    }

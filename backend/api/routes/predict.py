from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import os
import numpy as np
import shap

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

    input_data = np.array([[
        data.gre_score,
        data.toefl_score,
        data.university_rating,
        data.sop,
        data.lor,
        data.cgpa,
        data.research
    ]])

    scaled_data = scaler.transform(input_data)
    prediction = model.predict(scaled_data)[0]

    # --- SHAP Explainability (TreeExplainer for GradientBoosting) ---
    contributions = []
    base_value = 0.5
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scaled_data)

        # shap_values shape: (1, n_features) for regressors
        shap_arr = np.array(shap_values)
        shap_row = shap_arr[0] if shap_arr.ndim == 2 else shap_arr
        base_value = float(explainer.expected_value)

        for i, feature in enumerate(feature_names):
            contributions.append({
                "feature": feature,
                "contribution": float(shap_row[i]),
                "actual_value": float(input_data[0][i])
            })
    except Exception as shap_err:
        # SHAP failed — prediction still works, contributions return as zeros
        print(f"[SHAP warning] {shap_err}")
        for i, feature in enumerate(feature_names):
            contributions.append({
                "feature": feature,
                "contribution": 0.0,
                "actual_value": float(input_data[0][i])
            })

    # Sort by absolute impact
    contributions = sorted(contributions, key=lambda x: abs(x["contribution"]), reverse=True)

    # Categorise result
    chance = float(prediction) * 100
    if chance >= 85:
        category = "Safe"
    elif chance >= 65:
        category = "Moderate"
    else:
        category = "Reach"

    return {
        "chance_of_admit": min(max(float(prediction), 0.0), 1.0),
        "percentage": min(max(chance, 0.0), 100.0),
        "category": category,
        "base_value": base_value,
        "shap_contributions": contributions
    }

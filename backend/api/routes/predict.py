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
    
    # Generate SHAP values for explainability
    explainer = shap.Explainer(model)
    shap_values = explainer(scaled_data)
    
    # Extract feature contributions
    contributions = []
    base_value = float(shap_values.base_values[0]) if hasattr(shap_values, 'base_values') else 0.5
    
    for i, feature in enumerate(feature_names):
        try:
            val = float(shap_values.values[0][i])
        except:
            val = float(shap_values.values[i]) if len(np.shape(shap_values.values)) == 1 else 0
        contributions.append({
            "feature": feature,
            "contribution": val,
            "actual_value": float(input_data[0][i])
        })
        
    # Sort contributions by absolute impact
    contributions = sorted(contributions, key=lambda x: abs(x["contribution"]), reverse=True)
    
    # Categorize
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

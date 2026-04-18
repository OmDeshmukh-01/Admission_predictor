from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_PATH = os.path.join(BASE_DIR, 'models', 'saved_models', 'metrics.json')

@router.get("/metrics")
def get_model_metrics():
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="Metrics not found. Please train models first.")
        
    with open(METRICS_PATH, 'r') as f:
        metrics = json.load(f)
        
    # Format for charting
    formatted_metrics = []
    for model_name, scores in metrics.items():
        formatted_metrics.append({
            "model": model_name,
            **scores
        })
        
    return {
        "raw_metrics": metrics,
        "chart_data": formatted_metrics
    }

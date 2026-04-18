from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import predict, analytics, models

app = FastAPI(
    title="AdmitScope API",
    description="Backend API for AdmitScope Graduate Admission Predictor",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(predict.router, prefix="/api/predict", tags=["prediction"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(models.router, prefix="/api/models", tags=["models"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AdmitScope API"}

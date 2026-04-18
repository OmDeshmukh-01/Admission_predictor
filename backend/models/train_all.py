import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'US_graduate_schools_admission_parameters_dataset.csv')
SAVE_DIR = os.path.join(BASE_DIR, 'models', 'saved_models')

# Create save dir if not exists
os.makedirs(SAVE_DIR, exist_ok=True)

def load_data():
    df = pd.read_csv(DATA_PATH)
    # Strip spaces from column names
    df.columns = [col.strip() for col in df.columns]
    
    # Drop Serial No.
    if 'Serial No.' in df.columns:
        df = df.drop('Serial No.', axis=1)
        
    X = df.drop('Chance of Admit', axis=1)
    y = df['Chance of Admit']
    
    return X, y

def build_ann_model(input_dim):
    model = Sequential([
        Dense(64, activation='relu', input_dim=input_dim),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.1),
        Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_and_evaluate():
    print("Loading data...")
    X, y = load_data()
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler and feature names
    joblib.dump(scaler, os.path.join(SAVE_DIR, 'scaler.pkl'))
    joblib.dump(list(X.columns), os.path.join(SAVE_DIR, 'feature_names.pkl'))
    
    # Initialize Models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }
    
    results = {}
    
    # Train scikit-learn models
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = model.predict(X_test_scaled)
        
        # Evaluate
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        results[name] = {
            'R2 Score': float(r2),
            'MAE': float(mae),
            'RMSE': float(rmse)
        }
        
        # Save model
        joblib.dump(model, os.path.join(SAVE_DIR, f"{name.replace(' ', '_').lower()}.pkl"))

    # Train ANN
    print("Training ANN...")
    ann_model = build_ann_model(X_train_scaled.shape[1])
    ann_model.fit(X_train_scaled, y_train, epochs=50, batch_size=16, verbose=0)
    
    # Predict and evaluate ANN
    ann_pred = ann_model.predict(X_test_scaled).flatten()
    r2_ann = r2_score(y_test, ann_pred)
    mae_ann = mean_absolute_error(y_test, ann_pred)
    rmse_ann = np.sqrt(mean_squared_error(y_test, ann_pred))
    
    results['ANN'] = {
        'R2 Score': float(r2_ann),
        'MAE': float(mae_ann),
        'RMSE': float(rmse_ann)
    }
    
    # Save ANN
    ann_model.save(os.path.join(SAVE_DIR, 'ann.h5'))
    
    # Save results to JSON
    with open(os.path.join(SAVE_DIR, 'metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Training complete! Metrics saved to models/saved_models/metrics.json")
    print(json.dumps(results, indent=4))

if __name__ == '__main__':
    train_and_evaluate()

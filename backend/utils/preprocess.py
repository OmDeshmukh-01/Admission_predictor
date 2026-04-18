import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import os


class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = None
        self.X_scaled = None
        self.y = None
    
    def load_data(self, filepath):
        try:
            df = pd.read_csv(filepath)
            print(f"Dataset loaded successfully. Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            return df
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return None
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None
    
    def prepare_data(self, df, target_column='Chance of Admit '):
        df = df.dropna()
        
        if 'Serial No.' in df.columns:
            df = df.drop(columns=['Serial No.'])
        
        X = df.drop(columns=[target_column])
        y = df[target_column].values
        
        self.feature_names = X.columns.tolist()
        
        print(f"Features extracted: {self.feature_names}")
        print(f"  Feature matrix shape: {X.shape}")
        print(f"  Target shape: {y.shape}")
        
        return X, y
    
    def fit_and_scale(self, X):
        X_scaled = self.scaler.fit_transform(X)
        print(f"StandardScaler fitted and applied")
        print(f"  Scaling ranges:")
        for i, feature in enumerate(self.feature_names):
            print(f"    {feature}: [{X_scaled[:, i].min():.4f}, {X_scaled[:, i].max():.4f}]")
        
        return X_scaled
    
    def scale(self, X):
        if self.scaler is None:
            raise ValueError("Scaler not fitted. Call fit_and_scale() first.")
        return self.scaler.transform(X)
    
    def save_scaler(self, filepath):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump(self.scaler, f)
            print(f"Scaler saved to {filepath}")
        except Exception as e:
            print(f"Error saving scaler: {str(e)}")
    
    @staticmethod
    def load_scaler(filepath):
        try:
            with open(filepath, 'rb') as f:
                scaler = pickle.load(f)
            print(f"Scaler loaded from {filepath}")
            return scaler
        except FileNotFoundError:
            print(f"Error: Scaler file not found at {filepath}")
            return None
        except Exception as e:
            print(f"Error loading scaler: {str(e)}")
            return None
    
    def get_feature_statistics(self, X):
        print("\nFeature Statistics:")
        print(X.describe())
        print(f"\nMissing values:\n{X.isnull().sum()}")


def download_sample_dataset():
    np.random.seed(42)
    
    sample_data = {
        'GRE Score': np.random.randint(290, 340, 100),
        'TOEFL Score': np.random.randint(90, 120, 100),
        'University Rating': np.random.randint(1, 5, 100),
        'SOP': np.random.uniform(1, 5, 100),
        'LOR ': np.random.uniform(1, 5, 100),
        'CGPA': np.random.uniform(6.0, 10.0, 100),
        'Research': np.random.randint(0, 2, 100),
        'Chance of Admit ': np.random.uniform(0.4, 0.97, 100)
    }
    
    df = pd.DataFrame(sample_data)
    print("Sample dataset created")
    return df




from fastapi import APIRouter
import pandas as pd
import os
import json

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'US_graduate_schools_admission_parameters_dataset.csv')

def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = [col.strip() for col in df.columns]
    return df

@router.get("/kpis")
def get_kpis():
    df = load_data()
    return {
        "total_students": len(df),
        "avg_gre": round(df['GRE Score'].mean(), 1),
        "avg_toefl": round(df['TOEFL Score'].mean(), 1),
        "avg_cgpa": round(df['CGPA'].mean(), 2),
        "avg_admit_chance": round(df['Chance of Admit'].mean() * 100, 1),
        "research_percentage": round((df['Research'].sum() / len(df)) * 100, 1)
    }

@router.get("/distributions")
def get_distributions():
    df = load_data()
    
    # Gre ranges
    gre_bins = [290, 300, 310, 320, 330, 340]
    gre_labels = ['290-300', '300-310', '310-320', '320-330', '330-340']
    df['gre_range'] = pd.cut(df['GRE Score'], bins=gre_bins, labels=gre_labels, right=True)
    
    gre_dist = df['gre_range'].value_counts().sort_index().to_dict()
    gre_data = [{"range": str(k), "count": int(v)} for k, v in gre_dist.items()]
    
    # Admit categories
    def categorize(x):
        if x >= 0.85: return 'High'
        elif x >= 0.65: return 'Medium'
        else: return 'Low'
        
    df['Admit_Category'] = df['Chance of Admit'].apply(categorize)
    admit_dist = df['Admit_Category'].value_counts().to_dict()
    admit_data = [{"category": str(k), "count": int(v)} for k, v in admit_dist.items()]
    
    return {
        "gre_distribution": gre_data,
        "admit_distribution": admit_data
    }

@router.get("/scatter")
def get_scatter():
    df = load_data()
    # Provide a downsampled version for the frontend if too large, but 400 points is fine.
    scatter_data = df[['GRE Score', 'CGPA', 'Chance of Admit']].copy()
    scatter_data['Chance of Admit'] = scatter_data['Chance of Admit'] * 100
    
    return scatter_data.to_dict(orient='records')

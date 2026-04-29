import os
import yaml
import pandas as pd
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

TEMP_MIN_THRESHOLD = CONFIG['thresholds']['temp_min_f']
TEMP_MAX_THRESHOLD = CONFIG['thresholds']['temp_max_f']
ENERGY_MIN_THRESHOLD = CONFIG['thresholds']['energy_min']

def generate_quality_report(df):
    """
    Generate data quality metrics from the dataframe.
    """
    report = {}
    
    if df.empty:
        report['status'] = "Error: Dataset is empty"
        return report
        
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. Missing Values
    missing_counts = df.isnull().sum().to_dict()
    report['missing_values'] = missing_counts
    
    # 2. Outliers
    temp_min_outliers = df[(df['temp_min'] < TEMP_MIN_THRESHOLD) | (df['temp_min'] > TEMP_MAX_THRESHOLD)]
    temp_max_outliers = df[(df['temp_max'] < TEMP_MIN_THRESHOLD) | (df['temp_max'] > TEMP_MAX_THRESHOLD)]
    energy_outliers = df[df['energy_demand'] < ENERGY_MIN_THRESHOLD]
    
    report['outliers'] = {
        'temp_min_outliers_count': len(temp_min_outliers),
        'temp_max_outliers_count': len(temp_max_outliers),
        'energy_outliers_count': len(energy_outliers)
    }
    
    # 3. Data Freshness
    latest_date = df['date'].max()
    now_date = datetime.now()
    days_diff = (now_date - latest_date).days
    
    report['data_freshness'] = {
        'latest_date': latest_date.strftime('%Y-%m-%d'),
        'days_since_last_update': days_diff,
        'is_fresh': days_diff <= 2
    }
    
    return report

def get_outlier_details(df):
    """Return actual records that are outliers for detailed viewing."""
    outliers_mask = (
        (df['temp_min'] < TEMP_MIN_THRESHOLD) | 
        (df['temp_min'] > TEMP_MAX_THRESHOLD) |
        (df['temp_max'] < TEMP_MIN_THRESHOLD) | 
        (df['temp_max'] > TEMP_MAX_THRESHOLD) |
        (df['energy_demand'] < ENERGY_MIN_THRESHOLD)
    )
    return df[outliers_mask]

import os
import yaml
import logging
import requests
import pandas as pd
from dotenv import load_dotenv

# Load env variables
load_dotenv()
NOAA_TOKEN = os.getenv("NOAA_TOKEN")
EIA_KEY = os.getenv("EIA_KEY")

# Load YAML configs
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

NOAA_BASE_URL = CONFIG['api']['noaa_base_url']
EIA_BASE_URL = CONFIG['api']['eia_base_url']

def fetch_weather_data(station_id, start_date, end_date):
    """Fetch TMAX and TMIN from NOAA."""
    headers = {'token': NOAA_TOKEN}
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'datatypeid': 'TMAX,TMIN',
        'limit': 1000
    }
    
    try:
        response = requests.get(NOAA_BASE_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'results' not in data:
            logging.warning(f"No weather data found for station {station_id} between {start_date} and {end_date}.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data['results'])
        df_pivot = df.pivot(index='date', columns='datatype', values='value').reset_index()
        df_pivot['date'] = pd.to_datetime(df_pivot['date']).dt.strftime('%Y-%m-%d')
        
        # Values are in tenths of a degree Celsius
        for col in ['TMAX', 'TMIN']:
            if col in df_pivot.columns:
                df_pivot[col] = (df_pivot[col] / 10.0) * 1.8 + 32.0
            else:
                df_pivot[col] = pd.NA
                
        df_pivot.rename(columns={'TMAX': 'temp_max', 'TMIN': 'temp_min'}, inplace=True)
        return df_pivot[['date', 'temp_max', 'temp_min']]
        
    except Exception as e:
        logging.error(f"Error fetching weather data for {station_id}: {e}")
        return pd.DataFrame()

def fetch_energy_data(region_code, start_date, end_date):
    """Fetch daily electricity demand from EIA."""
    params = {
        'api_key': EIA_KEY,
        'frequency': 'daily',
        'data[0]': 'value',
        'facets[respondent][]': region_code,
        'start': start_date,
        'end': end_date,
    }
    
    try:
        response = requests.get(EIA_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'response' not in data or 'data' not in data['response']:
            logging.warning(f"No energy data found for region {region_code} between {start_date} and {end_date}.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data['response']['data'])
        if df.empty:
            logging.warning(f"Empty energy data returned for region {region_code}.")
            return pd.DataFrame()
            
        df_clean = df[['period', 'value']].rename(columns={'period': 'date', 'value': 'energy_demand'})
        df_clean['date'] = pd.to_datetime(df_clean['date']).dt.strftime('%Y-%m-%d')
        df_clean['energy_demand'] = pd.to_numeric(df_clean['energy_demand'], errors='coerce')
        df_clean = df_clean.groupby('date')['energy_demand'].sum().reset_index()
        
        return df_clean
        
    except Exception as e:
        logging.error(f"Error fetching energy data for {region_code}: {e}")
        return pd.DataFrame()

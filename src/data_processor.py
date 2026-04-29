import os
import pandas as pd
import logging
from src.data_fetcher import CONFIG

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed", "processed_data.csv")
os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)

def merge_and_save(city, weather_df, energy_df):
    """Clean, merge, and save data for a specific city."""
    metadata = CONFIG['cities'][city]
    
    if weather_df.empty and energy_df.empty:
        logging.warning(f"Both weather and energy data missing for {city}.")
        return None
        
    if not weather_df.empty and not energy_df.empty:
        city_df = pd.merge(weather_df, energy_df, on='date', how='outer')
    elif not weather_df.empty:
        city_df = weather_df.copy()
        city_df['energy_demand'] = pd.NA
    else:
        city_df = energy_df.copy()
        city_df['temp_max'] = pd.NA
        city_df['temp_min'] = pd.NA
        
    city_df['city'] = city
    city_df['state'] = metadata['state']
    city_df['lat'] = metadata['lat']
    city_df['lon'] = metadata['lon']
    
    return city_df

def append_to_processed_data(new_data_df):
    """Appends to the processed csv without duplicating dates/cities."""
    if new_data_df.empty:
        return
        
    if os.path.exists(PROCESSED_FILE):
        existing_data = pd.read_csv(PROCESSED_FILE)
        combined_data = pd.concat([existing_data, new_data_df]).drop_duplicates(subset=['date', 'city'], keep='last')
        combined_data.to_csv(PROCESSED_FILE, index=False)
        logging.info(f"Appended {len(new_data_df)} rows. Total rows now: {len(combined_data)}")
    else:
        new_data_df.to_csv(PROCESSED_FILE, index=False)
        logging.info(f"Created new processed file with {len(new_data_df)} rows.")

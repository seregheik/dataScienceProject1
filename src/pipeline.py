import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime, timedelta

# Append src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_fetcher import fetch_weather_data, fetch_energy_data, CONFIG
from src.data_processor import merge_and_save, append_to_processed_data

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_pipeline(days_back=1):
    logging.info(f"Starting data pipeline execution. Fetching {days_back} days of data.")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    str_end = end_date.strftime('%Y-%m-%d')
    str_start = start_date.strftime('%Y-%m-%d')
    
    all_data = []
    
    for city, metadata in CONFIG['cities'].items():
        logging.info(f"Processing data for {city}...")
        
        weather_df = fetch_weather_data(metadata['noaa_station'], str_start, str_end)
        energy_df = fetch_energy_data(metadata['eia_region'], str_start, str_end)
        
        city_df = merge_and_save(city, weather_df, energy_df)
        if city_df is not None:
            all_data.append(city_df)
    
    if not all_data:
        logging.error("No data fetched for any city. Exiting.")
        return
        
    # We must explicitly cast to list and handle pd.concat
    new_data = pd.concat(all_data, ignore_index=True)
    append_to_processed_data(new_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the automated data pipeline.")
    parser.add_argument('--historical', action='store_true', help="Fetch 90 days of historical data")
    args = parser.parse_args()
    
    days = 90 if args.historical else 2
    run_pipeline(days_back=days)

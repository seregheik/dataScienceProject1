# Energy Demand & Weather Forecasting Project

This project combines NOAA weather data with EIA electricity demand data to build predictive data pipelines and visualization tools. It allows utility companies to identify correlations between temperature variations and electrical load, helping to optimize power generation and mitigate losses.

## Overview
- **Data Pipeline (`src/pipeline.py`)**: Connects to the NOAA CDO and EIA Energy APIs to retrieve specified date ranges for daily energy consumption and daily temperature extremes.
- **Data Quality Module (`src/data_quality.py`)**: Evaluates missing data, numerical outliers (against sane physical thresholds), and flags staleness.
- **Interactive Dashboard (`app.py`)**: A Streamlit interface that combines geographic, time-series, correlation, and heatmap visualisations of demand data.

## Prerequisites
- **Python 3.8+**
- **Valid API Tokens** for both NOAA and EIA.

### API Registration
1. **NOAA Climate Data Online:** Register at [https://www.ncdc.noaa.gov/cdo-web/token](https://www.ncdc.noaa.gov/cdo-web/token)
2. **EIA Energy API:** Register at [https://www.eia.gov/opendata/register.php](https://www.eia.gov/opendata/register.php)

Provide these in a `.env` file in the root of the repository:
```env
NOAA_TOKEN=your_noaa_token
EIA_KEY=your_eia_key
```

## Installation

```bash
# Clone the repository
# cd dataScienceProject1

# Install required dependencies
pip install -r requirements.txt
```

## Usage

### 1. Initializing Financial Data (Pipeline)
The first run should fetch historical data up to 90 days. The pipeline is robust, logging errors sequentially.

```bash
python src/pipeline.py --historical
```

*Output data will be managed dynamically within the `data/processed/processed_data.csv` directory.*

### 2. Running Daily Ingestion
To run the standard daily ingestion, invoke the script without flags. To automate this daily via `cron`, open your crontab (`crontab -e`) and add an entry:
```bash
# Run every day at 6:00 AM
0 6 * * * cd /path/to/project && /path/to/python src/pipeline.py
```

### 3. Running the Streamlit Dashboard
With data loaded locally via the pipeline, launch the Streamlit server:

```bash
streamlit run app.py
```
This deploys the dashboard (by default on `localhost:8501`), making available real-time analysis and the configurable visual reports.

## Expected Findings
- Strong correlation (r > 0.7) between temperature extremes and energy usage.
- Distinct seasonal and regional consumption differences.

## File Structure Breakdown
- `src/config.py`: Adjust mappings for cities, acceptable constraints, and URLs.
- `src/pipeline.py`: Main process for extraction and transformation.
- `src/data_quality.py`: Module returning comprehensive checks on the pipeline data.
- `app.py`: Streamlit User Interface.
- `pipeline.log`: Verbose activity and stack traces (generated upon first run).

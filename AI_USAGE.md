# AI Tools Used

Gemini 3 Pro
Claude Sonnet 4.5
Googles Antigravity

# Prompts used

1. I want the structure of the codebase to be similar to:
    project1-energy-analysis/
    ├── README.md                 # Business-focused project summary
    ├── AI_USAGE.md              # AI assistance documentation
    ├── pyproject.toml           # Dependencies (using uv)
    ├── config/
    │   └── config.yaml          # API keys, cities list
    ├── src/
    │   ├── data_fetcher.py      # API interaction module
    │   ├── data_processor.py    # Cleaning and transformation
    │   ├── analysis.py          # Statistical analysis
    │   └── pipeline.py          # Main orchestration
    ├── dashboards/
    │   └── app.py               # Streamlit application
    ├── logs/
    │   └── pipeline.log         # Execution logs
    ├── data/
    │   ├── raw/                 # Original API responses
    │   └── processed/           # Clean, analysis-ready data
    ├── notebooks/
    │   └── exploration.ipynb    # Initial analysis (optional)
    ├── tests/
    │   └── test_pipeline.py     # Basic unit tests
    └── video_link.md            # Link to your presentation

2. For second prompt i fed it the document containing the   requirement for this project directly.
3. update the pyproject.toml file to use python verson >= 3.10.
4. For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.
5. in the geographic overview, the current name of the cities should be displayed on top of the map region

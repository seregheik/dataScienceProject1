import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress
from plotly.subplots import make_subplots

# Adjust sys.path to find src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import PROCESSED_FILE
from src.analysis import generate_quality_report, get_outlier_details

st.set_page_config(page_title="Energy Demand & Weather Forecasting", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists(PROCESSED_FILE):
        return pd.DataFrame()
    df = pd.read_csv(PROCESSED_FILE)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

st.title("Energy Demand & Weather Forecasting Dashboard")

if df.empty:
    st.error("No data found! Please ensure you have run the data pipeline (`python src/pipeline.py --historical`).")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
min_date = df['date'].min()
max_date = df['date'].max()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) != 2:
    st.stop()
    
start_date, end_date = date_range
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

cities = df['city'].unique().tolist()
selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities)

# Filter Data
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
if selected_cities:
    filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- Tabs ---
tab1, tab2 = st.tabs(["Analysis Dashboard", "Data Quality Report"])

with tab1:
    st.header("1. Geographic Overview")
    st.caption(f"Data last updated: {max_date.strftime('%Y-%m-%d')}")
    
    latest_per_city_idx = filtered_df.groupby('city')['date'].idxmax()
    map_df = filtered_df.loc[latest_per_city_idx].copy()
    
    def get_pct_change(row):
        yesterday = row['date'] - pd.Timedelta(days=1)
        city = row['city']
        past_record = df[(df['city'] == city) & (df['date'] == yesterday)]
        if not past_record.empty and past_record.iloc[0]['energy_demand'] > 0:
            return ((row['energy_demand'] - past_record.iloc[0]['energy_demand']) / past_record.iloc[0]['energy_demand']) * 100
        return 0.0

    map_df['pct_change'] = map_df.apply(get_pct_change, axis=1)
    
    overall_mean = df['energy_demand'].mean()
    map_df['color'] = map_df['energy_demand'].apply(lambda x: '#ff0000' if x > overall_mean else '#00ff00')
    map_df['size'] = 15 
    map_df['hover_text'] = map_df.apply(
        lambda r: f"{r['city']}<br>Temp: {r['temp_max']:.1f}°F<br>Demand: {r['energy_demand']:.0f} MWh<br>Change: {r['pct_change']:.1f}%", 
        axis=1
    )

    fig_map = go.Figure(data=go.Scattergeo(
        lon = map_df['lon'],
        lat = map_df['lat'],
        text = map_df['hover_text'],
        mode = 'markers+text',
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=map_df['size'],
            color=map_df['color'],
            opacity=0.8,
            line=dict(width=1, color='black')
        )
    ))

    fig_map.update_layout(
        geo_scope='usa',
        title="Current Energy Demand Overview",
        margin=dict(l=0, r=0, t=30, b=0),
        height=400
    )
    st.plotly_chart(fig_map, use_container_width=True)

    
    st.header("2. Time Series Analysis")
    city_filter_ts = st.selectbox("Select City for Time Series", ["All Cities"] + cities)
    
    ts_df = filtered_df.copy()
    if city_filter_ts != "All Cities":
        ts_df = ts_df[ts_df['city'] == city_filter_ts]
        
    ts_agg = ts_df.groupby('date').agg({'temp_max': 'mean', 'energy_demand': 'sum'}).reset_index()

    fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
    fig_ts.add_trace(
        go.Scatter(x=ts_agg['date'], y=ts_agg['temp_max'], name="Temperature (°F)", line=dict(color='orange', dash='solid')),
        secondary_y=False,
    )
    fig_ts.add_trace(
        go.Scatter(x=ts_agg['date'], y=ts_agg['energy_demand'], name="Energy Demand", line=dict(color='blue', dash='dash')),
        secondary_y=True,
    )
    
    import datetime
    start_dt = ts_agg['date'].min()
    end_dt = ts_agg['date'].max()
    d = start_dt
    shapes = []
    while pd.notnull(d) and d <= end_dt:
        if d.weekday() >= 5: 
            shapes.append(
                dict(type="rect", xref="x", yref="paper",
                     x0=d - pd.Timedelta(hours=12), x1=d + pd.Timedelta(hours=12),
                     y0=0, y1=1,
                     fillcolor="LightSalmon", opacity=0.3, layer="below", line_width=0)
            )
        d += pd.Timedelta(days=1)
        
    fig_ts.update_layout(
        title="Temperature vs Energy Over Time",
        xaxis_title="Date",
        shapes=shapes,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_ts.update_yaxes(title_text="Temperature (°F)", secondary_y=False)
    fig_ts.update_yaxes(title_text="Energy (MWh)", secondary_y=True)
    st.plotly_chart(fig_ts, use_container_width=True)

    st.header("3. Correlation Analysis")
    
    plot_df = filtered_df.dropna(subset=['temp_max', 'energy_demand'])
    if not plot_df.empty:
        slope, intercept, r_value, p_value, std_err = linregress(plot_df['temp_max'], plot_df['energy_demand'])
        r_squared = r_value ** 2
        line_eq = f"y = {slope:.2f}x + {intercept:.2f}"
        
        fig_scatter = px.scatter(
            plot_df, x='temp_max', y='energy_demand', color='city',
            hover_data=['date'],
            title=f"Correlation (R²: {r_squared:.4f}, r: {r_value:.4f})  |  {line_eq}",
            labels={'temp_max': 'Max Temperature (°F)', 'energy_demand': 'Energy Demand'}
        )
        
        fig_scatter.add_traces(go.Scatter(
            x=plot_df['temp_max'], 
            y=intercept + slope * plot_df['temp_max'], 
            mode='lines', name='Regression Line', 
            line=dict(color='black', dash='dash')
        ))
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Not enough data points for correlation analysis.")


    st.header("4. Usage Patterns Heatmap")
    
    hm_df = filtered_df.dropna(subset=['temp_max', 'energy_demand']).copy()
    
    def get_temp_range(t):
        if t < 50: return '<50°F'
        elif t < 60: return '50-60°F'
        elif t < 70: return '60-70°F'
        elif t < 80: return '70-80°F'
        elif t < 90: return '80-90°F'
        else: return '>90°F'
        
    if not hm_df.empty:    
        hm_df['Temp Range'] = hm_df['temp_max'].apply(get_temp_range)
        hm_df['Day of Week'] = hm_df['date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        temp_order = ['<50°F', '50-60°F', '60-70°F', '70-80°F', '80-90°F', '>90°F']
        
        hm_grouped = hm_df.groupby(['Temp Range', 'Day of Week'])['energy_demand'].mean().unstack()[day_order]
        hm_grouped = hm_grouped.reindex(temp_order)
        
        fig_heatmap = px.imshow(
            hm_grouped,
            labels=dict(x="Day of Week", y="Temperature Range", color="Avg Energy"),
            x=hm_grouped.columns,
            y=hm_grouped.index,
            color_continuous_scale="RdBu_r",
            aspect="auto",
            text_auto=".0f" 
        )
        
        fig_heatmap.update_layout(title="Average Energy Usage by Temperature and Day of Week")
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab2:
    st.header("Data Quality Report")
    
    report = generate_quality_report(df)
    
    if 'status' in report:
        st.error(report['status'])
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest Data Update", report['data_freshness']['latest_date'])
        with col2:
            is_fresh = "Yes" if report['data_freshness']['is_fresh'] else "No"
            st.metric("Fresh Data (< 48h)", is_fresh, 
                      delta=f"{report['data_freshness']['days_since_last_update']} days ago", delta_color="inverse")
        with col3:
            total_outliers = sum(report['outliers'].values())
            st.metric("Total Outliers Detected", total_outliers)
            
        st.subheader("Missing Values")
        st.json(report['missing_values'])
        st.info("Missing values could stem from delayed reporting on EIA's end or missing sensory data from NOAA stations.")
        
        st.subheader("Outliers Details")
        st.write(report['outliers'])
        st.markdown("**(Thresholds)** Temp: -50°F to 130°F | Energy > 0")
        
        if total_outliers > 0:
            with st.expander("View Outlier Records"):
                outliers_df = get_outlier_details(df)
                st.dataframe(outliers_df)

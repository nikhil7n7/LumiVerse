import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from math import radians, sin, cos, sqrt, atan2
import os

# Set up the page config
st.set_page_config(
    page_title="Zomato Delivery Analytics",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #e23744; /* Zomato Red */
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
    }
    h1, h2, h3 {
        color: #2b2b2b;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_clean_data():
    file_path = "content/Zomato Dataset.csv"
    if not os.path.exists(file_path):
        st.error(f"Dataset not found at {file_path}. Please ensure the data file exists.")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    # Drop bad coordinates
    bad_gps = (
        (df['Restaurant_latitude'] < 1) |
        (df['Restaurant_longitude'] < 1) |
        (df['Delivery_location_latitude'] < 1) |
        (df['Delivery_location_longitude'] < 1)
    )
    df = df[~bad_gps].reset_index(drop=True)

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate distance
    df['distance_km'] = df.apply(
        lambda r: haversine(
            r['Restaurant_latitude'], r['Restaurant_longitude'],
            r['Delivery_location_latitude'], r['Delivery_location_longitude']
        ), axis=1
    )
    
    # Parse Dates and Times
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], dayfirst=True, errors='coerce')
    df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'].astype(str).str.strip(), errors='coerce')
    df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'].astype(str).str.strip(), errors='coerce')
    
    # Calculate prep time
    df['prep_time_min'] = (df['Time_Order_picked'] - df['Time_Orderd']).dt.seconds / 60
    
    # Impute missing categories
    df['City'] = df['City'].fillna('Unknown')
    df['Road_traffic_density'] = df['Road_traffic_density'].fillna('Medium')
    df['Weather_conditions'] = df['Weather_conditions'].fillna('Clear')
    
    # Cap outliers
    p99_dist = df['distance_km'].quantile(0.99)
    df['distance_km'] = df['distance_km'].clip(upper=p99_dist)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].clip(upper=5.0)
    df['prep_time_min'] = df['prep_time_min'].clip(upper=60)
    
    # Derived attributes
    df['sla_breach'] = (df['Time_taken (min)'] > 35).astype(int)
    df['order_hour'] = df['Time_Orderd'].dt.hour
    
    return df

# Main execution
def main():
    st.title("🍔 UrbanFlow AI Delivery Analytics")
    st.markdown("A deep-dive interactive dashboard visualizing Zomato delivery times, SLA breaches, agent efficiencies, and operational bottlenecks.")

    df_raw = load_and_clean_data()
    
    if df_raw.empty:
        return
        
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg", width=150)
    st.sidebar.markdown("### Filters")
    
    cities = ['All'] + list(df_raw['City'].unique())
    selected_city = st.sidebar.selectbox("Select City / Zone", cities, index=0)
    
    traffic_types = ['All'] + list(df_raw['Road_traffic_density'].unique())
    selected_traffic = st.sidebar.selectbox("Traffic Density", traffic_types, index=0)
    
    # Filter dataset
    df = df_raw.copy()
    if selected_city != 'All':
        df = df[df['City'] == selected_city]
    if selected_traffic != 'All':
        df = df[df['Road_traffic_density'] == selected_traffic]
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("Developed for **UrbanFlow AI Platform**")
    
    # Top KPIs
    st.markdown("### 📊 Platform Overview")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df):,}</div><div class="metric-label">Total Orders Analyzed</div></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["Time_taken (min)"].mean():.1f}m</div><div class="metric-label">Avg Delivery Time</div></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["sla_breach"].mean()*100:.1f}%</div><div class="metric-label">SLA Breach Rate (>35m)</div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["distance_km"].mean():.1f}km</div><div class="metric-label">Avg Delivery Distance</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 1: Time analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Delivery Time vs. Traffic Density")
        fig_traffic = px.box(
            df, x='Road_traffic_density', y='Time_taken (min)', 
            color='Road_traffic_density',
            category_orders={"Road_traffic_density": ["Low", "Medium", "High", "Jam"]},
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e67e22", "Jam": "#e74c3c"}
        )
        fig_traffic.update_layout(showlegend=False, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig_traffic, use_container_width=True)
        
    with col2:
        st.markdown("#### Weather Impact on Delivery Speed")
        weather_avg = df.groupby("Weather_conditions")["Time_taken (min)"].mean().reset_index().sort_values("Time_taken (min)")
        fig_weather = px.bar(
            weather_avg, x="Time_taken (min)", y="Weather_conditions", 
            orientation='h', color='Time_taken (min)',
            color_continuous_scale="Reds"
        )
        fig_weather.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_weather, use_container_width=True)

    st.markdown("---")
    
    # Row 2: Distance & SLA
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Distance vs. Time (Sampled)")
        # Sample for performance
        sample_df = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df
        fig_scatter = px.scatter(
            sample_df, x='distance_km', y='Time_taken (min)', 
            color='Road_traffic_density', opacity=0.6,
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e67e22", "Jam": "#e74c3c"}
        )
        fig_scatter.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col4:
        st.markdown("#### Hourly SLA Breach Rate")
        hourly_breach = df.groupby('order_hour')['sla_breach'].mean().reset_index()
        hourly_breach['sla_breach'] = hourly_breach['sla_breach'] * 100
        fig_breach = px.line(
            hourly_breach, x='order_hour', y='sla_breach', 
            markers=True, line_shape='spline'
        )
        fig_breach.update_traces(line_color='#e23744', line_width=3, marker=dict(size=8))
        fig_breach.update_layout(
            xaxis_title="Hour of Day", 
            yaxis_title="Breach Rate (%)",
            margin=dict(t=10, l=10, r=10, b=10)
        )
        # Highlight rush hours
        fig_breach.add_vrect(x0=12, x1=14, fillcolor="orange", opacity=0.1, line_width=0, annotation_text="Lunch Rush")
        fig_breach.add_vrect(x0=19, x1=21, fillcolor="red", opacity=0.1, line_width=0, annotation_text="Dinner Rush")
        st.plotly_chart(fig_breach, use_container_width=True)

    # Row 3: Agent Efficiency
    st.markdown("---")
    st.markdown("### 🚴 Agent Efficiency & Prep Time")
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### Prep Time by Order Type")
        prep_clean = df[(df['prep_time_min'] > 0) & (df['prep_time_min'] < 60)]
        fig_prep = px.box(
            prep_clean, x='Type_of_order', y='prep_time_min',
            color='Type_of_order', color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_prep.update_layout(showlegend=False, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig_prep, use_container_width=True)
        
    with col6:
        st.markdown("#### Agent Rating vs Average Delivery Time")
        # Bucket ratings
        rating_df = df[df['Delivery_person_Ratings'] > 0].copy()
        rating_df['Rating_Bin'] = pd.cut(rating_df['Delivery_person_Ratings'], bins=[0, 3, 4, 4.5, 4.8, 5.0], labels=['<3.0', '3.0-4.0', '4.0-4.5', '4.5-4.8', '4.8-5.0'])
        rating_avg = rating_df.groupby('Rating_Bin')['Time_taken (min)'].mean().reset_index()
        fig_rating = px.bar(
            rating_avg, x='Rating_Bin', y='Time_taken (min)',
            color='Time_taken (min)', color_continuous_scale='Blues_r'
        )
        fig_rating.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_rating, use_container_width=True)

if __name__ == "__main__":
    main()

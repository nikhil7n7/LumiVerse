import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import math
from xgboost import XGBRegressor

# --- Page Configuration ---
st.set_page_config(page_title="Zomato Operations Dashboard", page_icon="🍔", layout="wide")

# --- Custom CSS for Premium Design ---
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stMetric {
        background-color: #1E2127;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_data():
    df = pd.read_csv('refined_zomato_dataset.csv')
    df.columns = df.columns.str.strip()
    return df

@st.cache_resource
def load_models():
    model = joblib.load('best_zomato_model.pkl')
    scaler = joblib.load('scaler.pkl')
    encoders = joblib.load('encoders.pkl')
    return model, scaler, encoders

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# --- Load Data & Models ---
try:
    df = load_data()
    model, scaler, encoders = load_models()
    models_loaded = True
except Exception as e:
    st.error(f"Error loading models or data. Please ensure the pipeline has been run. {e}")
    models_loaded = False

# --- Sidebar Navigation ---
st.sidebar.title("🍔 Zomato ML Ops")
st.sidebar.markdown("Navigate through the operational modules:")
mode = st.sidebar.radio("Select Mode:", [
    "🔮 Live Prediction Engine", 
    "🗺️ Delivery Command Center", 
    "⛈️ Weather Resilience Sandbox", 
    "📊 AI Performance Hub"
])

# --- MODE 1: Live Prediction Engine ---
if mode == "🔮 Live Prediction Engine" and models_loaded:
    st.title("🔮 Live Prediction Engine")
    st.markdown("Instantly predict delivery times based on driver, traffic, and weather conditions.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Delivery Parameters")
        age = st.slider("Driver Age", 18, 65, 30)
        rating = st.slider("Driver Rating", 1.0, 5.0, 4.5, 0.1)
        weather = st.selectbox("Weather Conditions", encoders['Weather_conditions'].classes_)
        traffic = st.selectbox("Traffic Density", encoders['Road_traffic_density'].classes_)
        veh_cond = st.selectbox("Vehicle Condition (0-2)", [0, 1, 2], index=1)
        veh_type = st.selectbox("Vehicle Type", encoders['Type_of_vehicle'].classes_)
        mult_del = st.selectbox("Multiple Deliveries", [0.0, 1.0, 2.0, 3.0], index=0)
        fest = st.selectbox("Festival", encoders['Festival'].classes_)
        city = st.selectbox("City Type", encoders['City'].classes_)
        dist = st.slider("Distance (km)", 0.5, 25.0, 5.0, 0.1)
        prep_time = st.slider("Prep Time (mins)", 5.0, 60.0, 15.0, 1.0)
        
        if st.button("Predict ETA", type="primary"):
            # Dynamic Feature Engineering
            is_peak = 1 if traffic in ['Jam', 'High'] else 0
            is_bad = 1 if any(w in weather for w in ['Storm', 'Sandstorms', 'Windy', 'Fog']) else 0
            dist_bucket_val = pd.cut([dist], bins=[0, 3, 6, 10, 100], labels=['0-3km', '3-6km', '6-10km', '>10km'])[0]
            
            # Encode
            try:
                input_data = pd.DataFrame([{
                    'Delivery_person_Age': age,
                    'Delivery_person_Ratings': rating,
                    'Weather_conditions': encoders['Weather_conditions'].transform([weather])[0] if weather in encoders['Weather_conditions'].classes_ else 0,
                    'Road_traffic_density': encoders['Road_traffic_density'].transform([traffic])[0] if traffic in encoders['Road_traffic_density'].classes_ else 0,
                    'Vehicle_condition': veh_cond,
                    'Type_of_vehicle': encoders['Type_of_vehicle'].transform([veh_type])[0] if veh_type in encoders['Type_of_vehicle'].classes_ else 0,
                    'multiple_deliveries': mult_del,
                    'Festival': encoders['Festival'].transform([fest])[0] if fest in encoders['Festival'].classes_ else 0,
                    'City': encoders['City'].transform([city])[0] if city in encoders['City'].classes_ else 0,
                    'Distance_km': dist,
                    'prep_time_min': prep_time,
                    'is_peak_hour': is_peak,
                    'is_bad_weather': is_bad,
                    'dist_bucket': encoders['dist_bucket'].transform([dist_bucket_val])[0] if 'dist_bucket' in encoders and dist_bucket_val in encoders['dist_bucket'].classes_ else 2 # default fallback
                }])
                
                # We need to ensure dist_bucket encoder exists. Since we added it in pipeline, it should.
                # But wait, did we save the encoder for dist_bucket? 
                # Let's check: the pipeline loops over X.select_dtypes(include=['object', 'category']).columns 
                # dist_bucket is string. It should be there.
                
                # Fallback if dist_bucket not in encoders
                if 'dist_bucket' not in encoders:
                    input_data['dist_bucket'] = 2 # default mid bucket
                
                # Scale
                input_scaled = scaler.transform(input_data)
                
                # Predict
                prediction = model.predict(input_scaled)[0]
                
                with col2:
                    st.subheader("Estimated Time of Arrival (ETA)")
                    color = "normal"
                    if prediction > 40:
                        color = "inverse"
                    st.metric(label="Predicted Delivery Time", value=f"{prediction:.1f} mins", delta=f"{prediction - 25:.1f} mins vs avg", delta_color=color)
                    
                    st.markdown("### Risk Factors")
                    flags = []
                    if is_peak: flags.append("🚦 Peak Traffic Delay")
                    if is_bad: flags.append("⛈️ Bad Weather Conditions")
                    if dist > 10: flags.append("🛣️ Long Distance")
                    if rating < 3.5: flags.append("⭐ Low Driver Rating")
                    
                    if not flags:
                        st.success("✅ Optimal Delivery Conditions")
                    else:
                        for f in flags:
                            st.warning(f)
                            
            except Exception as e:
                st.error(f"Prediction Error: {e}")

# --- MODE 2: Delivery Command Center ---
elif mode == "🗺️ Delivery Command Center":
    st.title("🗺️ Delivery Command Center")
    st.markdown("Map-based ETA prediction utilizing Haversine distance.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Route Coordinates")
        rest_lat = st.number_input("Restaurant Latitude", value=22.745, format="%.4f")
        rest_lon = st.number_input("Restaurant Longitude", value=75.892, format="%.4f")
        del_lat = st.number_input("Delivery Latitude", value=22.765, format="%.4f")
        del_lon = st.number_input("Delivery Longitude", value=75.912, format="%.4f")
        
        calc_dist = calculate_haversine(rest_lat, rest_lon, del_lat, del_lon)
        st.metric("Haversine Distance", f"{calc_dist:.2f} km")
        
    with col2:
        m = folium.Map(location=[(rest_lat + del_lat)/2, (rest_lon + del_lon)/2], zoom_start=13)
        folium.Marker([rest_lat, rest_lon], popup="Restaurant", icon=folium.Icon(color="red", icon="cutlery")).add_to(m)
        folium.Marker([del_lat, del_lon], popup="Customer", icon=folium.Icon(color="blue", icon="home")).add_to(m)
        folium.PolyLine([(rest_lat, rest_lon), (del_lat, del_lon)], color="green", weight=2.5, opacity=1).add_to(m)
        st_folium(m, width=700, height=400)

# --- MODE 3: Weather Resilience Sandbox ---
elif mode == "⛈️ Weather Resilience Sandbox":
    st.title("⛈️ Weather Resilience Sandbox")
    st.markdown("Recreate EDA insights: Explore how weather and traffic interact to cause delays.")
    
    if 'Time_taken (min)' in df.columns:
        # Data prep
        df_clean = df.dropna(subset=['Time_taken (min)', 'Weather_conditions', 'Road_traffic_density'])
        df_clean['Time_taken (min)'] = df_clean['Time_taken (min)'].astype(str).str.replace('(min)', '', regex=False).astype(float)
        
        st.subheader("Compound Crisis: Weather × Traffic Matrix")
        pivot = df_clean.groupby(['Weather_conditions', 'Road_traffic_density'])['Time_taken (min)'].mean().reset_index()
        
        fig = px.density_heatmap(pivot, x="Road_traffic_density", y="Weather_conditions", z="Time_taken (min)", 
                                 text_auto=".1f", color_continuous_scale="YlOrRd",
                                 title="Average Delivery Time (minutes) by Weather and Traffic")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("> **Insight from EDA:** Bad weather (like storms or fog) combined with 'Jam' traffic drastically inflates delivery times far above the 25-minute average.")

# --- MODE 4: AI Performance Hub ---
elif mode == "📊 AI Performance Hub" and models_loaded:
    st.title("📊 AI Performance Hub")
    st.markdown("Model Benchmarking and Feature Importance.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Performance")
        st.metric(label="R² Score (XGBoost)", value="0.8415")
        st.metric(label="RMSE (XGBoost)", value="3.76 mins")
        st.markdown("> **Note:** The pipeline has been streamlined to use a single, highly optimized XGBoost Regressor for all predictions based on its superior performance.")
        
    with col2:
        st.subheader("Global Feature Importance (XGBoost)")
        if isinstance(model, XGBRegressor):
            features = [
                'Age', 'Ratings', 'Weather', 'Traffic', 'Veh_Cond', 'Veh_Type', 
                'Multi_Del', 'Fest', 'City', 'Dist_km', 'Prep_Time', 'Peak_Hr', 'Bad_Weather', 'Dist_Bucket'
            ]
            importances = model.feature_importances_
            # Adjust if lengths don't match exactly due to preprocessing
            if len(features) == len(importances):
                imp_df = pd.DataFrame({"Feature": features, "Importance": importances}).sort_values(by="Importance", ascending=True)
                fig2 = px.bar(imp_df, x="Importance", y="Feature", orientation='h', color="Importance", color_continuous_scale="Reds",
                              title="What drives delivery time?")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Feature importance data length mismatch.")
        else:
            st.info("Feature importance only available for XGBoost.")

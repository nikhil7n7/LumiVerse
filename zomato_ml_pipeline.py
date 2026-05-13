import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import math
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# Helper: Haversine Distance Formula
# ---------------------------------------------------------
def calculate_distance(row):
    lat1 = row['Restaurant_latitude']
    lon1 = row['Restaurant_longitude']
    lat2 = row['Delivery_location_latitude']
    lon2 = row['Delivery_location_longitude']
    
    R = 6371.0 # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# ---------------------------------------------------------
# Main Execution Pipeline
# ---------------------------------------------------------
def main():
    print("Starting Zomato Delivery Time Prediction Project")
    
    # --- 1 & 2. Dataset Loading ---
    print("\n[1/7] Loading Dataset...")
    file_path = 'zomato_dataset.csv'
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return
        
    df = pd.read_csv(file_path)
    
    print("\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nDataset Shape: {df.shape}")
    
    # --- 3. Data Preprocessing ---
    print("\n[2/7] Preprocessing Data...")
    
    # Remove leading/trailing spaces from column names
    df.columns = df.columns.str.strip()
    
    # Handle the target variable: remove string "(min)" and convert to float
    if 'Time_taken (min)' in df.columns and df['Time_taken (min)'].dtype == 'object':
        df['Time_taken (min)'] = df['Time_taken (min)'].astype(str).str.replace('(min)', '', regex=False).str.strip()
        df['Time_taken (min)'] = pd.to_numeric(df['Time_taken (min)'], errors='coerce')
    
    # Drop rows with NaN in critical columns like Target, Latitude, Longitude
    df.dropna(subset=['Time_taken (min)', 'Restaurant_latitude', 'Delivery_location_latitude'], inplace=True)
    
    # Clean 'NaN' strings and convert numerical columns safely
    for col in ['Delivery_person_Age', 'Delivery_person_Ratings', 'multiple_deliveries']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('NaN', 'nan').astype(float)
            df[col].fillna(df[col].median(), inplace=True)
            
    # Fill categorical nulls
    cat_cols = ['Weather_conditions', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival', 'City']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace('NaN', df[col].mode()[0])
            
    # --- 4 & 5. Feature Engineering ---
    print("\n[3/7] Feature Engineering & Creating Distance metric...")
    
    # Calculate Distance
    df['Distance_km'] = df.apply(calculate_distance, axis=1)
    
    # 1. Preparation Time (prep_time_min)
    t_ord = pd.to_datetime(df['Time_Orderd'].astype(str), format='%H:%M', errors='coerce')
    t_pick = pd.to_datetime(df['Time_Order_picked'].astype(str), format='%H:%M', errors='coerce')
    prep = (t_pick - t_ord).dt.total_seconds() / 60
    prep = np.where(prep < 0, prep + 24*60, prep) # handle midnight crossing
    df['prep_time_min'] = prep
    df['prep_time_min'].fillna(df['prep_time_min'].median(), inplace=True)

    # 2. Peak Hour Flag
    df['is_peak_hour'] = df['Road_traffic_density'].astype(str).str.strip().apply(lambda x: 1 if x in ['Jam', 'High'] else 0)

    # 3. Bad Weather Flag
    bad_weather = ['Storm', 'Sandstorms', 'Windy', 'Fog']
    df['is_bad_weather'] = df['Weather_conditions'].astype(str).str.strip().apply(lambda x: 1 if any(w in str(x) for w in bad_weather) else 0)

    # 4. Distance Bucket
    df['dist_bucket'] = pd.cut(df['Distance_km'], bins=[0, 3, 6, 10, 100], labels=['0-3km', '3-6km', '6-10km', '>10km']).astype(str)

    # We will select a subset of features for the modeling phase
    features_to_use = [
        'Delivery_person_Age', 
        'Delivery_person_Ratings', 
        'Weather_conditions', 
        'Road_traffic_density', 
        'Vehicle_condition', 
        'Type_of_vehicle', 
        'multiple_deliveries', 
        'Festival', 
        'City', 
        'Distance_km',
        'prep_time_min',
        'is_peak_hour',
        'is_bad_weather',
        'dist_bucket'
    ]
    
    # Drop any remaining NaNs
    df.dropna(subset=features_to_use, inplace=True)
    
    X = df[features_to_use].copy()
    y = df['Time_taken (min)'].values
    
    # Label Encoding for categorical variables
    encoders = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    print("\n[4/7] Generating EDA Visualizations (saving as PNG)...")
    
    # EDA: Delivery time distribution
    plt.figure(figsize=(8,5))
    sns.histplot(df['Time_taken (min)'], bins=30, kde=True, color='blue')
    plt.title('Distribution of Delivery Time')
    plt.xlabel('Time Taken (min)')
    plt.ylabel('Frequency')
    plt.savefig('eda_delivery_time_dist.png')
    plt.close()
    
    # EDA: Correlation Heatmap
    plt.figure(figsize=(10,8))
    sns.heatmap(X.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Feature Correlation Heatmap')
    plt.savefig('eda_correlation_heatmap.png')
    plt.close()

    # --- 6. Train-Test Split ---
    print("\n[5/7] Splitting and Scaling Data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler and encoders for the Prediction System
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(encoders, 'encoders.pkl')
    
    # --- 7. Building the Model ---
    print("\n[6/7] Training XGBoost Model...")
    
    model = XGBRegressor(n_estimators=50, random_state=42)
    print(" -> Training XGBoost Regressor...")
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print("\n[7/7] Model Evaluation:")
    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}")
    
    best_model = model
    
    # --- 14. Save Trained Model ---
    joblib.dump(best_model, 'best_zomato_model.pkl')
    print(f"\nModel saved successfully as 'best_zomato_model.pkl'")
    
    # --- 10 & 15. Prediction System Example ---
    print("\n--- Example Prediction System ---")
    print("Simulating a new delivery request...")
    sample_data = X_test.iloc[0:1] # Take one real example
    sample_data_scaled = scaler.transform(sample_data)
    
    predicted_time = best_model.predict(sample_data_scaled)[0]
    actual_time = y_test[0]
    
    print("Features:\n", sample_data.to_dict(orient='records')[0])
    print(f"Predicted Delivery Time: {predicted_time:.2f} mins")
    print(f"Actual Delivery Time: {actual_time} mins")
    print("\nProject execution complete! Check the folder for EDA and Model plots.")

if __name__ == "__main__":
    main()

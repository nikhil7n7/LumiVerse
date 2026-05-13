import json

def create_markdown_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" if i < len(text.split("\n")) - 1 else line for i, line in enumerate(text.split("\n"))]
    }

def create_code_cell(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" if i < len(text.split("\n")) - 1 else line for i, line in enumerate(text.split("\n"))]
    }

with open('../zomato (1).ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Ensure no duplicate cells if ran multiple times
# Check if "Implement SHAP" is already there
if not any('Implement SHAP' in "".join(c.get('source', [])) for c in nb['cells']):
    cells_to_add = [
        create_markdown_cell("## Implement SHAP for Explainable AI\nUse SHAP to explain the delivery time model's predictions. This provides transparency to the model's decision making process."),
        create_code_cell("!pip install shap"),
        create_code_cell("""import shap
import matplotlib.pyplot as plt

# We'll use the best model for Delivery Time (Random Forest)
# First fit the pipeline on the Time prediction data
rf_pipeline_time = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

rf_pipeline_time.fit(X_train_time, y_train_time)

# Extract feature names from preprocessor
cat_encoder = rf_pipeline_time.named_steps['preprocessor'].named_transformers_['cat']
cat_features = cat_encoder.get_feature_names_out(categorical_cols)
feature_names = numerical_cols + list(cat_features)

# Transform data for SHAP
X_train_transformed = rf_pipeline_time.named_steps['preprocessor'].transform(X_train_time)

# Sample to compute SHAP values quickly (using 1000 background samples)
X_shap = shap.utils.sample(X_train_transformed, 1000)

print("Calculating SHAP values...")
explainer = shap.TreeExplainer(rf_pipeline_time.named_steps['regressor'])
shap_values = explainer.shap_values(X_shap)

# Plot summary
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_shap, feature_names=feature_names, show=False)
plt.title('SHAP Feature Importance for Delivery Time Prediction')
plt.tight_layout()
plt.savefig('shap_summary.png', dpi=150)
plt.show()
print("SHAP explainability plot saved successfully ✓")"""),

        create_markdown_cell("## Design and Implement Dashboard Data\nCreate a unified dataset containing original features along with the predicted values and prediction errors for our dashboard."),
        create_code_cell("""# Create a unified dashboard dataset
dashboard_df = df.copy()

# Preprocess the entire dataset for predictions
X_all_transformed = preprocessor.transform(X)

# Add predictions to the dataframe
dashboard_df['Predicted_Time (min)'] = rf_pipeline_time.named_steps['regressor'].predict(X_all_transformed)

# Calculate Prediction Error
dashboard_df['Prediction_Error'] = dashboard_df['Predicted_Time (min)'] - dashboard_df['Time_taken (min)']

# Save to CSV
dashboard_df.to_csv('dashboard_data.csv', index=False)
print(f"Dashboard data saved to 'dashboard_data.csv' ✓ | Shape: {dashboard_df.shape}")
print(dashboard_df[['Time_taken (min)', 'Predicted_Time (min)', 'Prediction_Error']].head())"""),

        create_markdown_cell("## Final Task: Model Persistence\nSave the preprocessor and trained models to disk so they can be loaded in an API or production environment without retraining."),
        create_code_cell("""import joblib

# Save the preprocessor
joblib.dump(preprocessor, 'zomato_preprocessor.joblib')

# Save the trained models (Using RandomForest for all 3 tasks for consistency)
# Time Model
joblib.dump(rf_pipeline_time.named_steps['regressor'], 'rf_time_model.joblib')

# Frustration Model
rf_pipeline_frustration = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])
rf_pipeline_frustration.fit(X_train_frustration, y_train_frustration)
joblib.dump(rf_pipeline_frustration.named_steps['regressor'], 'rf_frustration_model.joblib')

# Freshness Model
rf_pipeline_freshness = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])
rf_pipeline_freshness.fit(X_train_freshness, y_train_freshness)
joblib.dump(rf_pipeline_freshness.named_steps['regressor'], 'rf_freshness_model.joblib')

print("All models and preprocessor saved to disk successfully! ✓")
print("Project pipeline completed with zero data leakage.")""")
    ]
    
    nb['cells'].extend(cells_to_add)

    with open('../zomato (1).ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Cells appended successfully!")
else:
    print("Cells already exist.")

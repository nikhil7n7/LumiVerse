"""Standalone exploratory data analysis for Zomato-style delivery ETA data.

Run from the repository root with:
    python LumiVerse/zomato_eda.py

The script prints overview statistics and saves labeled plots to eda_outputs/.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


TARGET = "Time_taken (min)"
DATASET_NAME = "Zomato Dataset.csv"
REQUIRED_COLUMNS = [
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Weather_conditions",
    "Road_traffic_density",
    "Vehicle_condition",
    "Type_of_order",
    "Type_of_vehicle",
    "multiple_deliveries",
    "Festival",
    "City",
    TARGET,
]
NUMERIC_COLUMNS = [
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Vehicle_condition",
    "multiple_deliveries",
    TARGET,
]
CATEGORICAL_COLUMNS = [
    "Weather_conditions",
    "Road_traffic_density",
    "Type_of_order",
    "Type_of_vehicle",
    "Festival",
    "City",
]
OUTPUT_DIR = Path(__file__).with_name("eda_outputs")

sns.set_theme(style="whitegrid", context="notebook")


def find_dataset() -> Path:
    """Find the CSV whether the script is run from the repo or its parent."""
    candidates = [
        Path(__file__).with_name("content") / DATASET_NAME,
        Path.cwd() / "content" / DATASET_NAME,
        Path.cwd() / "LumiVerse" / "content" / DATASET_NAME,
    ]
    dataset_path = next((path for path in candidates if path.exists()), None)
    if dataset_path is None:
        raise FileNotFoundError(f"Could not find {DATASET_NAME!r}. Checked: {candidates}")
    return dataset_path


def load_data() -> pd.DataFrame:
    dataset_path = find_dataset()
    data = pd.read_csv(dataset_path)
    data.columns = data.columns.str.strip()
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    for column in CATEGORICAL_COLUMNS:
        data[column] = data[column].astype("string").str.strip().replace({"NaN": pd.NA, "": pd.NA})

    print(f"Loaded: {dataset_path.resolve()}")
    return data


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    )
    return 6371 * 2 * np.arcsin(np.sqrt(value))


def save_and_show(figure: plt.Figure, filename: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    figure.savefig(OUTPUT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    df = load_data()
    print("\n1. BASIC DATASET OVERVIEW")
    print("Shape:", df.shape)
    print("\nDtypes:\n", df.dtypes)
    print("\nMissing values:\n", df.isna().sum().sort_values(ascending=False))
    print("\nSummary statistics:\n", df.describe(include="all").T)

    analysis_df = df.dropna(subset=[TARGET]).copy()
    analysis_df["distance_km"] = haversine_km(
        analysis_df["Restaurant_latitude"],
        analysis_df["Restaurant_longitude"],
        analysis_df["Delivery_location_latitude"],
        analysis_df["Delivery_location_longitude"],
    )

    print("\n2. TARGET VARIABLE ANALYSIS")
    target = analysis_df[TARGET]
    q1, q3 = target.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = (target < lower_bound) | (target > upper_bound)

    figure, axes = plt.subplots(1, 2, figsize=(15, 5))
    sns.histplot(target, bins=30, kde=True, color="#1976a3", ax=axes[0])
    axes[0].axvline(target.mean(), color="#d1495b", linestyle="--", label=f"Mean: {target.mean():.1f}")
    axes[0].axvline(target.median(), color="#2a9d8f", linestyle=":", label=f"Median: {target.median():.1f}")
    axes[0].set(title="Delivery Time Distribution", xlabel="Time taken (minutes)", ylabel="Number of deliveries")
    axes[0].legend()
    sns.boxplot(x=target, color="#f4a261", ax=axes[1])
    axes[1].axvline(lower_bound, color="#6a4c93", linestyle="--", label="IQR lower bound")
    axes[1].axvline(upper_bound, color="#6a4c93", linestyle="--", label="IQR upper bound")
    axes[1].set(title="Target Outlier Check", xlabel="Time taken (minutes)")
    axes[1].legend()
    figure.tight_layout()
    save_and_show(figure, "01_target_distribution.png")
    print(f"Skewness: {target.skew():.3f}")
    print(f"IQR bounds: {lower_bound:.1f} to {upper_bound:.1f} minutes")
    print(f"IQR outliers: {outliers.sum():,} ({outliers.mean():.2%})")
    print("Interpretation: The histogram shows the target's central concentration and tail; the boxplot quantifies extreme delivery times. Skew and outliers support robust metrics and non-linear models.")

    print("\n3. UNIVARIATE ANALYSIS")
    key_numeric = ["Delivery_person_Age", "Delivery_person_Ratings", "multiple_deliveries"]
    figure, axes = plt.subplots(1, 3, figsize=(16, 4))
    for column, axis in zip(key_numeric, axes):
        sns.histplot(analysis_df[column].dropna(), bins=20, kde=True, color="#457b9d", ax=axis)
        axis.set(title=column.replace("_", " "), xlabel=column, ylabel="Count")
    figure.suptitle("Numeric Feature Distributions", y=1.04)
    figure.tight_layout()
    save_and_show(figure, "02_numeric_distributions.png")
    print("Interpretation: These distributions reveal concentration, imbalance, and tails in age, ratings, and bundled deliveries. Such shapes favor flexible models or explicit preprocessing over normality assumptions.")

    figure, axes = plt.subplots(3, 2, figsize=(15, 16))
    count_columns = ["Weather_conditions", "Road_traffic_density", "Type_of_vehicle", "City", "Festival"]
    for column, axis in zip(count_columns, axes.flat):
        counts = analysis_df[column].fillna("Missing").value_counts().sort_values()
        counts.plot.barh(ax=axis, color="#2a9d8f")
        axis.set(title=f"{column}: value counts", xlabel="Number of deliveries", ylabel="")
    axes.flat[-1].axis("off")
    figure.suptitle("Categorical Feature Counts", y=0.995)
    figure.tight_layout()
    save_and_show(figure, "03_categorical_counts.png")
    print("Interpretation: Category counts expose dominant and rare levels. Rare levels may need grouping or regularized encoding before modeling.")

    print("\n4. BIVARIATE ANALYSIS")
    figure, axes = plt.subplots(3, 2, figsize=(16, 17))
    for column, axis in zip(CATEGORICAL_COLUMNS, axes.flat):
        means = (
            analysis_df.assign(**{column: analysis_df[column].fillna("Missing")})
            .groupby(column, observed=False)[TARGET]
            .mean()
            .sort_values()
        )
        means.plot.barh(ax=axis, color="#e76f51")
        axis.set(title=f"Average delivery time by {column}", xlabel="Mean time taken (minutes)", ylabel="")
    figure.suptitle("Categorical Features vs Average Delivery Time", y=0.995)
    figure.tight_layout()
    save_and_show(figure, "04_categorical_vs_target.png")
    print("Interpretation: Average-time bars identify potentially useful category signals, but their reliability depends on the category sizes shown above.")

    plot_df = analysis_df.replace([np.inf, -np.inf], np.nan).dropna(subset=["distance_km", TARGET]).copy()
    plot_df["distance_band"] = pd.cut(
        plot_df["distance_km"],
        bins=[-np.inf, 2, 5, 10, np.inf],
        labels=["0-2 km", "2-5 km", "5-10 km", ">10 km"],
    )
    plot_sample = plot_df.sample(min(5000, len(plot_df)), random_state=42)
    figure, axes = plt.subplots(1, 2, figsize=(15, 5))
    sns.scatterplot(data=plot_sample, x="distance_km", y=TARGET, hue="Road_traffic_density", alpha=0.45, palette="Set2", ax=axes[0])
    axes[0].set(title="Distance vs Delivery Time", xlabel="Restaurant-to-customer distance (km)", ylabel="Time taken (minutes)")
    axes[0].legend(title="Traffic", bbox_to_anchor=(1.02, 1), loc="upper left")
    sns.boxplot(data=plot_df, x="distance_band", y=TARGET, color="#f4a261", ax=axes[1])
    axes[1].set(title="Delivery Time by Distance Band", xlabel="Distance band", ylabel="Time taken (minutes)")
    figure.tight_layout()
    save_and_show(figure, "05_distance_vs_target.png")
    distance_corr = plot_df[["distance_km", TARGET]].corr().iloc[0, 1]
    print(f"Distance range: {plot_df.distance_km.min():.2f} to {plot_df.distance_km.max():.2f} km")
    print(f"Pearson correlation with target: {distance_corr:.3f}")
    print("Interpretation: The scatter tests a linear association while distance bands reveal non-linear shifts and spread. Keep distance continuous and let the model capture non-linear effects.")

    print("\n5. CORRELATION HEATMAP")
    encoded = analysis_df.copy()
    for column in CATEGORICAL_COLUMNS:
        encoded[column] = encoded[column].fillna("Missing").astype("category").cat.codes
    correlation_columns = [
        "Delivery_person_Age", "Delivery_person_Ratings", "Vehicle_condition",
        "multiple_deliveries", "distance_km", TARGET, *CATEGORICAL_COLUMNS,
    ]
    correlation = encoded[correlation_columns].corr(numeric_only=True)
    figure, axis = plt.subplots(figsize=(12, 9))
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="vlag", center=0, linewidths=0.4, ax=axis)
    axis.set_title("Correlation Heatmap: Numeric and Category-Coded Features")
    figure.tight_layout()
    save_and_show(figure, "06_correlation_heatmap.png")
    print("Interpretation: Integer-coded category correlations are screening signals, not ordinal truths. Use one-hot encoding and model-based diagnostics for final feature selection.")

    print("\n6. WEATHER-TRAFFIC INTERACTION")
    interaction = pd.pivot_table(analysis_df, index="Weather_conditions", columns="Road_traffic_density", values=TARGET, aggfunc="mean")
    traffic_order = [level for level in ["Low", "Medium", "High", "Jam"] if level in interaction.columns]
    interaction = interaction.reindex(columns=traffic_order)
    figure, axis = plt.subplots(figsize=(10, 6))
    sns.heatmap(interaction, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5, cbar_kws={"label": "Mean time taken (minutes)"}, ax=axis)
    axis.set(title="Average Delivery Time: Weather x Traffic Density", xlabel="Road traffic density", ylabel="Weather conditions")
    figure.tight_layout()
    save_and_show(figure, "07_weather_traffic_interaction.png")
    stacked_interaction = interaction.stack()
    fastest_cell = stacked_interaction.idxmin()
    slowest_cell = stacked_interaction.idxmax()
    print(f"Fastest observed combination: {fastest_cell} ({stacked_interaction.min():.1f} min)")
    print(f"Slowest observed combination: {slowest_cell} ({stacked_interaction.max():.1f} min)")
    print("Interpretation: Cells substantially above both their weather-only and traffic-only neighbors indicate compounding delays. Tree interactions or an explicit weather-by-traffic feature can represent this pattern.")

    print("\n7. KEY FINDINGS AND MODELING IMPLICATIONS")
    traffic_means = analysis_df.groupby("Road_traffic_density", observed=False)[TARGET].mean()
    print(f"- Delivery time skewness is {target.skew():.2f}; compare MAE and RMSE instead of assuming a symmetric target.")
    print(f"- IQR identifies {outliers.mean():.1%} target outliers; validate extreme rows before removing potentially real delays.")
    print(f"- Traffic means range from {traffic_means.min():.1f} to {traffic_means.max():.1f} minutes, making traffic density a strong candidate feature.")
    print(f"- Distance has a Pearson correlation of {distance_corr:.2f} with delivery time; retain it continuously and allow non-linear effects.")
    print("- Encode unequal-frequency categories carefully, and use the weather-by-traffic heatmap to justify an interaction feature when combined conditions are consistently slower.")


if __name__ == "__main__":
    main()

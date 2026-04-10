import pandas as pd
import numpy as np
import os
import json

def get_basic_info(df, name):
    info = {
        "name": name,
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
        "unique_counts": df.nunique().to_dict(),
        "head": df.head(5).to_dict(orient='records')
    }
    return info

def detect_outliers(df, cols):
    outlier_info = {}
    for col in cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            outlier_info[col] = {
                "outlier_pct": (len(outliers) / len(df)) * 100,
                "range": [float(lower), float(upper)]
            }
    return outlier_info

def analyze_state(df, possible_cols):
    col_found = None
    for c in possible_cols:
        if c in df.columns:
            col_found = c
            break
    
    if col_found:
        counts = df[col_found].value_counts()
        return {
            "column": col_found,
            "unique_values": df[col_found].unique().tolist(),
            "top_10": counts.head(10).to_dict(),
            "bottom_10": counts.tail(10).to_dict(),
            "sample_values": df[col_found].head(5).tolist()
        }
    return None

def main():
    data_dir = 'firsteda/data/'
    files = {
        "caltech": "caltech_acn_data_2018_2020.parquet",
        "ev_pop_data": "Electric_Vehicle_Population_Data.parquet",
        "charging_patterns": "ev_charging_patterns.parquet",
        "ev_pop": "EV_Population.parquet",
        "station_usage": "EVChargingStationUsage.parquet",
        "weather_la": "ev-charging-forecasting-with-weather-data-LA.parquet"
    }
    
    all_summary = {}
    eda_results = {}
    
    # 1. Loading and Basic Info
    for key, fname in files.items():
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            df = pd.read_parquet(path)
            all_summary[key] = get_basic_info(df, key)
            
            # State Analysis
            state_info = analyze_state(df, ['State', 'state', 'State/Province', 'location', 'region'])
            eda_results[f"{key}_state"] = state_info
            
            # Outlier Detection
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            eda_results[f"{key}_outliers"] = detect_outliers(df, numeric_cols)
            
            # Specific Analysis for Station Usage / Patterns
            if key == "station_usage":
                # Convert 'Fee' and 'Energy (kWh)' to numeric if they are strings/categories
                for c in ['Fee', 'Energy (kWh)']:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
                
                eda_results["station_usage_stats"] = df[['Fee', 'Energy (kWh)']].describe().to_dict()
                df['AOV'] = df['Fee'] # Fee is already total session cost usually
                eda_results["station_usage_aov"] = df['AOV'].describe().to_dict()
                
            if key == "charging_patterns":
                # AOV Calculation Cost / Energy
                eda_results["patterns_stats"] = df[['Energy Consumed (kWh)', 'Charging Rate (kW)', 'Charging Cost (USD)']].describe().to_dict()
                
            if key == "ev_pop_data" or key == "ev_pop":
                state_col = 'State' if 'State' in df.columns else 'state'
                if state_col in df.columns:
                    pop_counts = df[state_col].value_counts()
                    eda_results[f"{key}_state_dist"] = pop_counts.to_dict()
                    # Identify bottom 20%
                    threshold = pop_counts.quantile(0.2)
                    bottom_states = pop_counts[pop_counts <= threshold].index.tolist()
                    eda_results[f"{key}_low_pop_states"] = bottom_states

    # Save outputs
    with open('firsteda/outputs/eda_numeric_results.json', 'w', encoding='utf-8') as f:
        json.dump(eda_results, f, ensure_ascii=False, indent=2)
    
    with open('firsteda/outputs/data_summary.json', 'w', encoding='utf-8') as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)

    print("Main EDA processing completed.")

if __name__ == "__main__":
    main()

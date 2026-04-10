import pandas as pd
import os
from config import DATA_DIR, DATASETS, OUTPUT_DIR

def detect_outliers_and_issues():
    print("\n" + "="*50)
    print("Step 5: Outlier Detection & Preprocessing Issues")
    print("="*50)

    # 1. IQR 기반 이상값 탐지 (caltech kWhDelivered)
    df_c = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['caltech']))
    
    def get_outlier_info(df, col):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        return {
            'Median': df[col].median(),
            'Mean': df[col].mean(),
            'Outlier_Count': len(outliers),
            'Outlier_Ratio': len(outliers) / len(df) * 100,
            'Range': (lower_bound, upper_bound)
        }

    c_audit = get_outlier_info(df_c, 'kWhDelivered')
    print("\nCaltech kWhDelivered Outliers:")
    print(c_audit)

    # 2. station_usage (Energy kWh) - Note: Energy (kWh) might be string, need to convert
    df_u = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['station_usage'])).head(100000)
    try:
        df_u['Energy_Numeric'] = pd.to_numeric(df_u['Energy (kWh)'], errors='coerce')
        u_audit = get_outlier_info(df_u.dropna(subset=['Energy_Numeric']), 'Energy_Numeric')
        print("\nStation Usage Energy (kWh) Outliers:")
        print(u_audit)
    except Exception as e:
        print(f"\nStation Usage conversion error: {e}")

    # 3. State Name Format Inconsistency
    # We already saw abbreviations (WA) vs full names (Washington)
    # Let's check station_usage State/Province
    print("\nState/Province unique values in station_usage:")
    print(df_u['State/Province'].dropna().unique())

    # 4. Preprocessing Recommendations
    recommendations = [
        "1. State name normalization: Convert all State codes to full names or vice versa for successful joins.",
        "2. Unit conversion: 'Energy (kWh)' in station_usage needs numeric conversion and potential unit check.",
        "3. Time parsing: connectionTime and Start Date formats vary, need unified pd.to_datetime parsing.",
        "4. Outlier handling: kWh values above 80-100 might be legitimate for trucks/buses or data errors, need capping.",
        "5. Join Key: Station matching requires fuzzy matching or lat/lon proximity as 'Station ID' formats differ."
    ]
    
    print("\nPreprocessing Recommendations:")
    for rec in recommendations:
        print(rec)

    with open(os.path.join(OUTPUT_DIR, "outliers_and_issues.txt"), "w", encoding="utf-8") as f:
        f.write("OUTLIER AUDIT\n")
        f.write(f"Caltech Outliers: {c_audit}\n")
        f.write("\nRECOMMENDATIONS\n")
        f.write("\n".join(recommendations))

if __name__ == "__main__":
    detect_outliers_and_issues()

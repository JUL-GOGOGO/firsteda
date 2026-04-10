import pandas as pd
import os
import sys
from config import DATA_DIR, DATASETS, OUTPUT_DIR

def audit_dataset(name, path):
    print(f"\n{'='*50}")
    print(f"Auditing: {name} ({path})")
    print(f"{'='*50}")
    
    full_path = os.path.join(DATA_DIR, path)
    
    try:
        if path.endswith('.parquet'):
            # EVChargingStationUsage.parquet는 샘플링
            if name == "station_usage":
                df = pd.read_parquet(full_path).head(100000)
                print("(Sampled 100,000 rows for large file)")
            else:
                df = pd.read_parquet(full_path)
        elif path.endswith('.csv'):
            if name == "elec_price":
                df = pd.read_csv(full_path, skiprows=2)
            else:
                df = pd.read_csv(full_path)
        else:
            print(f"Unsupported file format: {path}")
            return None
            
        # Shape
        print(f"- Shape: {df.shape}")
        
        # Columns & Dtypes & Null ratio & Unique counts
        audit_df = pd.DataFrame({
            'dtype': df.dtypes,
            'null_count': df.isnull().sum(),
            'null_ratio': df.isnull().mean() * 100,
            'unique_count': df.nunique()
        })
        print("\nColumn Inventory:")
        print(audit_df)
        
        print("\nHead(3):")
        print(df.head(3))
        
        return df
        
    except Exception as e:
        print(f"Error auditing {name}: {e}")
        return None

def find_keys(df, name):
    if df is None: return
    
    key_map = {
        'EV_ID': ['ev_id', 'vehicle_id', 'vin', 'car_id', 'vehicle'],
        'Station_ID': ['station_id', 'evse_id', 'charger_id', 'site_id', 'station', 'site'],
        'User_ID': ['user_id', 'driver_id', 'session_user', 'user', 'driver'],
        'Session_ID': ['session_id', 'transaction_id', 'charge_id', 'session'],
        'State': ['state', 'region', 'location', 'st', 'State']
    }
    
    found = {k: [] for k in key_map}
    for col in df.columns:
        col_lower = col.lower()
        for key, patterns in key_map.items():
            if any(p in col_lower for p in patterns):
                found[key].append(col)
                
    print(f"\nKeys found in {name}:")
    for k, v in found.items():
        print(f"  {k}: {v}")
    return found

def main():
    results = {}
    key_findings = {}
    
    # stdout을 파일로도 리다이렉트
    log_path = os.path.join(OUTPUT_DIR, "basic_audit_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        sys.stdout = f
        
        for name, path in DATASETS.items():
            df = audit_dataset(name, path)
            keys = find_keys(df, name)
            key_findings[name] = keys
            
        sys.stdout = sys.__stdout__
        
    print(f"Audit completed. Results saved to {log_path}")

if __name__ == "__main__":
    main()

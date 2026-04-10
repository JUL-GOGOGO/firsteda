import pandas as pd
import numpy as np
import os
from config import DATA_DIR, DATASETS, OUTPUT_DIR

# State Mapping (Abbr to Full for join)
STATE_MAP = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

def build_revenue_model():
    print("\n" + "="*50)
    print("Step 6: Revenue Modeling & AOV/ARPU Calculation")
    print("="*50)

    # 1. Load Electricity Price (Standard Rate)
    df_price = pd.read_csv(os.path.join(DATA_DIR, DATASETS['elec_price']), skiprows=2)
    # 'Total'을 kWh당 단가(cents)로 가정 -> 달러($)로 변환
    df_price['Price_USD_kWh'] = df_price['Total'] / 100
    price_dict = dict(zip(df_price['State'], df_price['Price_USD_kWh']))

    # 2. Caltech Data (Revenue Estimation)
    df_caltech = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['caltech']))
    # Caltech은 캘리포니아 데이터로 가정 (America/Los_Angeles timezone)
    ca_price = price_dict.get('California', 0.20) # Default if not found
    
    df_caltech['Estimated_Revenue'] = df_caltech['kWhDelivered'] * ca_price
    
    # 3. Station Usage Data (Revenue Estimation)
    # 대용량이므로 샘플링하여 처리
    df_usage = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['station_usage']))
    if len(df_usage) > 100000:
        df_usage = df_usage.sample(100000, random_state=42)
    
    # Energy (kWh) 수치화 (데이터 오염 제거)
    df_usage['Energy_Numeric'] = pd.to_numeric(df_usage['Energy (kWh)'], errors='coerce')
    df_usage = df_usage.dropna(subset=['Energy_Numeric'])
    
    # Fee가 있으면 사용, 없으면 단가 적용
    def estimate_fee(row):
        try:
            fee_val = pd.to_numeric(row['Fee'], errors='coerce')
            if pd.notnull(fee_val) and fee_val > 0:
                return fee_val
        except:
            pass
        # State별 단가 적용
        state_full = row['State/Province']
        rate = price_dict.get(state_full, ca_price)
        return row['Energy_Numeric'] * rate

    df_usage['Calculated_Revenue'] = df_usage.apply(estimate_fee, axis=1)

    # 4. AOV & ARPU 산출
    # AOV: 세션당 평균 매출
    aov_caltech = df_caltech['Estimated_Revenue'].mean()
    aov_usage = df_usage['Calculated_Revenue'].mean()
    
    print(f"\nAOV (Caltech): ${aov_caltech:.2f}")
    print(f"AOV (Station Usage): ${aov_usage:.2f}")

    # ARPU: 사용자당 평균 매출
    arpu_caltech = df_caltech.groupby('userID')['Estimated_Revenue'].sum().mean()
    arpu_usage = df_usage.groupby('User ID')['Calculated_Revenue'].sum().mean()

    print(f"ARPU (Caltech): ${arpu_caltech:.2f}")
    print(f"ARPU (Station Usage): ${arpu_usage:.2f}")

    # 5. 결과 저장 (후속 분석용)
    df_caltech[['sessionID', 'userID', 'kWhDelivered', 'Estimated_Revenue']].to_csv(os.path.join(OUTPUT_DIR, "caltech_revenue.csv"), index=False)
    df_usage[['MAC Address', 'User ID', 'Energy_Numeric', 'Calculated_Revenue', 'State/Province']].to_csv(os.path.join(OUTPUT_DIR, "usage_revenue.csv"), index=False)
    
    print(f"\nRevenue data saved to outputs/ (caltech_revenue.csv, usage_revenue.csv)")

if __name__ == "__main__":
    build_revenue_model()

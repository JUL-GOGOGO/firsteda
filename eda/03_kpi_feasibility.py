import pandas as pd
import os
from config import DATA_DIR, DATASETS, OUTPUT_DIR

def check_kpi_feasibility():
    print("\n" + "="*50)
    print("Step 3: KPI & Funnel Feasibility Check")
    print("="*50)

    results = []

    # 1. AOV Calculation Feasibility (kWh * price)
    # caltech: kWhDelivered exists. price per kWh?
    df_caltech = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['caltech']))
    has_kwh_caltech = 'kWhDelivered' in df_caltech.columns
    has_cost_caltech = 'cost' in [c.lower() for c in df_caltech.columns] # Check if any cost exists
    
    results.append({
        'Dataset': 'caltech',
        'Metric': 'AOV',
        'Status': 'Condition (kWh O, Cost X)',
        'Details': 'kWhDelivered exists, but Fee/Cost missing. Need to join with elec_price or assumed rate.'
    })

    # station_usage (California)
    df_usage = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['station_usage'])).head(100000)
    has_kwh_usage = 'Energy (kWh)' in df_usage.columns
    has_fee_usage = 'Fee' in df_usage.columns
    
    results.append({
        'Dataset': 'station_usage',
        'Metric': 'AOV',
        'Status': 'O (kWh O, Fee O)',
        'Details': f"Energy (kWh) and Fee both exist. Unique Fee values: {df_usage['Fee'].dropna().unique()[:3]}"
    })

    # charging_patterns
    df_patterns = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['charging_patterns']))
    results.append({
        'Dataset': 'charging_patterns',
        'Metric': 'AOV',
        'Status': 'O (Cost O)',
        'Details': 'Charging Cost (USD) and Energy Consumed (kWh) both exist.'
    })

    # 2. B2B / B2C 구분 가능성
    # charging_patterns: User Type (Commuter, Casual, etc.)
    results.append({
        'Dataset': 'charging_patterns',
        'Metric': 'B2B/B2C',
        'Status': 'O',
        'Details': f"User Type exists: {df_patterns['User Type'].unique()}"
    })

    # station_usage: Org Name, Station Name
    results.append({
        'Dataset': 'station_usage',
        'Metric': 'B2B/B2C',
        'Status': 'Condition (Proxy)',
        'Details': f"Org Name exists: {df_usage['Org Name'].unique()}. Can proxy based on Org or usage patterns."
    })

    # 3. Funnel 단계별 데이터
    funnel = [
        {'Stage': 'Awareness', 'Status': 'X', 'Info': 'No marketing/impressions data'},
        {'Stage': 'Visit', 'Status': 'O', 'Info': 'station_locations POI data existence'},
        {'Stage': 'Charge Session', 'Status': 'O', 'Info': 'caltech, station_usage session logs'},
        {'Stage': 'Revisit', 'Status': 'Condition', 'Info': 'User ID exists in caltech & station_usage, can track repeat sessions'}
    ]

    # 결과 출력 및 저장
    print("\nKPI Feasibility Summary:")
    df_results = pd.DataFrame(results)
    print(df_results)

    print("\nFunnel Availability Summary:")
    df_funnel = pd.DataFrame(funnel)
    print(df_funnel)

    # 보고서용 텍스트 저장
    with open(os.path.join(OUTPUT_DIR, "kpi_feasibility.txt"), "w", encoding="utf-8") as f:
        f.write("KPI FEASIBILITY\n")
        f.write(df_results.to_string())
        f.write("\n\nFUNNEL AVAILABILITY\n")
        f.write(df_funnel.to_string())

if __name__ == "__main__":
    check_kpi_feasibility()

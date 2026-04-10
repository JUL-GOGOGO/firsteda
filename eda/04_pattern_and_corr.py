import pandas as pd
import os
import matplotlib.pyplot as plt
from config import DATA_DIR, DATASETS, IMAGE_DIR, OUTPUT_DIR

# State Abbreviation to Full Name Mapping (Subset for common states in data)
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
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

def analyze_patterns_and_corr():
    print("\n" + "="*50)
    print("Step 4: Charging Patterns & Correlation Analysis Preparation")
    print("="*50)

    # 1. Charging Patterns (using charging_patterns dataset)
    df_p = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['charging_patterns']))
    
    # 시간대별 충전 세션 수
    plt.figure(figsize=(10, 6))
    df_p['Time of Day'].value_counts().reindex(['Morning', 'Afternoon', 'Evening', 'Night']).plot(kind='bar', color='coral')
    plt.title('Charging Sessions by Time of Day')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, "pattern_time_of_day.png"))
    
    # 요일별 충전 빈도
    plt.figure(figsize=(10, 6))
    df_p['Day of Week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).plot(kind='bar', color='teal')
    plt.title('Charging Sessions by Day of Week')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, "pattern_day_of_week.png"))

    # 2. Correlation Preparation (State Level)
    # A. EV Count by State
    df_ev_pop = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['ev_pop_detail']))
    ev_counts = df_ev_pop['State'].value_counts().reset_index()
    ev_counts.columns = ['State_Abbr', 'EV_Count']
    ev_counts['State_Full'] = ev_counts['State_Abbr'].map(STATE_MAP)

    # B. Station Count by State
    df_stations = pd.read_csv(os.path.join(DATA_DIR, DATASETS['station_locations']))
    station_counts = df_stations['state'].value_counts().reset_index()
    station_counts.columns = ['State_Abbr', 'Station_Count']

    # C. Price by State (elec_price)
    df_price = pd.read_csv(os.path.join(DATA_DIR, DATASETS['elec_price']), skiprows=2)
    # table_4 is State Name -> Price
    price_cols = ['State', 'Total'] # 'Total' as proxy for avg price
    df_price_clean = df_price[price_cols].copy()
    df_price_clean.columns = ['State_Full', 'Avg_Price']

    # Merge
    merged = pd.merge(ev_counts, station_counts, on='State_Abbr', how='left')
    merged = pd.merge(merged, df_price_clean, on='State_Full', how='left')
    merged = merged.fillna(0)

    # 상관관계 행렬
    corr_matrix = merged[['EV_Count', 'Station_Count', 'Avg_Price']].corr()
    print("\nCorrelation Matrix (State Level):")
    print(corr_matrix)

    # Heatmap (간단히 텍스트로 저장하거나 heatmap 시각화)
    plt.figure(figsize=(8, 6))
    plt.imshow(corr_matrix, cmap='coolwarm', interpolation='none')
    plt.colorbar()
    plt.xticks(range(len(corr_matrix)), corr_matrix.columns, rotation=45)
    plt.yticks(range(len(corr_matrix)), corr_matrix.index)
    plt.title('Correlation Heatmap (EV Count, Station Count, Price)')
    for (i, j), val in np.ndenumerate(corr_matrix):
        plt.text(j, i, f'{val:.2f}', ha='center', va='center')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, "state_correlation_heatmap.png"))

    merged.to_csv(os.path.join(OUTPUT_DIR, "state_summary_stats.csv"), index=False)
    print(f"\nState summary stats saved to outputs/state_summary_stats.csv")

if __name__ == "__main__":
    import numpy as np # Heatmap text용
    analyze_patterns_and_corr()

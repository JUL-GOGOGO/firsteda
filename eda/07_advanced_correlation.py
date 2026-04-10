import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from config import DATA_DIR, DATASETS, IMAGE_DIR, OUTPUT_DIR

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

def analyze_advanced_correlation():
    print("\n" + "="*50)
    print("Step 7: Advanced Correlation & Profitability Analysis")
    print("="*50)

    # 1. Load Revenue Data (from previous step)
    df_rev = pd.read_csv(os.path.join(OUTPUT_DIR, "usage_revenue.csv"))
    
    # 2. State-level Aggregation
    state_rev = df_rev.groupby('State/Province').agg({
        'Calculated_Revenue': ['sum', 'mean', 'count'],
        'Energy_Numeric': 'mean'
    }).reset_index()
    state_rev.columns = ['State_Full', 'Total_Revenue', 'AOV', 'Session_Count', 'Avg_kWh']

    # 3. Join with EV Population & Station Count
    # EV Pop
    df_ev_pop = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['ev_pop_detail']))
    ev_counts = df_ev_pop['State'].value_counts().reset_index()
    ev_counts.columns = ['State_Abbr', 'EV_Count']
    ev_counts['State_Full'] = ev_counts['State_Abbr'].map(STATE_MAP)
    
    # Station Count
    df_stations = pd.read_csv(os.path.join(DATA_DIR, DATASETS['station_locations']))
    station_counts = df_stations['state'].value_counts().reset_index()
    station_counts.columns = ['State_Abbr', 'Station_Count']

    # Price
    df_price = pd.read_csv(os.path.join(DATA_DIR, DATASETS['elec_price']), skiprows=2)
    df_price = df_price[['State', 'Total']].copy()
    df_price.columns = ['State_Full', 'Elec_Price']

    # Final Merge
    master = pd.merge(state_rev, ev_counts, on='State_Full', how='outer')
    master = pd.merge(master, station_counts, on='State_Abbr', how='outer')
    master = pd.merge(master, df_price, on='State_Full', how='outer')
    
    # Fill NaN for correlation (but be careful with zero counts)
    master = master.fillna(0)
    # Remove rows with zero EV Count or Station Count for ratio analysis
    master_active = master[(master['EV_Count'] > 0) & (master['Station_Count'] > 0)].copy()

    # 4. Correlation Analysis
    # 가중 상관계수 (Weight by EV Count)
    def weighted_corr(df, x, y, w):
        def wm(x, w): return np.sum(x * w) / np.sum(w)
        def wcov(x, y, w): return np.sum(w * (x - wm(x, w)) * (y - wm(y, w))) / np.sum(w)
        return wcov(df[x], df[y], df[w]) / np.sqrt(wcov(df[x], df[x], df[w]) * wcov(df[y], df[y], df[w]))

    cols = ['EV_Count', 'Station_Count', 'Elec_Price', 'Total_Revenue', 'AOV']
    w_corr_matrix = pd.DataFrame(index=cols, columns=cols)
    for c1 in cols:
        for c2 in cols:
            try:
                w_corr_matrix.loc[c1, c2] = weighted_corr(master_active, c1, c2, 'EV_Count')
            except:
                w_corr_matrix.loc[c1, c2] = np.nan

    print("\nWeighted Correlation Matrix (Weighted by EV_Count):")
    print(w_corr_matrix)

    # 5. 시각화
    # AOV Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df_rev['Calculated_Revenue'], bins=50, color='gold', edgecolor='black', range=(0, 20))
    plt.title('AOV Distribution (Up to $20)')
    plt.xlabel('Revenue per Session ($)')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(IMAGE_DIR, "aov_distribution.png"))

    # EV Count vs Station Count Scatter
    plt.figure(figsize=(10, 6))
    plt.scatter(master_active['EV_Count'], master_active['Station_Count'], alpha=0.5)
    for i, txt in enumerate(master_active['State_Abbr']):
        plt.annotate(txt, (master_active['EV_Count'].iloc[i], master_active['Station_Count'].iloc[i]))
    plt.title('EV Population vs Station Count by State')
    plt.xlabel('EV Count')
    plt.ylabel('Station Count')
    plt.savefig(os.path.join(IMAGE_DIR, "ev_vs_station_scatter.png"))

    master.to_csv(os.path.join(OUTPUT_DIR, "master_profitability_table.csv"), index=False)
    print(f"\nMaster profitability table saved to outputs/master_profitability_table.csv")

if __name__ == "__main__":
    analyze_advanced_correlation()

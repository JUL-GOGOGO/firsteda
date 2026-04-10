import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from config import DATA_DIR, DATASETS, IMAGE_DIR, OUTPUT_DIR

def perform_roi_analysis():
    print("\n" + "="*50)
    print("Step 8: ROI Analysis & Strategic Recommendation")
    print("="*50)

    # 1. Load Revenue Data
    df_rev = pd.read_csv(os.path.join(OUTPUT_DIR, "usage_revenue.csv"))
    
    # 2. B2B / B2C Segmentation
    # B2B: High frequency users (>= 5 sessions in sample) or specific Org Names
    user_counts = df_rev['User ID'].value_counts()
    b2b_users = user_counts[user_counts >= 5].index
    
    b2b_orgs = ['University', 'Corporate', 'Work', 'Office', 'Enterprise']
    
    def classify_channel(row):
        if row['User ID'] in b2b_users:
            return 'B2B'
        if any(org in str(row['State/Province']) for org in b2b_orgs): # State/Province column had Org data in audit
            return 'B2B'
        return 'B2C'

    df_rev['Channel'] = df_rev.apply(classify_channel, axis=1)

    # 3. Revenue Metrics by Channel
    channel_stats = df_rev.groupby('Channel').agg({
        'Calculated_Revenue': ['sum', 'mean', 'count'],
        'Energy_Numeric': 'mean'
    }).reset_index()
    channel_stats.columns = ['Channel', 'Total_Revenue', 'AOV', 'Session_Count', 'Avg_kWh']

    # 4. ROI Calculation (Capex Assumptions)
    # B2B: Mostly L2, B2C: Blend of L2/L3
    capex_per_port = {
        'B2B': 5000,  # $5k for L2 office installation
        'B2C': 15000  # $15k blend for public/fast charging
    }
    
    # Assume 1 port can handle N sessions in the period
    # To simplify, we look at Revenue per Port ROI
    channel_stats['Assumed_Capex'] = channel_stats['Channel'].map(capex_per_port)
    # ROI = Total_Revenue / (Port_Count * Capex)
    # We don't have port count, so we calculate "Revenue as % of Capex per session efficiency"
    # Actually, let's calculate Monthly ROI if we assume 30 sessions/month per port
    sessions_per_month = 60 # 2 per day
    channel_stats['Est_Monthly_Revenue'] = channel_stats['AOV'] * sessions_per_month
    channel_stats['Monthly_ROI_Pct'] = (channel_stats['Est_Monthly_Revenue'] / channel_stats['Assumed_Capex']) * 100

    print("\nROI Metrics by Channel:")
    print(channel_stats)

    # 5. 시각화
    # Channel ROI Comparison
    plt.figure(figsize=(10, 6))
    plt.bar(channel_stats['Channel'], channel_stats['Monthly_ROI_Pct'], color=['#4C72B0', '#55A868'])
    plt.title('Estimated Monthly ROI (%) by Channel')
    plt.ylabel('ROI (%)')
    plt.savefig(os.path.join(IMAGE_DIR, "channel_roi_comparison.png"))

    # 6. 최종 투자 매트릭스 재료 (State별 ROI 추정)
    df_master = pd.read_csv(os.path.join(OUTPUT_DIR, "master_profitability_table.csv"))
    # ROI Score = (AOV * Elec_Price) / Avg_Density
    # States with low EV Count but high Elec_Price and high AOV are high priority
    df_master['ROI_Score'] = (df_master['AOV'] + df_master['Elec_Price']) / (df_master['EV_Count'] + 1)
    # Normalize for 0-100 score
    df_master['Priority_Score'] = (df_master['ROI_Score'] / df_master['ROI_Score'].max()) * 100
    
    top_priority = df_master.sort_values('Priority_Score', ascending=False).head(10)
    print("\nTop 10 Priority States for Investment:")
    print(top_priority[['State_Full', 'Priority_Score', 'EV_Count', 'Elec_Price']])

    channel_stats.to_csv(os.path.join(OUTPUT_DIR, "channel_roi_stats.csv"), index=False)
    top_priority.to_csv(os.path.join(OUTPUT_DIR, "investment_priority.csv"), index=False)

if __name__ == "__main__":
    import numpy as np
    perform_roi_analysis()

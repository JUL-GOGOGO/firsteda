import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# 스타일 설정: seaborn 스타일 금지, matplotlib 기본 사용
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.unicode_minus'] = False

def save_plot(name):
    # Ensure images directory exists
    if not os.path.exists('firsteda/images/'):
        os.makedirs('firsteda/images/')
    path = os.path.join('firsteda/images/', name)
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")

def visualize():
    data_dir = 'firsteda/data/'
    
    # 1. State-wise EV Population (Electric_Vehicle_Population_Data)
    df_pop = pd.read_parquet(os.path.join(data_dir, 'Electric_Vehicle_Population_Data.parquet'))
    state_counts = df_pop['State'].value_counts()
    
    plt.figure(figsize=(15, 6))
    state_counts.head(20).plot(kind='bar', color='skyblue')
    plt.title('Top 20 States by EV Population')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    save_plot('ev_population_top20.png')

    plt.figure(figsize=(15, 6))
    state_counts.tail(20).sort_values().plot(kind='bar', color='orange')
    plt.title('Bottom 20 States by EV Population (Target States)')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    save_plot('ev_population_bottom20.png')

    # 2. Charging Patterns (ev_charging_patterns)
    df_patterns = pd.read_parquet(os.path.join(data_dir, 'ev_charging_patterns.parquet'))
    
    # Day of Week Frequency
    plt.figure()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_patterns['Day of Week'].value_counts().reindex(day_order).plot(kind='bar', color='teal')
    plt.title('Charging Frequency by Day of Week')
    plt.ylabel('Sessions')
    save_plot('charging_frequency_by_day.png')

    # Energy Distribution
    plt.figure()
    df_patterns['Energy Consumed (kWh)'].hist(bins=30, color='coral', edgecolor='black')
    plt.title('Energy Consumed Distribution (kWh)')
    plt.xlabel('Energy (kWh)')
    plt.ylabel('Frequency')
    save_plot('energy_distribution.png')

    # 3. Hourly Peak (caltech_acn_data_2018_2020)
    df_caltech = pd.read_parquet(os.path.join(data_dir, 'caltech_acn_data_2018_2020.parquet'))
    df_caltech['connectionTime'] = pd.to_datetime(df_caltech['connectionTime'])
    df_caltech['hour'] = df_caltech['connectionTime'].dt.hour
    
    plt.figure()
    df_caltech['hour'].value_counts().sort_index().plot(kind='line', marker='o', color='purple')
    plt.title('Hourly Charging Session Count (Peak Identification)')
    plt.xlabel('Hour')
    plt.ylabel('Sessions')
    plt.grid(True, linestyle='--', alpha=0.6)
    save_plot('hourly_charging_peak.png')

    # 4. Weather Impact (ev-charging-forecasting-with-weather-data-LA)
    df_weather = pd.read_parquet(os.path.join(data_dir, 'ev-charging-forecasting-with-weather-data-LA.parquet'))
    
    plt.figure(figsize=(12, 6))
    weather_counts = df_weather['weather_conditions'].value_counts()
    weather_counts.plot(kind='barh', color='gray')
    plt.title('Charging Sessions by Weather Condition (LA)')
    plt.xlabel('Sessions')
    save_plot('weather_session_distribution.png')

if __name__ == "__main__":
    visualize()

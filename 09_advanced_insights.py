import pandas as pd
import os
from config import DATA_DIR, DATASETS, OUTPUT_DIR

def analyze_weather_and_demand():
    print("\n" + "="*50)
    print("Step 9: Weather-based Demand Analysis")
    print("="*50)

    # 1. Load Weather Data
    df_w = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['weather_la']))
    
    # 2. Weather Conditions vs Avg kWh
    weather_avg = df_w.groupby('weather_conditions')['kWhDelivered'].agg(['mean', 'count', 'std']).reset_index()
    weather_avg.columns = ['Condition', 'Avg_kWh', 'Session_Count', 'Std_kWh']
    
    # 3. Categorize Weather (Good vs Bad)
    bad_weather = ['Rain', 'Fog', 'Mist', 'Thunderstorm', 'Drizzle', 'Snow']
    df_w['Weather_Type'] = df_w['weather_conditions'].apply(lambda x: 'Bad' if x in bad_weather else 'Good')
    
    weather_type_avg = df_w.groupby('Weather_Type')['kWhDelivered'].agg(['mean', 'median', 'count']).reset_index()
    
    # 4. Hourly Demand Pattern
    hourly_avg = df_w.groupby('departure_hour')['kWhDelivered'].mean().reset_index()
    
    print("\nWeather Condition Insights:")
    print(weather_avg)
    
    print("\nWeather Type Insights (Good vs Bad):")
    print(weather_type_avg)

    # 5. 결과 저장
    weather_avg.to_csv(os.path.join(OUTPUT_DIR, "weather_insights.csv"), index=False)
    hourly_avg.to_csv(os.path.join(OUTPUT_DIR, "hourly_weather_demand.csv"), index=False)
    
    print(f"\nAdvanced insights saved to outputs/ (weather_insights.csv, hourly_weather_demand.csv)")

if __name__ == "__main__":
    analyze_weather_and_demand()

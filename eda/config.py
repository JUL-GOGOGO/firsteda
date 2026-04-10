import os

# 파일 경로 관련 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGE_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# 디렉토리 생성
for dir_path in [IMAGE_DIR, OUTPUT_DIR, REPORT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# 데이터셋 목록
DATASETS = {
    "caltech": "caltech_acn_data_2018_2020.parquet",
    "ev_pop_detail": "Electric_Vehicle_Population_Data.parquet",
    "charging_patterns": "ev_charging_patterns.parquet",
    "station_locations": "ev_data.csv",
    "state_ev_pop": "EV_Population.parquet",
    "weather_la": "ev-charging-forecasting-with-weather-data-LA.parquet",
    "station_usage": "EVChargingStationUsage.parquet",
    "elec_price": "table_4(Table 4).csv"
}

# 시각화 설정 (koreanize-matplotlib는 스크립트에서 임포트)
import matplotlib.pyplot as plt
try:
    import koreanize_matplotlib
except ImportError:
    print("Warning: koreanize_matplotlib not found. Korean fonts may not be displayed correctly in plots.")

plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.unicode_minus'] = False

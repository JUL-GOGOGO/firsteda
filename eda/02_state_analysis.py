import pandas as pd
import os
import matplotlib.pyplot as plt
from config import DATA_DIR, DATASETS, IMAGE_DIR, OUTPUT_DIR

def analyze_states():
    print("\n" + "="*50)
    print("Step 2: State Analysis & Low-Adoption Candidate Identification")
    print("="*50)

    # 1. State 명칭 통일성 확인
    files_with_state = {
        "ev_pop_detail": "State",
        "station_locations": "state",
        "state_ev_pop": "State",
        "station_usage": "State/Province",
        "elec_price": "State"
    }

    state_variants = {}
    for name, col in files_with_state.items():
        full_path = os.path.join(DATA_DIR, DATASETS[name])
        if DATASETS[name].endswith('.parquet'):
            df = pd.read_parquet(full_path)
        else:
            if name == "elec_price":
                df = pd.read_csv(full_path, skiprows=2)
            else:
                df = pd.read_csv(full_path)
        
        # State 컬럼의 유니크값 확인
        states = df[col].dropna().unique()
        state_variants[name] = sorted(list(states))
        print(f"File '{name}' states: {len(states)} unique values. Sample: {states[:5]}")

    # 2. EV 등록 수 기준 State별 순위 (ev_pop_detail 사용)
    # 참고: ev_pop_detail은 상세 등록 데이터이므로 행 수가 등록 대수와 비례함
    df_pop = pd.read_parquet(os.path.join(DATA_DIR, DATASETS['ev_pop_detail']))
    state_counts = df_pop['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'EV_Count']

    # 상위/하위 5개 출력
    print("\nTop 5 States by EV Population (in this dataset):")
    print(state_counts.head(5))
    print("\nBottom 5 States by EV Population (in this dataset):")
    print(state_counts.tail(5))

    # 하위 20% 추출
    threshold = state_counts['EV_Count'].quantile(0.2)
    low_adoption_states = state_counts[state_counts['EV_Count'] <= threshold].copy()
    low_adoption_states['Status'] = 'Low-Adoption Candidate'
    
    print(f"\nidentified {len(low_adoption_states)} Low-Adoption Candidate States (Bottom 20%, threshold: {threshold:.1f} vehicles)")
    print(low_adoption_states[['State', 'EV_Count']])

    # 3. 시각화
    plt.figure(figsize=(15, 8))
    # 상위 20개만 시각화 (너무 많으면 안보임)
    top_20 = state_counts.head(20)
    plt.bar(top_20['State'], top_20['EV_Count'], color='skyblue')
    plt.title('Top 20 States by EV Population')
    plt.xlabel('State')
    plt.ylabel('EV Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, "state_ev_distribution.png"))
    print(f"\nChart saved to images/state_ev_distribution.png")

    # 결과 저장
    low_adoption_states.to_csv(os.path.join(OUTPUT_DIR, "low_adoption_states.csv"), index=False)
    
    return low_adoption_states

if __name__ == "__main__":
    analyze_states()

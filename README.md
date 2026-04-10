# ⚡ EV 충전 전략 데이터 분석 프로젝트

![Project Hero Image](images/hero_image.png)

## 📊 EV Charging Revenue Strategy for Low-Adoption States

---

## 🚀 Project Overview

본 프로젝트는 대규모 충전 세션 로그, EV 등록 현황, 전기 요금 등의 데이터를 통합 분석하여 **"저보급 지역에서도 수익을 낼 수 있는 최적의 지점과 채널은 어디인가?"**라는 질문에 대한 답을 제시합니다.

### 🎯 핵심 목표
- **북극성 지표(NSM)**: 저보급 State 내 월간 충전 세션 매출 총액 극대화
- **채널 전략**: 고ARPU를 창출하는 B2B(법인/기관) 및 고단가 B2C(일반/급속) 채널 차별화
- **의사결정 도구**: 전략 수립을 지원하는 인터랙티브 ROI 시뮬레이터 대시보드 구축

---

## 📊 Key Insights & Analytics

- **데이터 기반 주(State) 탐색**: 하위 20% EV 보급 지역(16개 주) 중 높은 전력 단가를 보유한 전략적 요충지(RI, VT 등) 식별.
- **수익성 모델링**: 세션당 평균 매출(AOV) $3.43 도출 및 B2B 고객의 충성도(ARPU $174.3) 입증.
- **ROI 시뮬레이션**: 하드웨어 가상 Capex 대비 채널별 예상 수익률(2.7%~3.8%) 시뮬레이션 완료.
- **기상 상관관계**: 기상 악화 시 평균 충전량(kWh)이 증가하는 패턴 발견을 통해 시즌별 탄력 가격제 전략 제언.

---

## 🖥️ Dashboard (Streamlit)

본 저장소에 포함된 `app.py`를 실행하여 분석 결과를 인터랙티브하게 탐색할 수 있습니다.

### 주요 기능
- **State Heatmap**: 미국 전역 EV 보급 및 인프라 현황 지도
- **What-if Simulator**: 설치비, 세션 수 등을 조절하여 실시간 ROI 및 투자 회수 기간 예측
- **Strategic Matrix**: 전력 단가와 보급률에 따른 지역별 투자 우선순위 제시

### 실행 방법
```bash
# 의존성 설치
pip install -r requirements.txt

# 대시보드 실행
streamlit run app.py
```

---

## 📂 Repository Structure

- `app.py`: Streamlit 대시보드 메인
- `eda/`: 01~09번 분석 및 시뮬레이션 소스 코드
- `outputs/`: 분석 결과 정제 데이터 (CSV)
- `images/`: 상관관계 히트맵 및 분석 시각화 결과
- `reports/`: 전략 프레임워크 및 최종 ROI 보고서 (Markdown)
- `config.py`: 데이터 경로 및 환경 설정

---

## 🛠️ Technology Stack
- **Languages**: Python (3.13+)
- **Analysis**: Pandas, PyArrow, NumPy
- **Visualization**: Plotly, Matplotlib
- **Framework**: Streamlit

---
**Author**: Antigravity Strategic Intelligence Unit (Internal Demo)

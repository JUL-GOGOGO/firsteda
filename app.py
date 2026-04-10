import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="EV Strategy Advanced Dashboard",
    page_icon="⚡",
    layout="wide",
)

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "outputs")
IMAGE_DIR = os.path.join(BASE_DIR, "images")

# --- 데이터 로딩 함수 (캐싱) ---
@st.cache_data
def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.error(f"데이터 파일 읽기 오류: {filename} - {e}")
            return None
    else:
        st.warning(f"데이터 파일을 찾을 수 없습니다: {path}")
    return None

# 사이드바 구성
st.sidebar.title("⚡ EV 충전 전략")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["프로젝트 개요", "주(State) 탐색", "수익성 분석", "전략 시뮬레이터"]
)

st.sidebar.markdown("---")
st.sidebar.info("v2.0: 시뮬레이터 및 기상 분석 통합 버전")

# --- Menu: 프로젝트 개요 ---
if menu == "프로젝트 개요":
    st.title("🚀 프로젝트 전략 프레임워크")
    
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("대상 주(State) 수", "16", "하위 20%")
        c2.metric("평균 AOV", "$3.43", "추정치")
        c3.metric("B2B ARPU", "$174.3", "충성 고객")
        c4.metric("최대 ROI", "3.8%", "B2C 채널")

    # NSM & Funnel
    with st.expander("📌 북극성 지표(NSM) 및 퍼널 정의", expanded=True):
        st.success("**NSM: 저보급 State 내 월간 충전 세션 매출 총액 극대화**")
        st.markdown("""
        - **인지(Awareness)**: 거점(POI) 포트폴리오 노면 노출
        - **방문(Visit)**: 고유 차량 스테이션 방문 (Unique Users)
        - **충전(Charge)**: 실제 충전 세션 전환율 및 이용률
        - **재방문(Revisit)**: LTV 및 유지율 (Retention, 2회 이상 방문)
        """)

    st.markdown("### 🔗 전략적 엔티티 관계도 (상관관계)")
    st.image(os.path.join(IMAGE_DIR, "state_correlation_heatmap.png"), use_container_width=True)

# --- Menu: 주(State) 탐색 ---
elif menu == "주(State) 탐색":
    st.title("🗺️ 저보급 State 탐색 및 발견")
    
    df_master = load_data("master_profitability_table.csv")
    if df_master is not None:
        # Interactive Map
        fig = px.choropleth(
            df_master,
            locations="State_Abbr",
            locationmode="USA-states",
            color="EV_Count",
            hover_name="State_Full",
            scope="usa",
            color_continuous_scale="Viridis",
            title="미국 주별 EV 보급 현황 히트맵"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col_list, col_ratio = st.columns([1, 1])
        with col_list:
            st.markdown("#### 📍 저보급 후보군 (하위 20%)")
            df_low = load_data("low_adoption_states.csv")
            st.dataframe(df_low[['State', 'EV_Count']].head(10), use_container_width=True)
        
        with col_ratio:
            st.markdown("#### 전력 단가 vs EV 보급수")
            fig_bub = px.scatter(
                df_master[df_master['EV_Count'] > 0],
                x="EV_Count", y="Elec_Price",
                size="Station_Count", color="Total_Revenue",
                hover_name="State_Full", text="State_Abbr",
                log_x=True, title="전략적 포지셔닝 매트릭스"
            )
            st.plotly_chart(fig_bub, use_container_width=True)

# --- Menu: 수익성 분석 ---
elif menu == "수익성 분석":
    st.title("💰 수익성 및 매출 인사이트")
    
    tabs = st.tabs(["AOV 분포", "상관관계 분석", "채널별 ROI"])
    
    with tabs[0]:
        st.image(os.path.join(IMAGE_DIR, "aov_distribution.png"))
        st.info("대부분의 세션이 $5 미만에서 발생하며, $10 이상의 프리미엄 세션 비중 확대가 주요 과제입니다.")
        
    with tabs[1]:
        st.markdown("#### 가중 상관관계 분석 (EV 보급수 기준)")
        st.table(pd.DataFrame({
            "지표 그룹": ["EV vs 인프라", "단가 vs 매출", "인프라 vs 단가"],
            "상관계수": [0.97, 0.90, 0.94],
            "강도": ["매우 강함", "강함", "강함"]
        }))

    with tabs[2]:
        st.image(os.path.join(IMAGE_DIR, "channel_roi_comparison.png"))
        st.success("B2C의 단기 ROI가 높지만, B2B의 고정 수요를 통한 안정적 수익 구조 확보가 병행되어야 합니다.")

# --- Menu: 전략 시뮬레이터 ---
elif menu == "전략 시뮬레이터":
    st.title("🎮 What-if ROI 시뮬레이터")
    
    st.sidebar.markdown("### ⚙️ 시뮬레이션 파라미터")
    target_state = st.sidebar.selectbox("대상 주(State) 선택", ["Rhode Island", "Vermont", "Connecticut", "Maine", "Alaska"])
    
    # 입력 파라미터
    n_ports = st.sidebar.slider("충전기(포트) 수", 1, 20, 5)
    capex_per_port = st.sidebar.number_input("포트당 설치 비용 ($)", 2000, 50000, 10000)
    avg_sessions_day = st.sidebar.slider("포트당 일일 평균 세션", 0.5, 5.0, 2.0)
    fee_per_kwh = st.sidebar.slider("충전 요금 ($/kWh)", 0.20, 1.00, 0.45)
    avg_kwh = st.sidebar.number_input("세션당 평균 충전량 (kWh)", 5.0, 50.0, 15.0)
    
    # 계산 로직
    monthly_sessions = n_ports * avg_sessions_day * 30
    monthly_rev = monthly_sessions * avg_kwh * fee_per_kwh
    total_capex = n_ports * capex_per_port
    
    # 운영비 (가정: 매출의 20% + 포트당 유지비 $100)
    monthly_opex = (monthly_rev * 0.2) + (n_ports * 100)
    monthly_profit = monthly_rev - monthly_opex
    
    annual_roi = (monthly_profit * 12 / total_capex) * 100
    payback_months = total_capex / monthly_profit if monthly_profit > 0 else 999
    
    # 결과 출력
    col1, col2, col3 = st.columns(3)
    col1.metric("예상 월 순이익", f"${monthly_profit:,.0f}")
    col2.metric("예상 연간 ROI", f"{annual_roi:.1f}%")
    col3.metric("투자금 회수 기간", f"{payback_months:.1f} 개월")
    
    st.markdown("---")
    st.markdown("### 🌦️ 기상 기반 수요 예측 (LA 데이터 기반 인사이트)")
    df_weather = load_data("weather_insights.csv")
    if df_weather is not None:
        fig_w = px.bar(
            df_weather, x="Condition", y="Avg_kWh",
            color="Avg_kWh", title="기상 조건별 평균 충전량"
        )
        st.plotly_chart(fig_w, use_container_width=True)
        st.caption("※ 기상 악화 시 충전 효율 감소 및 차량 내 온도 조절 등으로 인해 평균 충전량이 증가하는 경향을 보입니다.")

    # 결과 다운로드
    sim_res = pd.DataFrame([{
        "주(State)": target_state, "포트수": n_ports, "투자비": total_capex, 
        "월이익": monthly_profit, "ROI": annual_roi, "회수기간": payback_months
    }])
    st.download_button("시뮬레이션 결과 다운로드 (CSV)", sim_res.to_csv(index=False), "sim_result_kr.csv", "text/csv")

# Footer
st.markdown("---")
st.caption("© 2026 Antigravity Strategic Intelligence Unit")

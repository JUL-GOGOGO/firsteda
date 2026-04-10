# EV 충전 매출 극대화 전략 종합 EDA 보고서

본 보고서는 미국 내 EV 저보급 State의 충전 매출 극대화 전략 수립을 위해 8개의 데이터셋을 분석한 결과입니다.

---

## 1. 데이터셋 인벤토리 및 ERD 설계 재료

### 📊 파일별 핵심 지표
| 파일명 | 주요 용도 | 핵심 컬럼 (PK/FK/Keys) |
|---|---|---|
| `caltech` | 세션 로그 분석 | `sessionID`(PK), `stationID`, `userID`, `kWhDelivered` |
| `station_usage` | CA 지역 이용 패턴 | `MAC Address`, `Energy (kWh)`, `Fee`, `State/Province` |
| `ev_pop_detail` | State별 EV 보급 현황 | `State`, `VIN (1-10)`, `Model Year`, `DOL Vehicle ID` |
| `station_locations` | 충전소 POI 데이터 | `state`, `latitude`, `longitude`, `total_kw` |
| `elec_price` | 지역별 수익성 분석 | `State`, `Residential`, `Commercial`, `Total` (단가) |

### 🔗 데이터 조인 맵
- **State 기준**: `ev_pop_detail.State` ↔ `elec_price.State` ↔ `station_locations.state` (명칭 표준화 필요)
- **사용자 기준**: `caltech.userID` ↔ `station_usage.User ID` (매칭 가능성 낮으나 개별 패턴 분석 가능)
- **충전소 기준**: `station_locations` ↔ `station_usage.Station Name` (Fuzzy matching 필요)

---

## 2. KPI Tree 및 NSM 측정 가용성

### 📈 매출 지표 (AOV = 충전 단가 × kWh)
- **측정 가능성**: ✅ **높음**
- **방법**:
  - `station_usage`의 `Fee` 컬럼 직접 활용.
  - `caltech`의 `kWhDelivered`와 `elec_price`의 State별 단가 조인하여 세션별 예상 매출 계산.
- **Proxy 제안**: 단가 데이터가 없는 세션은 해당 State의 'Commercial' 전력 단가를 기준(Proxy)으로 설정.

### 👥 B2B vs B2C 구분
- **방법**: 
  - `charging_patterns`의 `User Type` (Commuter=B2C, Commercial=B2B 가능성) 활용.
  - `station_usage`의 `Org Name` (City, Private, Univ 등)으로 채널 구분 가능.
- **Proxy**: 주중/근무시간 집중 충전 세션을 B2B로, 야간/주말 세션을 B2C로 분류.

### 🌪️ 퍼널 분석 가용성
- **인지**: ❌ 데이터 없음 (마케팅 지표 부재)
- **방문/충전**: ✅ 데이터 풍부 (충전소 POI 및 세션 로그)
- **재방문**: 🔶 조건부 (User ID가 있는 데이터셋에서 반복 방문 횟수 측정 가능)

---

## 3. 저보급 State 후보군 분석

`ev_pop_detail` 데이터 기반, EV 등록 수가 현저히 낮은 하위 20% State를 선정했습니다.

**📍 선정된 저보급 State 후보 (Top 5):**
1. **AK** (Alaska)
2. **DE** (Delaware)
3. **NH** (New Hampshire)
4. **MT** (Montana)
5. **MS** (Mississippi)
*※ 참고: 본 데이터셋은 WA(워싱턴)주 데이터 의존도가 매우 높으므로, 타 State 분석 시 POI 데이터와 병행 검토 필요.*

---

## 4. 충전 패턴 및 상관관계

### 🕒 주요 충전 패턴
- **Peak Time**: Afternoon(오후) 시간대에 세션 집중.
- **Weekdays**: 월요일과 금요일의 빈도가 높으며, 주말로 갈수록 소폭 감소.

### 🔗 주요 상관계수 (State Level)
- **Station Count ↔ Avg Price**: **0.44** (중간 정도의 양의 상관관계)
  - 전기 단가가 높은 지역이 충전소 인프라도 더 잘 구축되어 있는 경향을 보임.
- **EV Count ↔ Station Count**: **-0.05** (본 데이터셋 한계로 상관관계 낮음)

---

## 5. 전처리 이슈 및 권장 전략

> [!WARNING]
> **핵심 전처리 과제**
> 1. **State 명칭 통일**: 약어('CA')와 전체 이름('California')이 혼용되고 있어 조인 전 표준화 필수.
> 2. **수치형 변환**: `station_usage`의 `Energy (kWh)` 등 카테고리/오브젝트 타입 컬럼의 Numeric 변환 필요.
> 3. **이상값 처리**: kWhDeliverd 값이 100을 초과하는 상위 1.7% 이상값에 대한 정제(Capping) 전략 필요.
> 4. **좌표 이상**: `station_usage`의 `State/Province` 컬럼에 위경도 값이 섞여 있는 데이터 오염 확인됨.

---

## 🚀 다음 단계 최적화 제안
- **매출 극대화 전략**: `Avg_Price`가 높고 `Station_Count`가 적은 저보급 State(예: AK, MT)를 타깃으로 고단가 프리미엄 충전 서비스 배치 고려.
- **B2B 확장**: `station_usage`의 `Org Name` 분석을 통해 공공기관 외 민간 사업자 비중이 낮은 State 식별.

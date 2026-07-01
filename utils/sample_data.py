"""데모용 샘플 데이터 생성 모듈.

모든 함수는 @st.cache_data 로 감싸 한 번 계산한 결과를 재사용한다.
외부 파일·네트워크 없이 완결되므로 로컬·배포 환경 모두에서 동일하게 동작한다.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

REGIONS = ["서울", "경기", "부산", "대구", "광주", "대전"]
PRODUCTS = {
    "노트북": "전자기기",
    "스마트폰": "전자기기",
    "이어폰": "액세서리",
    "키보드": "액세서리",
    "모니터": "전자기기",
    "충전기": "액세서리",
}


@st.cache_data
def sales_data() -> pd.DataFrame:
    """15개월치 일별 매출 거래 데이터를 만든다."""
    rng = np.random.default_rng(42)
    start = date.today() - timedelta(days=450)
    days = pd.date_range(start, periods=450, freq="D")

    rows = []
    for d in days:
        # 요일·월별 계절성을 살짝 반영
        base = 18 + 6 * np.sin(d.month / 12 * 2 * np.pi)
        weekend_boost = 1.25 if d.weekday() >= 5 else 1.0
        n_orders = int(rng.poisson(base * weekend_boost))
        for _ in range(n_orders):
            product = rng.choice(list(PRODUCTS.keys()))
            unit_price = {
                "노트북": 1_450_000,
                "스마트폰": 1_150_000,
                "모니터": 320_000,
                "이어폰": 190_000,
                "키보드": 89_000,
                "충전기": 39_000,
            }[product]
            qty = int(rng.integers(1, 4))
            rows.append(
                {
                    "날짜": d,
                    "지역": rng.choice(REGIONS, p=[0.34, 0.26, 0.14, 0.1, 0.08, 0.08]),
                    "제품": product,
                    "분류": PRODUCTS[product],
                    "수량": qty,
                    "매출": unit_price * qty,
                }
            )
    return pd.DataFrame(rows)


@st.cache_data
def employee_data() -> pd.DataFrame:
    """직원 명부 형태의 탐색용 데이터를 만든다."""
    rng = np.random.default_rng(7)
    depts = ["영업", "개발", "디자인", "마케팅", "인사", "재무"]
    roles = ["사원", "대리", "과장", "차장", "부장"]
    surnames = list("김이박최정강조윤장임")
    givens = ["민준", "서연", "도윤", "지우", "하준", "서윤", "예준", "지호", "수아", "지안"]

    n = 120
    df = pd.DataFrame(
        {
            "이름": [rng.choice(surnames) + rng.choice(givens) for _ in range(n)],
            "부서": rng.choice(depts, n),
            "직급": rng.choice(roles, n, p=[0.4, 0.25, 0.18, 0.1, 0.07]),
            "근속연수": rng.integers(0, 18, n),
            "연봉": (rng.normal(5200, 1400, n)).round(-2).clip(3000, 12000).astype(int),
            "평가점수": (rng.normal(78, 10, n)).round(1).clip(40, 100),
            "재택비율": rng.integers(0, 101, n),
        }
    )
    return df


@st.cache_data
def geo_points() -> pd.DataFrame:
    """전국 주요 도시 주변에 흩뿌린 지점 좌표를 만든다."""
    rng = np.random.default_rng(11)
    centers = {
        "서울": (37.5665, 126.9780),
        "부산": (35.1796, 129.0756),
        "대구": (35.8714, 128.6014),
        "인천": (37.4563, 126.7052),
        "광주": (35.1595, 126.8526),
        "대전": (36.3504, 127.3845),
        "울산": (35.5384, 129.3114),
        "제주": (33.4996, 126.5312),
    }
    rows = []
    for city, (lat, lon) in centers.items():
        for _ in range(int(rng.integers(6, 20))):
            rows.append(
                {
                    "도시": city,
                    "lat": lat + rng.normal(0, 0.05),
                    "lon": lon + rng.normal(0, 0.05),
                    "월매출": int(rng.integers(30, 300)),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data
def fx_fallback() -> pd.DataFrame:
    """환율 API 실패 시 사용할 원/달러 대체 시계열."""
    rng = np.random.default_rng(3)
    days = pd.date_range(date.today() - timedelta(days=180), periods=180, freq="D")
    walk = 1330 + np.cumsum(rng.normal(0, 4, len(days)))
    return pd.DataFrame({"날짜": days, "환율": walk.round(2)})

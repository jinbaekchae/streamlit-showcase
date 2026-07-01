"""데모용 현실감 합성 데이터.

가상의 이커머스 브랜드 '오렌지마켓'을 기준으로, 계절성·프로모션·채널·이익률이
반영된 데이터를 생성한다. 실제 기업·개인 정보와 무관한 완전 합성 데이터이며,
모든 함수는 @st.cache_data 로 감싸 한 번만 계산한다.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# ── 제품 카탈로그 (가상) ─────────────────────────────
# 제품: (분류, 단가, 계절가중 키)
CATALOG = {
    "무선청소기": ("가전", 299000, "q4"),
    "공기청정기": ("가전", 359000, "winter"),
    "에어프라이어": ("가전", 129000, "q4"),
    "노트북": ("디지털", 1290000, "q4"),
    "태블릿": ("디지털", 690000, "flat"),
    "스마트워치": ("디지털", 329000, "flat"),
    "블루투스이어폰": ("디지털", 159000, "flat"),
    "겨울패딩": ("패션", 189000, "winter"),
    "니트": ("패션", 59000, "winter"),
    "스니커즈": ("패션", 89000, "spring"),
    "백팩": ("패션", 79000, "spring"),
    "수분세럼": ("뷰티", 38000, "flat"),
    "선크림": ("뷰티", 24000, "summer"),
    "립밤": ("뷰티", 12000, "winter"),
    "원두커피": ("식품", 18900, "flat"),
    "견과세트": ("식품", 29900, "q4"),
    "디퓨저": ("리빙", 22000, "flat"),
    "무드등": ("리빙", 39000, "winter"),
}
MARGIN = {"가전": 0.18, "디지털": 0.12, "패션": 0.45, "뷰티": 0.55, "식품": 0.30, "리빙": 0.42}
CHANNELS = ["온라인", "오프라인", "제휴몰"]
REGIONS = ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "기타"]
REGION_P = [0.27, 0.24, 0.09, 0.12, 0.08, 0.06, 0.05, 0.09]

PRODUCTS = list(CATALOG.keys())
P_CAT = np.array([CATALOG[p][0] for p in PRODUCTS])
P_PRICE = np.array([CATALOG[p][1] for p in PRODUCTS])
P_SEASON = [CATALOG[p][2] for p in PRODUCTS]


def _season_weight(month: int, key: str) -> float:
    """월별 계절 가중치."""
    if key == "flat":
        return 1.0
    if key == "winter":
        return 1.9 if month in (11, 12, 1, 2) else 0.6
    if key == "summer":
        return 2.0 if month in (6, 7, 8) else 0.6
    if key == "spring":
        return 1.6 if month in (3, 4, 5, 9) else 0.85
    if key == "q4":
        return 1.8 if month in (10, 11, 12) else 0.9
    return 1.0


@st.cache_data
def sales_data() -> pd.DataFrame:
    """약 15개월치 주문 단위 매출 데이터."""
    rng = np.random.default_rng(42)
    start = date.today() - timedelta(days=455)
    days = pd.date_range(start, periods=455, freq="D")

    # 프로모션일: 매월 11일(오렌지데이) + 블랙프라이데이 주간
    promo_days = set()
    for d in days:
        if d.day == 11:
            promo_days.add(d.normalize())
        if d.month == 11 and 24 <= d.day <= 30:
            promo_days.add(d.normalize())

    frames = []
    for i, d in enumerate(days):
        trend = 1.0 + 0.10 * (i / len(days))  # 완만한 성장
        season = 1.0 + 0.18 * np.sin((d.month - 3) / 12 * 2 * np.pi)
        weekday = 1.25 if d.weekday() >= 5 else 1.0
        is_promo = d.normalize() in promo_days
        promo_mult = 2.1 if is_promo else 1.0
        base = 34 * trend * season * weekday * promo_mult
        n = int(rng.poisson(base))
        if n == 0:
            continue

        w = np.array([_season_weight(d.month, k) for k in P_SEASON])
        w = w / w.sum()
        idx = rng.choice(len(PRODUCTS), size=n, p=w)

        cat = P_CAT[idx]
        price = P_PRICE[idx]
        qty = rng.choice([1, 1, 1, 2, 2, 3], size=n)
        base_disc = rng.choice([0.0, 0.0, 0.05, 0.1, 0.15], size=n)
        disc = np.clip(base_disc + (0.2 if is_promo else 0.0), 0, 0.5)
        revenue = np.round(price * qty * (1 - disc), -2).astype(int)
        margin = np.array([MARGIN[c] for c in cat])
        profit = np.round(revenue * margin).astype(int)

        frames.append(
            pd.DataFrame(
                {
                    "날짜": d,
                    "시": rng.integers(8, 24, n),
                    "채널": rng.choice(CHANNELS, n, p=[0.55, 0.30, 0.15]),
                    "지역": rng.choice(REGIONS, n, p=REGION_P),
                    "분류": cat,
                    "제품": np.array(PRODUCTS)[idx],
                    "수량": qty,
                    "단가": price,
                    "할인율": np.round(disc, 2),
                    "매출": revenue,
                    "이익": profit,
                    "고객유형": rng.choice(["신규", "재구매"], n, p=[0.42, 0.58]),
                    "반품": rng.random(n) < 0.03,
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


@st.cache_data
def employee_data() -> pd.DataFrame:
    """현실적인 조직 구성의 직원 명부 (가상 인물)."""
    rng = np.random.default_rng(7)
    depts = {
        "영업": ["국내영업", "해외영업"],
        "마케팅": ["퍼포먼스", "브랜드"],
        "개발": ["백엔드", "프론트엔드", "플랫폼"],
        "디자인": ["프로덕트", "브랜드"],
        "데이터": ["분석", "ML"],
        "인사": ["채용", "운영"],
        "재무": ["회계", "자금"],
        "고객경험": ["CS", "품질"],
    }
    levels = ["L1", "L2", "L3", "L4", "L5"]
    titles = {"L1": "사원", "L2": "선임", "L3": "책임", "L4": "수석", "L5": "리드"}
    base_salary = {"L1": 3600, "L2": 4600, "L3": 6000, "L4": 7800, "L5": 9800}
    grades = ["S", "A", "B", "C"]
    locs = ["서울", "판교", "부산", "원격"]
    surnames = list("김이박최정강조윤장임한오서신권황")
    givens = ["민준", "서연", "도윤", "지우", "하준", "서윤", "예준", "지호", "수아",
              "지안", "준우", "하은", "시우", "유진", "연우", "지민", "채원", "현우"]

    n = 140
    lvl = rng.choice(levels, n, p=[0.34, 0.28, 0.2, 0.12, 0.06])
    dept = rng.choice(list(depts.keys()), n)
    team = [rng.choice(depts[d]) for d in dept]
    tenure = np.round(rng.gamma(2.2, 1.7, n), 1).clip(0.2, 16)
    salary = np.array(
        [base_salary[l] * (1 + 0.03 * t) * rng.normal(1, 0.06) for l, t in zip(lvl, tenure)]
    )
    salary = (salary / 100).round() * 100

    df = pd.DataFrame(
        {
            "이름": [rng.choice(surnames) + rng.choice(givens) for _ in range(n)],
            "부서": dept,
            "팀": team,
            "레벨": lvl,
            "직급": [titles[l] for l in lvl],
            "근속연수": tenure,
            "연봉": salary.astype(int),
            "성과등급": rng.choice(grades, n, p=[0.15, 0.4, 0.35, 0.1]),
            "몰입도": rng.normal(74, 11, n).round(0).clip(35, 100).astype(int),
            "재택비율": rng.choice(range(0, 101, 10), n),
            "근무지": rng.choice(locs, n, p=[0.5, 0.3, 0.1, 0.1]),
        }
    )
    return df


@st.cache_data
def geo_points() -> pd.DataFrame:
    """전국 오프라인 매장 네트워크 (가상)."""
    rng = np.random.default_rng(11)
    centers = {
        "서울": (37.5665, 126.9780, 14),
        "경기": (37.4138, 127.5183, 12),
        "인천": (37.4563, 126.7052, 5),
        "부산": (35.1796, 129.0756, 8),
        "대구": (35.8714, 128.6014, 5),
        "대전": (36.3504, 127.3845, 4),
        "광주": (35.1595, 126.8526, 4),
        "제주": (33.4996, 126.5312, 3),
    }
    types = ["플래그십", "일반", "익스프레스"]
    rows = []
    idx = 1
    for city, (lat, lon, cnt) in centers.items():
        for _ in range(cnt):
            t = rng.choice(types, p=[0.12, 0.6, 0.28])
            scale = {"플래그십": 3.0, "일반": 1.6, "익스프레스": 0.8}[t]
            rows.append(
                {
                    "매장명": f"오렌지마켓 {city}{idx:02d}",
                    "도시": city,
                    "유형": t,
                    "lat": lat + rng.normal(0, 0.07),
                    "lon": lon + rng.normal(0, 0.07),
                    "월매출": int(rng.normal(120, 40) * scale),
                    "월방문객": int(rng.normal(9000, 2500) * scale),
                    "오픈연도": int(rng.integers(2013, 2026)),
                }
            )
            idx += 1
    df = pd.DataFrame(rows)
    df["월매출"] = df["월매출"].clip(20, None)
    df["월방문객"] = df["월방문객"].clip(1500, None)
    return df


@st.cache_data
def fx_fallback() -> pd.DataFrame:
    """환율 API 실패 시 사용할 원/달러 대체 시계열."""
    rng = np.random.default_rng(3)
    days = pd.date_range(date.today() - timedelta(days=180), periods=180, freq="D")
    walk = 1330 + np.cumsum(rng.normal(0, 4, len(days)))
    return pd.DataFrame({"날짜": days, "환율": walk.round(2)})


def review_sample() -> str:
    """텍스트 분석기 기본 입력용 현실적인 상품 리뷰 글."""
    return (
        "지난주에 주문한 무선청소기를 일주일 정도 사용해 보고 후기를 남깁니다. "
        "우선 흡입력은 생각보다 훨씬 강했습니다. 카펫 위 먼지나 머리카락도 한 번에 빨아들여서 "
        "청소 시간이 확실히 줄었습니다. 무게는 가벼운 편이라 계단이나 높은 곳을 청소할 때도 팔이 "
        "덜 아팠고, 분리형 배터리라 여분을 충전해 두면 넓은 집도 끊김 없이 청소할 수 있었습니다. "
        "다만 아쉬운 점도 있습니다. 먼지통 용량이 작아서 청소 도중에 두세 번 비워야 했고, "
        "최대 모드로 돌리면 소음이 다소 크게 느껴졌습니다. 충전 거치대가 벽걸이 방식이라 설치에 "
        "시간이 조금 걸렸습니다. 그래도 전체적으로는 가격 대비 만족스러운 제품이라 재구매 의향이 "
        "있고, 주변에도 추천할 생각입니다. 배송도 주문 다음 날 바로 도착해서 좋았습니다."
    )

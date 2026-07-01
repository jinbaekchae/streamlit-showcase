"""⑤ 환율 대시보드 — 무료 공개 API 실시간 조회."""

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from utils.sample_data import fx_fallback
from utils.theme import ORANGE, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header(
    "💱",
    "환율 대시보드",
    "무료 공개 API로 환율을 실시간 조회, 결과는 1시간 캐시",
)

CURRENCIES = ["USD", "EUR", "JPY", "GBP", "CNY", "KRW"]
CURRENCY_LABEL = {
    "USD": "USD 미국 달러",
    "EUR": "EUR 유로",
    "JPY": "JPY 일본 엔",
    "GBP": "GBP 영국 파운드",
    "CNY": "CNY 중국 위안",
    "KRW": "KRW 대한민국 원",
}


@st.cache_data(ttl=3600)
def fetch_series(base: str, quote: str) -> tuple[pd.DataFrame, bool]:
    """최근 180일 환율 시계열을 가져온다. 실패하면 대체 데이터로 넘어간다."""
    if base == quote:
        return pd.DataFrame(), True
    end = date.today()
    start = end - timedelta(days=180)
    url = f"https://api.frankfurter.app/{start}..{end}"
    try:
        r = requests.get(url, params={"from": base, "to": quote}, timeout=8)
        r.raise_for_status()
        rates = r.json()["rates"]
        rows = [{"날짜": pd.Timestamp(d), "환율": v[quote]} for d, v in sorted(rates.items())]
        df = pd.DataFrame(rows)
        if df.empty:
            return fx_fallback(), False
        return df, True
    except Exception:
        return fx_fallback(), False


# ── 통화 선택 카드 ────────────────────────────
section("통화 선택")
with st.container(border=True):
    c1, c2 = st.columns(2)
    base = c1.selectbox(
        "기준 통화", CURRENCIES, index=0, format_func=lambda c: CURRENCY_LABEL[c]
    )
    quote = c2.selectbox(
        "대상 통화", CURRENCIES, index=5, format_func=lambda c: CURRENCY_LABEL[c]
    )

if base == quote:
    st.info("기준 통화와 대상 통화가 같습니다. 서로 다른 통화를 선택해 주세요.")
    footer()
    st.stop()

df, live = fetch_series(base, quote)
if not live:
    st.warning(
        "실시간 조회에 실패해 대체 데이터를 표시합니다. "
        "네트워크 상황에 따라 실제 환율과 차이가 있을 수 있습니다."
    )

df = df.sort_values("날짜").reset_index(drop=True)
latest = float(df["환율"].iloc[-1])
month_ago = float(df["환율"].iloc[-22]) if len(df) >= 22 else float(df["환율"].iloc[0])
delta = (latest - month_ago) / month_ago * 100 if month_ago else 0.0
period_high = float(df["환율"].max())
period_low = float(df["환율"].min())
period_avg = float(df["환율"].mean())

# ── 핵심 지표 ────────────────────────────────
section("핵심 지표")
m1, m2, m3, m4 = st.columns(4)
m1.metric(
    f"현재 1 {base} → {quote}",
    f"{latest:,.2f}",
    f"{delta:+.2f}% (약 한 달 전 대비)",
)
m2.metric("기간 최고", f"{period_high:,.2f}")
m3.metric("기간 최저", f"{period_low:,.2f}")
m4.metric("기간 평균", f"{period_avg:,.2f}")

# ── 추이 차트 ────────────────────────────────
section("최근 180일 추이")
with st.container(border=True):
    fig = px.area(df, x="날짜", y="환율")
    fig.update_traces(
        line_color=ORANGE,
        fillcolor="rgba(255,108,0,0.10)",
        hovertemplate="%{x|%Y-%m-%d}<br>환율 %{y:,.2f}<extra></extra>",
    )
    fig = style_fig(fig, height=360, legend=False)
    fig.update_layout(
        yaxis_title=f"1 {base} 당 {quote}",
        xaxis_title="",
    )
    st.plotly_chart(fig, width="stretch")

# ── 환전 계산기 ──────────────────────────────
section("환전 계산기")
with st.container(border=True):
    amount = st.number_input(
        f"{base} 금액", min_value=0.0, value=100.0, step=10.0, format="%.2f"
    )
    converted = amount * latest
    st.success(
        f"{amount:,.2f} {base}  =  **{converted:,.2f} {quote}**  "
        f"(현재 환율 1 {base} = {latest:,.2f} {quote} 기준)"
    )

feature_note(
    "환율 대시보드",
    [
        "`requests` 로 외부 REST API(frankfurter.app)를 호출해 실시간 데이터 사용",
        "`@st.cache_data(ttl=3600)`: API 응답을 1시간 캐시해 호출 횟수 절감",
        "네트워크 실패·빈 응답 시 대체 데이터로 넘어가는 예외 처리",
        "`st.selectbox` `st.number_input` 으로 조건 입력받아 즉시 환산",
        "`st.metric` delta 로 약 한 달 전 대비 등락률 표기",
    ],
)
footer()

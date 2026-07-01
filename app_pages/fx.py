"""⑤ 환율 대시보드."""

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from utils.sample_data import fx_fallback
from utils.ui import feature_note, footer

st.title("💱 환율 대시보드")
st.caption("무료 공개 API(frankfurter.app)에서 환율을 실시간으로 불러옵니다. 결과는 1시간 캐시됩니다.")

CURRENCIES = ["USD", "EUR", "JPY", "GBP", "CNY", "KRW"]

c1, c2 = st.columns(2)
base = c1.selectbox("기준 통화", CURRENCIES, index=0)
quote = c2.selectbox("대상 통화", CURRENCIES, index=5)


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
        return pd.DataFrame(rows), True
    except Exception:
        return fx_fallback(), False


if base == quote:
    st.info("기준 통화와 대상 통화가 같습니다. 서로 다른 통화를 선택해 주세요.")
    st.stop()

df, live = fetch_series(base, quote)
if not live:
    st.warning("실시간 조회에 실패해 대체 데이터를 표시합니다. (네트워크 상황에 따라 달라질 수 있습니다)")

latest = df["환율"].iloc[-1]
month_ago = df["환율"].iloc[-22] if len(df) >= 22 else df["환율"].iloc[0]
delta = (latest - month_ago) / month_ago * 100

m1, m2, m3 = st.columns(3)
m1.metric(f"현재 {base}/{quote}", f"{latest:,.2f}", f"{delta:+.2f}% (약 한 달)")
m2.metric("기간 최고", f"{df['환율'].max():,.2f}")
m3.metric("기간 최저", f"{df['환율'].min():,.2f}")

fig = px.line(df, x="날짜", y="환율", title=f"{base} → {quote} 최근 180일")
fig.update_traces(line_color="#ff6c00")
fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=340)
st.plotly_chart(fig, width="stretch")

st.divider()
st.markdown("**환전 계산기**")
amount = st.number_input(f"{base} 금액", min_value=0.0, value=100.0, step=10.0)
st.success(f"{amount:,.2f} {base}  =  **{amount * latest:,.2f} {quote}**  (현재 환율 기준)")

feature_note(
    "환율 대시보드",
    [
        "`requests` 로 외부 REST API를 호출해 실시간 데이터 사용",
        "`@st.cache_data(ttl=3600)`: API 응답을 1시간 캐시해 호출 횟수 절감",
        "네트워크 실패 시 대체 데이터로 넘어가는 예외 처리",
        "`st.selectbox` `st.number_input` 으로 조건 입력받아 즉시 환산",
    ],
)
footer()

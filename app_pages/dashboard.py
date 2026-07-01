"""① 매출 대시보드."""

import plotly.express as px
import streamlit as st

from utils.sample_data import sales_data
from utils.ui import feature_note, footer

st.title("📊 매출 대시보드")
st.caption("사이드바에서 조건을 바꾸면 KPI와 차트가 즉시 다시 계산됩니다.")

df = sales_data()

# ── 사이드바 필터 ─────────────────────────────
with st.sidebar:
    st.header("필터")
    min_d, max_d = df["날짜"].min().date(), df["날짜"].max().date()
    date_range = st.date_input("기간", (min_d, max_d), min_value=min_d, max_value=max_d)
    regions = st.multiselect("지역", sorted(df["지역"].unique()), default=sorted(df["지역"].unique()))
    products = st.multiselect("제품", sorted(df["제품"].unique()), default=sorted(df["제품"].unique()))

# 기간 입력이 한쪽만 선택된 순간에도 안전하게 처리
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_d, max_d

mask = (
    (df["날짜"].dt.date >= start)
    & (df["날짜"].dt.date <= end)
    & (df["지역"].isin(regions))
    & (df["제품"].isin(products))
)
f = df[mask]

if f.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ── KPI (전월 대비 증감 포함) ─────────────────────────────
monthly = f.set_index("날짜").resample("MS")["매출"].sum()
last, prev = (monthly.iloc[-1], monthly.iloc[-2]) if len(monthly) >= 2 else (monthly.iloc[-1], 0)
delta = (last - prev) / prev * 100 if prev else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("총매출", f"{f['매출'].sum()/1e8:.2f}억 원")
c2.metric("주문 수", f"{len(f):,}건")
c3.metric("평균 객단가", f"{f['매출'].mean():,.0f}원")
c4.metric("최근월 매출", f"{last/1e8:.2f}억", f"{delta:+.1f}% (전월비)")

st.divider()

# ── 차트 ─────────────────────────────
left, right = st.columns([3, 2])
with left:
    st.markdown("**월별 매출 추이**")
    m = monthly.reset_index()
    m.columns = ["월", "매출"]
    fig = px.area(m, x="월", y="매출", markers=True)
    fig.update_traces(line_color="#ff6c00", fillcolor="rgba(255,108,0,0.15)")
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320)
    st.plotly_chart(fig, width="stretch")

with right:
    st.markdown("**지역별 매출 비중**")
    by_region = f.groupby("지역", as_index=False)["매출"].sum()
    fig2 = px.pie(by_region, names="지역", values="매출", hole=0.5)
    fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320)
    st.plotly_chart(fig2, width="stretch")

st.markdown("**제품별 매출**")
by_product = f.groupby(["분류", "제품"], as_index=False)["매출"].sum()
fig3 = px.bar(by_product, x="제품", y="매출", color="분류", text_auto=".2s")
fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
st.plotly_chart(fig3, width="stretch")

# ── 원본 데이터 + 다운로드 ─────────────────────────────
with st.expander("필터링된 원본 데이터 보기 / 내려받기"):
    st.dataframe(f, width="stretch", height=260)
    st.download_button(
        "CSV로 다운로드",
        f.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

feature_note(
    "매출 대시보드",
    [
        "`st.sidebar` 필터: 날짜 범위·다중 선택 위젯으로 데이터를 실시간 필터링",
        "`st.metric`: 숫자 KPI와 전월 대비 증감(delta)을 한 번에 표시",
        "`st.plotly_chart`: 인터랙티브 차트(확대·툴팁) 삽입",
        "`@st.cache_data`: 무거운 데이터 생성을 한 번만 실행하고 재사용",
        "`st.download_button`: 결과를 CSV 파일로 즉시 내려받기",
    ],
)
footer()

"""① 매출 BI 대시보드."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.sample_data import sales_data
from utils.theme import BORDER, INK, ORANGE, ORANGE_DARK, WOKA_SEQ, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header(
    "📊",
    "매출 BI 대시보드",
    "사이드바 조건을 바꾸면 KPI와 차트가 즉시 다시 계산됩니다.",
)

df = sales_data()

# ── 사이드바 필터 ─────────────────────────────
with st.sidebar:
    st.header("필터")
    min_d, max_d = df["날짜"].min().date(), df["날짜"].max().date()
    date_range = st.date_input(
        "기간", (min_d, max_d), min_value=min_d, max_value=max_d
    )

    all_channels = sorted(df["채널"].unique())
    all_regions = sorted(df["지역"].unique())
    all_cats = sorted(df["분류"].unique())

    channels = st.multiselect("채널", all_channels, default=all_channels)
    regions = st.multiselect("지역", all_regions, default=all_regions)
    cats = st.multiselect("분류", all_cats, default=all_cats)

# 기간이 한쪽만 선택된 순간에도 안전하게 처리
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_d, max_d

mask = (
    (df["날짜"].dt.date >= start)
    & (df["날짜"].dt.date <= end)
    & (df["채널"].isin(channels))
    & (df["지역"].isin(regions))
    & (df["분류"].isin(cats))
)
f = df[mask]

if f.empty:
    st.info("선택한 조건에 해당하는 데이터가 없습니다. 필터를 조정해 주세요.")
    footer()
    st.stop()

# ── 상단 KPI ─────────────────────────────
total_sales = int(f["매출"].sum())
total_profit = int(f["이익"].sum())
profit_rate = total_profit / total_sales * 100 if total_sales else 0
orders = len(f)
aov = f["매출"].mean()
repeat_rate = (f["고객유형"] == "재구매").mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("총매출", f"{total_sales/1e8:.2f}억")
k2.metric("총이익", f"{total_profit/1e8:.2f}억", f"이익률 {profit_rate:.1f}%")
k3.metric("주문 수", f"{orders:,}건")
k4.metric("평균 객단가", f"{aov:,.0f}원")
k5.metric("재구매 비율", f"{repeat_rate:.1f}%")

# ── 월별 추이 ─────────────────────────────
section("월별 추이")
with st.container(border=True):
    monthly = (
        f.set_index("날짜")
        .resample("MS")[["매출", "이익"]]
        .sum()
        .reset_index()
    )
    fig_m = go.Figure()
    fig_m.add_trace(
        go.Scatter(
            x=monthly["날짜"],
            y=monthly["매출"] / 1e8,
            name="매출",
            mode="lines",
            fill="tozeroy",
            line=dict(color=ORANGE, width=2.5),
            fillcolor="rgba(255,108,0,0.12)",
            hovertemplate="%{x|%Y-%m}<br>매출 %{y:.2f}억<extra></extra>",
        )
    )
    fig_m.add_trace(
        go.Scatter(
            x=monthly["날짜"],
            y=monthly["이익"] / 1e8,
            name="이익",
            mode="lines+markers",
            line=dict(color="#2a9d8f", width=2.5),
            marker=dict(size=6),
            hovertemplate="%{x|%Y-%m}<br>이익 %{y:.2f}억<extra></extra>",
        )
    )
    fig_m.update_yaxes(title_text="금액(억)", ticksuffix="억")
    fig_m = style_fig(fig_m, height=340)
    st.plotly_chart(fig_m, width="stretch")

# ── 구성 분석 ─────────────────────────────
section("구성 분석")
col_l, col_r = st.columns(2)

with col_l:
    with st.container(border=True):
        st.markdown("**분류별 매출**")
        by_cat = (
            f.groupby("분류", as_index=False)["매출"]
            .sum()
            .sort_values("매출", ascending=False)
        )
        by_cat["매출(억)"] = by_cat["매출"] / 1e8
        fig_cat = px.bar(
            by_cat,
            x="분류",
            y="매출(억)",
            color="분류",
            color_discrete_sequence=WOKA_SEQ,
            text=by_cat["매출(억)"].map(lambda v: f"{v:.2f}억"),
        )
        fig_cat.update_traces(textposition="outside", cliponaxis=False)
        fig_cat.update_yaxes(title_text="매출(억)")
        fig_cat = style_fig(fig_cat, height=330, legend=False)
        st.plotly_chart(fig_cat, width="stretch")

with col_r:
    with st.container(border=True):
        st.markdown("**채널별 비중**")
        by_ch = f.groupby("채널", as_index=False)["매출"].sum()
        fig_ch = px.pie(
            by_ch,
            names="채널",
            values="매출",
            hole=0.55,
            color_discrete_sequence=WOKA_SEQ,
        )
        fig_ch.update_traces(
            textinfo="percent+label",
            hovertemplate="%{label}<br>%{percent}<extra></extra>",
        )
        fig_ch = style_fig(fig_ch, height=330, legend=False, show_ygrid=False)
        st.plotly_chart(fig_ch, width="stretch")

# ── 지역별 매출 ─────────────────────────────
section("지역별 매출")
with st.container(border=True):
    by_region = (
        f.groupby("지역", as_index=False)["매출"]
        .sum()
        .sort_values("매출", ascending=True)
    )
    by_region["매출(억)"] = by_region["매출"] / 1e8
    fig_reg = px.bar(
        by_region,
        x="매출(억)",
        y="지역",
        orientation="h",
        text=by_region["매출(억)"].map(lambda v: f"{v:.2f}억"),
    )
    fig_reg.update_traces(
        marker_color=ORANGE, textposition="outside", cliponaxis=False
    )
    fig_reg.update_xaxes(title_text="매출(억)")
    fig_reg = style_fig(fig_reg, height=340, legend=False, show_ygrid=False)
    st.plotly_chart(fig_reg, width="stretch")

# ── 요일 × 시간대 히트맵 ─────────────────────────────
section("요일 × 시간대 히트맵")
with st.container(border=True):
    st.markdown("**시간대별 매출 집중도**")
    tmp = f.copy()
    tmp["요일"] = tmp["날짜"].dt.dayofweek
    pivot = (
        tmp.groupby(["요일", "시"])["매출"].sum().div(1e8).reset_index()
    )
    day_labels = ["월", "화", "수", "목", "금", "토", "일"]
    heat = pivot.pivot(index="요일", columns="시", values="매출").reindex(
        range(7)
    )
    heat.index = day_labels
    fig_heat = px.imshow(
        heat,
        labels=dict(x="시간대", y="요일", color="매출(억)"),
        color_continuous_scale=["#fff3e9", ORANGE, ORANGE_DARK],
        aspect="auto",
    )
    fig_heat.update_xaxes(title_text="시간대", dtick=1)
    fig_heat = style_fig(fig_heat, height=340, legend=False, show_ygrid=False)
    st.plotly_chart(fig_heat, width="stretch")

# ── 원본 데이터 + 다운로드 ─────────────────────────────
with st.expander("필터링된 원본 데이터 보기 / 내려받기"):
    st.dataframe(f, width="stretch", height=280)
    st.download_button(
        "CSV로 내려받기",
        f.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

feature_note(
    "매출 BI 대시보드",
    [
        "`st.sidebar` 필터: 날짜 범위·다중 선택 위젯으로 데이터를 실시간 필터링",
        "`st.metric`: 5개 KPI를 카드로 배치하고 이익률을 delta로 병기",
        "`st.container(border=True)`: 관련 차트를 카드로 묶어 정돈",
        "`plotly`: 라인·막대·도넛·히트맵 등 인터랙티브 차트 조합",
        "`@st.cache_data`: 무거운 데이터 생성을 한 번만 실행하고 재사용",
        "`st.download_button`: 필터 결과를 CSV로 즉시 내려받기",
    ],
)
footer()

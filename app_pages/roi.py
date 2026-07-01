"""⑩ ROI 계산기."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.theme import ORANGE, ORANGE_DARK, WOKA_SEQ, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header("🧮", "ROI 계산기", "투자 회수 시점과 손익분기를 계산")

# ── 입력 카드 ─────────────────────────────
section("투자 조건 입력")
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        invest = st.number_input("초기 투자금(만원)", 0, 100000, 3000, step=100)
    with c2:
        monthly_rev = st.number_input("월 예상 매출(만원)", 0, 20000, 800, step=50)
    with c3:
        monthly_cost = st.number_input("월 고정비용(만원)", 0, 20000, 450, step=50)
    with c4:
        months = st.slider("분석 기간(개월)", 6, 60, 24)

# ── 계산 ─────────────────────────────
monthly_profit = monthly_rev - monthly_cost
m = np.arange(1, months + 1)
cumulative = monthly_profit * m - invest

df = pd.DataFrame(
    {
        "개월": m,
        "월순이익(만원)": np.full(months, monthly_profit),
        "누적손익(만원)": cumulative,
    }
)

reached = df["누적손익(만원)"] >= 0
break_even = int(df.loc[reached, "개월"].min()) if reached.any() else None
total_profit = int(cumulative[-1])
roi = total_profit / invest * 100 if invest else 0.0

# ── KPI ─────────────────────────────
section("핵심 지표")
k1, k2, k3, k4 = st.columns(4)
k1.metric("월 순이익", f"{monthly_profit:,}만 원", delta="흑자" if monthly_profit > 0 else "적자")
k2.metric("손익분기 도달", f"{break_even}개월" if break_even else "기간 내 미도달")
k3.metric(
    f"{months}개월 누적손익",
    f"{total_profit:,}만 원",
    delta=f"{total_profit:,}만 원",
    delta_color="normal",
)
k4.metric("ROI", f"{roi:,.0f}%", delta=f"{roi:,.0f}%", delta_color="normal")

if monthly_profit <= 0:
    st.warning("월 순이익이 0 이하입니다. 매출 확대 또는 비용 절감 없이는 투자 회수가 불가합니다.")
elif break_even is None:
    st.info(f"현재 조건에서는 {months}개월 내 손익분기 미도달입니다. 분석 기간을 늘려 확인하십시오.")
else:
    st.success(f"{break_even}개월 시점에 투자금을 회수하며, 이후 월 {monthly_profit:,}만 원씩 순이익이 누적됩니다.")

# ── 누적손익 곡선 ─────────────────────────────
section("누적손익 추이")
with st.container(border=True):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["개월"],
            y=df["누적손익(만원)"],
            mode="lines",
            name="누적손익",
            line=dict(color=ORANGE, width=3),
            fill="tozeroy",
            fillcolor="rgba(255,108,0,0.12)",
            hovertemplate="%{x}개월<br>누적손익 %{y:,}만 원<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#888")
    if break_even:
        fig.add_vline(x=break_even, line_dash="dot", line_color=WOKA_SEQ[2])
        fig.add_annotation(
            x=break_even,
            y=0,
            text=f"손익분기 {break_even}개월",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,
            font=dict(color=ORANGE_DARK, size=12),
            bgcolor="white",
            bordercolor=WOKA_SEQ[2],
            borderwidth=1,
            borderpad=4,
        )
    fig.update_layout(xaxis_title="개월", yaxis_title="누적손익(만원)")
    fig = style_fig(fig, height=380, legend=False)
    st.plotly_chart(fig, width="stretch")

# ── 월별 상세 표 ─────────────────────────────
section("월별 상세")
with st.expander("월별 손익 표 / CSV 다운로드"):
    st.dataframe(df, width="stretch", height=280, hide_index=True)
    st.download_button(
        "CSV 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="roi_projection.csv",
        mime="text/csv",
    )

feature_note(
    "ROI 계산기",
    [
        "`st.number_input` `st.slider` 입력값으로 즉시 재무 계산",
        "numpy·pandas 계산 결과를 지표·그래프·표로 동시 표현",
        "`add_vline` `add_annotation` 으로 손익분기 시점 주석 표시",
        "계산 결과를 CSV(utf-8-sig)로 내려받아 실무 활용",
    ],
)
footer()

"""⑩ ROI 계산기."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ui import feature_note, footer

st.title("🧮 ROI 계산기")
st.caption("투자 회수 시점과 손익분기점을 계산합니다. 비즈니스 계산기를 그대로 웹앱으로 만듭니다.")

c1, c2 = st.columns(2)
with c1:
    invest = st.number_input("초기 투자금(만원)", 0, 100000, 3000, step=100)
    monthly_rev = st.number_input("월 예상 매출(만원)", 0, 20000, 800, step=50)
with c2:
    monthly_cost = st.number_input("월 고정비용(만원)", 0, 20000, 450, step=50)
    months = st.slider("분석 기간(개월)", 6, 60, 24)

monthly_profit = monthly_rev - monthly_cost
m = np.arange(1, months + 1)
cumulative = monthly_profit * m - invest

df = pd.DataFrame({"개월": m, "누적손익": cumulative})

# 손익분기 도달 시점
break_even = int(df.loc[df["누적손익"] >= 0, "개월"].min()) if (df["누적손익"] >= 0).any() else None
total_profit = cumulative[-1]
roi = total_profit / invest * 100 if invest else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("월 순이익", f"{monthly_profit:,}만 원")
k2.metric("손익분기 도달", f"{break_even}개월" if break_even else "기간 내 미도달")
k3.metric(f"{months}개월 누적손익", f"{total_profit:,}만 원")
k4.metric("ROI", f"{roi:,.0f}%")

if monthly_profit <= 0:
    st.warning("월 순이익이 0 이하입니다. 매출을 늘리거나 비용을 줄여야 회수가 가능합니다.")

# ── 누적손익 곡선 ─────────────────────────────
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df["개월"], y=df["누적손익"], mode="lines",
        line=dict(color="#ff6c00", width=3), fill="tozeroy",
        fillcolor="rgba(255,108,0,0.12)",
    )
)
fig.add_hline(y=0, line_dash="dash", line_color="#888")
if break_even:
    fig.add_vline(x=break_even, line_dash="dot", line_color="#2a9d8f")
    fig.add_annotation(x=break_even, y=0, text=f"손익분기 {break_even}개월", showarrow=True, arrowhead=2)
fig.update_layout(
    height=340, margin=dict(l=0, r=0, t=10, b=0),
    xaxis_title="개월", yaxis_title="누적손익(만원)",
)
st.plotly_chart(fig, width="stretch")

with st.expander("월별 상세 표 / 다운로드"):
    st.dataframe(df, width="stretch", height=260)
    st.download_button(
        "CSV 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="roi_projection.csv",
        mime="text/csv",
    )

feature_note(
    "ROI 계산기",
    [
        "`st.number_input` `st.slider` 로 받은 값으로 즉시 재무 계산",
        "numpy·pandas 계산 결과를 지표·그래프·표로 동시에 표현",
        "`add_vline` 등으로 손익분기 시점을 그래프에 주석 표시",
        "계산 결과를 CSV로 내려받아 실무에 활용",
    ],
)
footer()

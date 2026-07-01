"""④ 예측 시뮬레이터."""

import plotly.graph_objects as go
import streamlit as st

from utils.ui import feature_note, footer

st.title("🤖 예측 시뮬레이터")
st.caption("슬라이더를 움직이면 예측값이 즉시 다시 계산됩니다. 콜백을 따로 연결하지 않아도 됩니다.")

st.markdown("가상의 카페 **일 매출**을 몇 가지 입력으로 예측하는 간단한 모델입니다.")

# ── 입력 ─────────────────────────────
c1, c2 = st.columns(2)
with c1:
    foot = st.slider("하루 유동인구(명)", 500, 20000, 6000, step=500)
    seats = st.slider("좌석 수", 10, 120, 40, step=5)
    rating = st.slider("리뷰 평점", 3.0, 5.0, 4.3, step=0.1)
with c2:
    promo = st.toggle("프로모션 진행", value=True)
    weather = st.select_slider("날씨", ["비", "흐림", "맑음"], value="맑음")
    price = st.number_input("평균 객단가(원)", 3000, 15000, 6500, step=500)

# ── 투명한 가중치 모델 ─────────────────────────────
weather_factor = {"비": 0.8, "흐림": 1.0, "맑음": 1.2}[weather]
visit_rate = 0.018 + (rating - 4.0) * 0.01  # 유동인구 중 방문 전환율
visitors = foot * visit_rate * weather_factor
visitors = min(visitors, seats * 12)  # 좌석 회전율 상한
revenue = visitors * price * (1.15 if promo else 1.0)

st.divider()
left, right = st.columns([2, 3])

with left:
    st.metric("예상 방문객", f"{visitors:,.0f}명")
    st.metric("예상 일 매출", f"{revenue/1e4:,.0f}만 원")
    st.metric("월 환산(30일)", f"{revenue*30/1e8:,.2f}억 원")

with right:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=revenue / 1e4,
            number={"suffix": " 만원"},
            title={"text": "예상 일 매출"},
            gauge={
                "axis": {"range": [0, 600]},
                "bar": {"color": "#ff6c00"},
                "steps": [
                    {"range": [0, 200], "color": "#ffe8d6"},
                    {"range": [200, 400], "color": "#ffd0a8"},
                ],
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, width="stretch")

# ── 민감도: 유동인구를 바꿔가며 매출 곡선 ─────────────────────────────
st.markdown("**유동인구에 따른 매출 변화**")
xs = list(range(500, 20001, 500))
ys = []
for x in xs:
    v = min(x * visit_rate * weather_factor, seats * 12)
    ys.append(v * price * (1.15 if promo else 1.0) / 1e4)
line = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#ff6c00", width=3)))
line.add_vline(x=foot, line_dash="dash", line_color="#888")
line.update_layout(
    height=260, margin=dict(l=0, r=0, t=10, b=0),
    xaxis_title="유동인구(명)", yaxis_title="예상 매출(만원)",
)
st.plotly_chart(line, width="stretch")

feature_note(
    "예측 시뮬레이터",
    [
        "위젯 값이 바뀌면 스크립트 전체가 위에서 아래로 다시 실행 → 결과 자동 갱신",
        "`st.slider` `st.toggle` `st.select_slider` 등 다양한 입력 위젯",
        "`st.plotly_chart` 게이지·라인으로 예측 결과를 시각화",
        "이 원리 그대로 scikit-learn 등 실제 머신러닝 모델을 연결할 수 있음",
    ],
)
footer()

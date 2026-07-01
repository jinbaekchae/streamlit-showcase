"""④ 예측 시뮬레이터."""

import plotly.graph_objects as go
import streamlit as st

from utils.theme import BORDER, INK, MUTED, ORANGE, ORANGE_DARK, SOFT, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header("🤖", "예측 시뮬레이터", "슬라이더를 움직이면 예측값이 즉시 재계산")

st.markdown(
    "오렌지마켓 신규 매장의 **일 매출**을 투명한 가중치 모델로 예측합니다. "
    "입력을 조정하면 스크립트 전체가 다시 실행되어 결과가 자동으로 갱신됩니다."
)

# ── 입력 카드 ─────────────────────────────
section("입력 조건")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        foot = st.slider("하루 유동인구(명)", 500, 20000, 6000, step=500)
        area = st.slider("매장 평수(평)", 10, 120, 45, step=5)
    with c2:
        rating = st.slider("리뷰 평점", 3.0, 5.0, 4.3, step=0.1)
        price = st.number_input("평균 객단가(원)", 3000, 30000, 9500, step=500)
    with c3:
        weather = st.select_slider("날씨", ["비", "흐림", "맑음"], value="맑음")
        promo = st.toggle("프로모션 진행", value=True)

# ── 투명한 가중치 모델 ─────────────────────────────
WEATHER_FACTOR = {"비": 0.75, "흐림": 1.0, "맑음": 1.2}
SEATS_PER_PYEONG = 0.9  # 평당 좌석 환산
TURNOVER = 11  # 좌석당 일 회전 상한
PROMO_LIFT = 1.15


def predict_revenue(foot_traffic: int) -> tuple[float, float]:
    """유동인구를 받아 (방문객, 일 매출)을 계산한다."""
    weather_factor = WEATHER_FACTOR[weather]
    visit_rate = 0.018 + (rating - 4.0) * 0.01  # 평점이 전환율을 좌우
    raw_visitors = foot_traffic * visit_rate * weather_factor
    seat_cap = area * SEATS_PER_PYEONG * TURNOVER  # 평수 → 좌석 회전 상한
    visitors = min(raw_visitors, seat_cap)
    revenue = visitors * price * (PROMO_LIFT if promo else 1.0)
    return visitors, revenue


visitors, revenue = predict_revenue(foot)
seat_cap = area * SEATS_PER_PYEONG * TURNOVER
capped = visitors >= seat_cap - 1e-6

# ── 출력 KPI ─────────────────────────────
section("예측 결과")
k1, k2, k3 = st.columns(3)
with k1:
    st.metric(
        "예상 방문객",
        f"{visitors:,.0f}명",
        delta="좌석 회전 상한 도달" if capped else None,
        delta_color="off",
    )
with k2:
    st.metric("예상 일 매출", f"{revenue/1e4:,.0f}만원", delta="프로모션 +15%" if promo else None)
with k3:
    st.metric("월 환산(30일)", f"{revenue*30/1e8:,.2f}억")

# ── 게이지 ─────────────────────────────
with st.container(border=True):
    gauge_max = 800
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=revenue / 1e4,
            number={"suffix": " 만원", "font": {"size": 34, "color": INK}},
            title={"text": "예상 일 매출", "font": {"size": 15, "color": MUTED}},
            gauge={
                "axis": {"range": [0, gauge_max], "tickcolor": BORDER},
                "bar": {"color": ORANGE, "thickness": 0.68},
                "bgcolor": SOFT,
                "borderwidth": 0,
                "steps": [
                    {"range": [0, gauge_max * 0.33], "color": "#ffe8d6"},
                    {"range": [gauge_max * 0.33, gauge_max * 0.66], "color": "#ffd0a8"},
                ],
                "threshold": {
                    "line": {"color": ORANGE_DARK, "width": 3},
                    "thickness": 0.8,
                    "value": revenue / 1e4,
                },
            },
        )
    )
    # 게이지(go.Indicator)는 축·범례가 없어 style_fig 대신 폰트·배경만 직접 통일한다.
    gauge.update_layout(
        height=280,
        margin=dict(l=24, r=24, t=48, b=16),
        font=dict(family="Pretendard, sans-serif", color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(gauge, width="stretch")

# ── 민감도 곡선 ─────────────────────────────
section("유동인구에 따른 매출 변화")
with st.container(border=True):
    xs = list(range(500, 20001, 500))
    ys = [predict_revenue(x)[1] / 1e4 for x in xs]

    line = go.Figure()
    line.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color=ORANGE, width=3),
            fill="tozeroy",
            fillcolor="rgba(255,108,0,0.08)",
            name="예상 일 매출",
            hovertemplate="유동인구 %{x:,}명<br>예상 매출 %{y:,.0f}만원<extra></extra>",
        )
    )
    line.add_trace(
        go.Scatter(
            x=[foot],
            y=[revenue / 1e4],
            mode="markers",
            marker=dict(color=ORANGE_DARK, size=12, line=dict(color="white", width=2)),
            name="현재 입력",
            hovertemplate="현재 유동인구 %{x:,}명<br>예상 매출 %{y:,.0f}만원<extra></extra>",
        )
    )
    line.add_vline(x=foot, line_dash="dash", line_color=MUTED, line_width=1.5)
    line.update_layout(xaxis_title="유동인구(명)", yaxis_title="예상 일 매출(만원)")
    line = style_fig(line, height=340)
    st.plotly_chart(line, width="stretch")

    if capped:
        st.info(
            "현재 매장 평수 기준 좌석 회전 상한에 도달했습니다. "
            "유동인구를 더 늘려도 매출이 평평해집니다. 평수를 키우면 상한이 함께 올라갑니다."
        )

feature_note(
    "예측 시뮬레이터",
    [
        "위젯 값이 바뀌면 스크립트 전체가 위에서 아래로 다시 실행 → 결과 자동 갱신",
        "`st.slider` `st.toggle` `st.select_slider` `st.number_input` 등 다양한 입력 위젯",
        "`st.metric` 카드로 핵심 예측값 요약, `delta` 로 상태 표시",
        "`go.Indicator` 게이지·`go.Scatter` 민감도 곡선으로 결과 시각화",
        "가중치 모델을 함수로 분리 → scikit-learn 등 실제 모델로 교체 가능",
    ],
)
footer()

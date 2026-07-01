"""⑧ 지도 시각화."""

import plotly.express as px
import streamlit as st

from utils.sample_data import geo_points
from utils.theme import WOKA_SEQ, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header("🗺️", "지도 시각화", "위경도만 있으면 지도가 한 줄")

df = geo_points()

TYPE_COLORS = {"플래그십": "#ff6c00", "일반": "#4c6ef5", "익스프레스": "#2a9d8f"}

# ── 필터 ───────────────────────────────
with st.container(border=True):
    f1, f2 = st.columns(2)
    cities = f1.multiselect(
        "도시",
        sorted(df["도시"].unique()),
        default=sorted(df["도시"].unique()),
    )
    types = f2.multiselect(
        "유형",
        list(TYPE_COLORS.keys()),
        default=list(TYPE_COLORS.keys()),
    )

view = df[df["도시"].isin(cities) & df["유형"].isin(types)].copy()

if view.empty:
    st.info("선택한 조건에 해당하는 매장이 없습니다. 도시 또는 유형을 하나 이상 선택해 주세요.")
    footer()
    st.stop()

# ── KPI ────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("매장 수", f"{len(view):,}곳")
k2.metric("합계 월매출", f"{view['월매출'].sum():,}백만원")
k3.metric("평균 월방문객", f"{view['월방문객'].mean():,.0f}명")
k4.metric("평균 오픈연차", f"{(2026 - view['오픈연도']).mean():.1f}년")

# ── 지도 ───────────────────────────────
section("매장 위치")
view["색"] = view["유형"].map(TYPE_COLORS)
st.map(view, latitude="lat", longitude="lon", size="월매출", color="색")

legend = "  ".join(f"● {name}" for name in TYPE_COLORS)
st.caption(f"점 크기는 월매출 규모를 반영합니다.  유형별 색상: {legend}")

# ── 분포 ───────────────────────────────
section("분포")
c1, c2 = st.columns(2)

with c1:
    city_cnt = view["도시"].value_counts().sort_values(ascending=True)
    fig_city = px.bar(
        x=city_cnt.values,
        y=city_cnt.index,
        orientation="h",
        title="도시별 매장 수",
        labels={"x": "매장 수", "y": ""},
    )
    fig_city.update_traces(marker_color=WOKA_SEQ[0])
    st.plotly_chart(style_fig(fig_city, height=320, legend=False), width="stretch")

with c2:
    type_rev = (
        view.groupby("유형", as_index=False)["월매출"].sum().sort_values("월매출", ascending=False)
    )
    fig_type = px.bar(
        type_rev,
        x="유형",
        y="월매출",
        color="유형",
        title="유형별 합계 월매출(백만원)",
        color_discrete_sequence=WOKA_SEQ,
        labels={"월매출": "월매출(백만원)", "유형": ""},
    )
    st.plotly_chart(style_fig(fig_type, height=320, legend=False), width="stretch")

# ── 상위 매장 ──────────────────────────
section("상위 매장")
top = (
    view.sort_values("월매출", ascending=False)
    .head(10)
    .loc[:, ["매장명", "도시", "유형", "월매출", "월방문객", "오픈연도"]]
    .reset_index(drop=True)
)
st.dataframe(
    top,
    width="stretch",
    hide_index=True,
    column_config={
        "월매출": st.column_config.NumberColumn("월매출(백만원)", format="%d"),
        "월방문객": st.column_config.NumberColumn("월방문객(명)", format="%d"),
        "오픈연도": st.column_config.NumberColumn("오픈연도", format="%d"),
    },
)

feature_note(
    "지도 시각화",
    [
        "`st.map`: 위경도 컬럼만 넘기면 지도 위에 점을 표시(별도 설정 불필요)",
        "`size`·`color` 인자로 값·범주에 따라 점 크기와 색상을 구분",
        "유형별 hex 색상 매핑으로 범례와 지도 색을 일치",
        "필터 선택에 따라 지도·지표·차트·표가 함께 갱신",
        "더 정교한 지도가 필요하면 `st.pydeck_chart` 로 확장 가능",
    ],
)
footer()

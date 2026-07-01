"""⑧ 지도 시각화."""

import streamlit as st

from utils.sample_data import geo_points
from utils.ui import feature_note, footer

st.title("🗺️ 지도 시각화")
st.caption("위경도(lat, lon)만 있으면 지도가 한 줄로 그려집니다. 지점 분포를 지도 위에 표시합니다.")

df = geo_points()

cities = st.multiselect("표시할 도시", sorted(df["도시"].unique()), default=sorted(df["도시"].unique()))
view = df[df["도시"].isin(cities)]

if view.empty:
    st.warning("도시를 하나 이상 선택해 주세요.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("표시 지점 수", f"{len(view)}곳")
c2.metric("합계 월매출", f"{view['월매출'].sum():,}백만 원")
c3.metric("지점당 평균", f"{view['월매출'].mean():,.0f}백만 원")

# 매출 규모를 점 크기로 반영해 지도에 표시
st.map(view, latitude="lat", longitude="lon", size="월매출", color="#ff6c00")

st.markdown("**도시별 지점 수**")
st.bar_chart(view["도시"].value_counts())

feature_note(
    "지도 시각화",
    [
        "`st.map`: 위경도 컬럼만 넘기면 지도 위에 점을 표시(별도 설정 불필요)",
        "`size` 인자로 값에 따라 점 크기를 다르게 표현",
        "필터 선택에 따라 지도·지표·차트가 함께 갱신",
        "더 정교한 지도가 필요하면 `st.pydeck_chart` 로 확장 가능",
    ],
)
footer()

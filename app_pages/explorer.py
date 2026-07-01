"""② 직원 데이터 탐색기."""

import numpy as np
import plotly.express as px
import streamlit as st

from utils.sample_data import employee_data
from utils.theme import WOKA_SEQ, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header(
    "🔎",
    "직원 데이터 탐색기",
    "표를 화면에서 직접 편집·정렬·검색하고, 분포를 시각화합니다.",
)

df = employee_data()

# ── 필터 카드 ─────────────────────────────
section("조건 필터")
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        keyword = st.text_input("이름 검색", placeholder="예: 김")
        depts = st.multiselect(
            "부서",
            sorted(df["부서"].unique()),
            default=sorted(df["부서"].unique()),
        )
    with c2:
        levels = st.multiselect(
            "레벨",
            sorted(df["레벨"].unique()),
            default=sorted(df["레벨"].unique()),
        )
        grades = st.multiselect(
            "성과등급",
            ["S", "A", "B", "C"],
            default=["S", "A", "B", "C"],
        )
    with c3:
        sal_min = int(df["연봉"].min())
        sal_max = int(df["연봉"].max())
        salary = st.slider(
            "연봉 범위(만원)",
            min_value=sal_min,
            max_value=sal_max,
            value=(sal_min, sal_max),
            step=100,
        )

view = df[
    df["부서"].isin(depts)
    & df["레벨"].isin(levels)
    & df["성과등급"].isin(grades)
    & df["연봉"].between(salary[0], salary[1])
]
if keyword:
    view = view[view["이름"].str.contains(keyword)]

st.caption(f"조건에 맞는 인원: **{len(view)}명** / 전체 {len(df)}명")

if view.empty:
    st.info("조건에 맞는 직원이 없습니다. 필터를 조정해 주세요.")
    footer()
    st.stop()

# ── 직원 명부 (편집 가능) ─────────────────────────────
section("직원 명부")
edited = st.data_editor(
    view,
    width="stretch",
    height=430,
    num_rows="dynamic",
    column_config={
        "연봉": st.column_config.NumberColumn("연봉", format="%d 만원"),
        "몰입도": st.column_config.ProgressColumn(
            "몰입도", min_value=0, max_value=100, format="%d"
        ),
        "재택비율": st.column_config.ProgressColumn(
            "재택비율", min_value=0, max_value=100, format="%d%%"
        ),
        "성과등급": st.column_config.SelectboxColumn(
            "성과등급", options=["S", "A", "B", "C"]
        ),
    },
)

# ── KPI ─────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("인원", f"{len(edited)}명", delta=f"전체 대비 {len(edited) - len(df)}")
k2.metric("평균 연봉", f"{edited['연봉'].mean():,.0f} 만원")
k3.metric("평균 근속", f"{edited['근속연수'].mean():.1f} 년")
k4.metric("평균 몰입도", f"{edited['몰입도'].mean():.0f}")

# ── 분포 ─────────────────────────────
section("분포")
left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.markdown("**부서별 평균 연봉**")
        by_dept = (
            edited.groupby("부서", as_index=False)["연봉"]
            .mean()
            .sort_values("연봉", ascending=False)
        )
        fig_bar = px.bar(
            by_dept,
            x="부서",
            y="연봉",
            color="부서",
            color_discrete_sequence=WOKA_SEQ,
            labels={"연봉": "평균 연봉(만원)"},
        )
        fig_bar = style_fig(fig_bar, height=360, legend=False)
        st.plotly_chart(fig_bar, width="stretch")

with right:
    with st.container(border=True):
        st.markdown("**근속연수 대비 연봉**")
        fig_sc = px.scatter(
            edited,
            x="근속연수",
            y="연봉",
            color="레벨",
            color_discrete_sequence=WOKA_SEQ,
            hover_name="이름",
            labels={"근속연수": "근속연수(년)", "연봉": "연봉(만원)"},
            category_orders={"레벨": sorted(edited["레벨"].unique())},
        )
        fig_sc.update_traces(marker=dict(size=9, opacity=0.75))
        fig_sc = style_fig(fig_sc, height=360)
        st.plotly_chart(fig_sc, width="stretch")

# ── 다운로드 ─────────────────────────────
st.download_button(
    "편집한 표를 CSV로 다운로드",
    edited.to_csv(index=False).encode("utf-8-sig"),
    file_name="employees_edited.csv",
    mime="text/csv",
)

feature_note(
    "직원 데이터 탐색기",
    [
        "`st.data_editor`: 셀 직접 수정·행 추가·삭제, 진행률 막대·선택 목록 컬럼 서식",
        "`st.column_config`: 숫자 서식·ProgressColumn·SelectboxColumn 등 컬럼별 표시 지정",
        "`st.metric`: 필터 결과에 연동되는 KPI 카드(delta 포함)",
        "`plotly.express`: 부서별 막대·근속 대비 연봉 산점도, 공용 테마로 통일",
        "필터 위젯 값 변경 시 표·KPI·차트가 자동 재계산",
    ],
)
footer()

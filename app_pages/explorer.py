"""② 데이터 탐색기."""

import streamlit as st

from utils.sample_data import employee_data
from utils.ui import feature_note, footer

st.title("🔎 데이터 탐색기")
st.caption("표를 화면에서 직접 편집·정렬·검색합니다. 엑셀 같은 상호작용을 코드 몇 줄로 구현합니다.")

df = employee_data()

# ── 검색·필터 ─────────────────────────────
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    keyword = st.text_input("이름 검색", placeholder="예: 김")
with c2:
    depts = st.multiselect("부서", sorted(df["부서"].unique()), default=sorted(df["부서"].unique()))
with c3:
    salary_min = st.slider("최소 연봉(만원)", 3000, 12000, 3000, step=500)

view = df[df["부서"].isin(depts) & (df["연봉"] >= salary_min)]
if keyword:
    view = view[view["이름"].str.contains(keyword)]

st.caption(f"조건에 맞는 인원: **{len(view)}명** / 전체 {len(df)}명")

# ── 편집 가능한 표 (막대·진행률 컬럼 서식 포함) ─────────────────────────────
edited = st.data_editor(
    view,
    width="stretch",
    height=420,
    num_rows="dynamic",
    column_config={
        "연봉": st.column_config.NumberColumn("연봉", format="%d 만원"),
        "평가점수": st.column_config.ProgressColumn(
            "평가점수", min_value=0, max_value=100, format="%.1f"
        ),
        "재택비율": st.column_config.ProgressColumn(
            "재택비율", min_value=0, max_value=100, format="%d%%"
        ),
    },
)

st.divider()

# ── 요약 통계 + 다운로드 ─────────────────────────────
left, right = st.columns(2)
with left:
    st.markdown("**부서별 평균 연봉**")
    st.bar_chart(edited.groupby("부서")["연봉"].mean())
with right:
    st.markdown("**요약 통계**")
    st.dataframe(edited[["근속연수", "연봉", "평가점수", "재택비율"]].describe().round(1))

st.download_button(
    "편집한 표를 CSV로 다운로드",
    edited.to_csv(index=False).encode("utf-8-sig"),
    file_name="employees_edited.csv",
    mime="text/csv",
)

feature_note(
    "데이터 탐색기",
    [
        "`st.data_editor`: 표의 셀을 화면에서 직접 수정하고 행 추가·삭제까지 가능",
        "`st.column_config`: 숫자 서식, 진행률 막대 등 컬럼별 표시 방식 지정",
        "`st.dataframe`: 정렬·검색이 되는 대화형 표(헤더 클릭으로 정렬)",
        "필터 위젯의 값이 바뀌면 아래 표·차트가 자동으로 다시 그려짐",
    ],
)
footer()

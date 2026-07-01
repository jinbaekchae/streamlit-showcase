"""⑦ 설문 폼."""

import pandas as pd
import streamlit as st

from utils.ui import feature_note, footer

st.title("📝 설문 폼")
st.caption("여러 입력을 하나로 묶어 제출 버튼을 누를 때만 처리합니다. 응답을 누적·집계합니다.")

if "responses" not in st.session_state:
    st.session_state.responses = []

# ── 폼: 제출 전까지는 재실행이 일어나지 않음 ─────────────────────────────
with st.form("survey", clear_on_submit=True):
    name = st.text_input("이름(선택)")
    role = st.radio("직군", ["기획", "개발", "디자인", "영업/마케팅", "기타"], horizontal=True)
    tools = st.multiselect("사용 중인 도구", ["Excel", "Notion", "Figma", "Slack", "GitHub"])
    nps = st.slider("추천 의향(0~10)", 0, 10, 8)
    comment = st.text_area("자유 의견")
    agree = st.checkbox("응답 저장에 동의합니다")
    submitted = st.form_submit_button("제출", type="primary")

if submitted:
    if not agree:
        st.error("응답을 저장하려면 동의 항목을 체크해 주세요.")
    else:
        st.session_state.responses.append(
            {"이름": name or "익명", "직군": role, "도구수": len(tools), "추천점수": nps, "의견": comment}
        )
        st.success("응답이 저장되었습니다. 아래 집계에 반영됩니다.")

# ── 누적 응답 집계 ─────────────────────────────
st.divider()
n = len(st.session_state.responses)
st.markdown(f"### 지금까지 모인 응답: {n}건")

if n:
    df = pd.DataFrame(st.session_state.responses)
    c1, c2 = st.columns(2)
    c1.metric("평균 추천점수(NPS)", f"{df['추천점수'].mean():.1f} / 10")
    c2.metric("최다 직군", df["직군"].mode()[0])

    st.markdown("**직군 분포**")
    st.bar_chart(df["직군"].value_counts())

    st.dataframe(df, width="stretch")
    st.download_button(
        "응답 CSV 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="survey_responses.csv",
        mime="text/csv",
    )
    if st.button("응답 전체 초기화"):
        st.session_state.responses = []
        st.rerun()
else:
    st.info("아직 응답이 없습니다. 위 폼을 제출해 보세요. 여러 번 제출하면 집계가 쌓입니다.")

feature_note(
    "설문 폼",
    [
        "`st.form`: 여러 입력을 묶어 제출 버튼을 누를 때만 한 번에 처리",
        "`clear_on_submit`: 제출 후 입력값 자동 초기화",
        "`st.session_state`: 제출된 응답을 목록에 누적 저장",
        "입력 검증(동의 체크) 후 집계·차트·다운로드까지 연결",
    ],
)
footer()

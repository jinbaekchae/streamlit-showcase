"""⑦ 설문 폼."""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import feature_note, footer, page_header, section
from utils.theme import ORANGE, WOKA_SEQ, style_fig

page_header("📝", "설문 폼", "여러 입력을 묶어 제출할 때만 처리, 응답 누적·집계")

if "responses" not in st.session_state:
    st.session_state.responses = []

ROLES = ["기획", "개발", "디자인", "영업·마케팅", "기타"]
TOOLS = ["Excel", "Notion", "Figma", "Slack", "GitHub", "Streamlit"]
SAT_LEVELS = ["매우불만", "불만", "보통", "만족", "매우만족"]

# ── 입력 폼: 제출 버튼 전까지 재실행이 일어나지 않음 ─────────────────
section("응답 입력")

with st.container(border=True):
    with st.form("survey", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("이름 (선택)", placeholder="미입력 시 익명 처리")
        with c2:
            role = st.radio("직군", ROLES, horizontal=True)

        tools = st.multiselect("사용 도구", TOOLS, placeholder="사용 중인 도구 선택")

        c3, c4 = st.columns(2)
        with c3:
            nps = st.slider("추천 의향 (NPS, 0~10)", 0, 10, 8)
        with c4:
            satisfaction = st.select_slider("만족도", SAT_LEVELS, value="보통")

        comment = st.text_area("자유 의견", placeholder="개선 제안·불편 사항 등", height=96)
        agree = st.checkbox("응답 저장 및 집계 활용에 동의합니다")
        submitted = st.form_submit_button("제출", type="primary", width="stretch")

    if submitted:
        if not agree:
            st.error("응답을 저장하려면 동의 항목을 체크해 주세요.")
        else:
            st.session_state.responses.append(
                {
                    "이름": name.strip() or "익명",
                    "직군": role,
                    "사용도구": ", ".join(tools) if tools else "없음",
                    "도구수": len(tools),
                    "NPS": nps,
                    "만족도": satisfaction,
                    "의견": comment.strip(),
                }
            )
            st.success("응답이 저장되었습니다. 아래 집계에 반영됩니다.")

# ── 누적 응답 집계 ─────────────────────────────
section("응답 집계")

n = len(st.session_state.responses)

if not n:
    st.info("아직 응답이 없습니다. 위 폼을 제출해 보세요. 여러 번 제출하면 집계가 누적됩니다.")
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
    st.stop()

df = pd.DataFrame(st.session_state.responses)
avg_nps = df["NPS"].mean()
promoter_ratio = (df["NPS"] >= 9).mean() * 100
detractor_ratio = (df["NPS"] <= 6).mean() * 100
nps_score = promoter_ratio - detractor_ratio

m1, m2, m3, m4 = st.columns(4)
m1.metric("응답 수", f"{n}건")
m2.metric("평균 NPS", f"{avg_nps:.1f} / 10")
m3.metric("추천그룹 비율", f"{promoter_ratio:.0f}%", help="추천 의향 9~10점 응답 비율")
m4.metric("NPS 지수", f"{nps_score:+.0f}", help="추천그룹 비율 − 비추천그룹(0~6) 비율")

# ── 분포 차트 ─────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown("**직군 분포**")
        role_counts = df["직군"].value_counts().reindex(ROLES).dropna()
        fig_role = px.bar(
            x=role_counts.values,
            y=role_counts.index,
            orientation="h",
            text=role_counts.values,
            color_discrete_sequence=[ORANGE],
        )
        fig_role.update_traces(textposition="outside", cliponaxis=False)
        fig_role.update_layout(xaxis_title="응답 수", yaxis_title="")
        fig_role = style_fig(fig_role, height=300, legend=False, show_ygrid=False)
        st.plotly_chart(fig_role, width="stretch")

with col_right:
    with st.container(border=True):
        st.markdown("**NPS 분포 (0~10)**")
        nps_counts = df["NPS"].value_counts().reindex(range(11), fill_value=0)
        fig_nps = px.bar(
            x=nps_counts.index,
            y=nps_counts.values,
            text=nps_counts.values,
            color_discrete_sequence=WOKA_SEQ,
        )
        fig_nps.update_traces(textposition="outside", cliponaxis=False)
        fig_nps.update_layout(xaxis_title="점수", yaxis_title="응답 수")
        fig_nps.update_xaxes(dtick=1)
        fig_nps = style_fig(fig_nps, height=300, legend=False)
        st.plotly_chart(fig_nps, width="stretch")

# ── 응답 원본 + 내보내기 ─────────────────────────────
with st.container(border=True):
    st.markdown("**응답 원본**")
    st.dataframe(
        df.drop(columns=["도구수"]),
        width="stretch",
        hide_index=True,
    )

    b1, b2 = st.columns([3, 1])
    with b1:
        st.download_button(
            "응답 CSV 다운로드",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name="survey_responses.csv",
            mime="text/csv",
            width="stretch",
        )
    with b2:
        if st.button("응답 초기화", width="stretch"):
            st.session_state.responses = []
            st.rerun()

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

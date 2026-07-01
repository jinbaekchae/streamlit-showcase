"""⑨ 텍스트 분석기."""

import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import feature_note, footer

st.title("✍️ 텍스트 분석기")
st.caption("글을 입력하면 글자·단어·문장 수와 빈출 단어가 즉시 갱신됩니다. 입력하는 동안 실시간 분석합니다.")

SAMPLE = (
    "Streamlit은 파이썬만으로 데이터 웹앱을 만드는 도구입니다. "
    "복잡한 프런트엔드 지식 없이도 대시보드와 챗봇, 시각화 앱을 빠르게 만들 수 있습니다. "
    "코드를 저장하면 화면이 자동으로 갱신되고, 배포도 무료로 할 수 있습니다."
)

text = st.text_area("분석할 텍스트", value=SAMPLE, height=180)

# ── 기본 지표 ─────────────────────────────
chars = len(text)
chars_no_space = len(text.replace(" ", "").replace("\n", ""))
words = re.findall(r"[가-힣A-Za-z0-9]+", text)
sentences = [s for s in re.split(r"[.!?。\n]", text) if s.strip()]
reading_sec = int(len(words) / 200 * 60)  # 분당 200단어 기준

c1, c2, c3, c4 = st.columns(4)
c1.metric("글자 수", f"{chars:,}")
c2.metric("공백 제외", f"{chars_no_space:,}")
c3.metric("단어 수", f"{len(words):,}")
c4.metric("문장 수", f"{len(sentences):,}")

st.caption(f"예상 읽기 시간: 약 {reading_sec}초 (분당 200단어 기준)")

st.divider()

# ── 빈출 단어 ─────────────────────────────
STOP = {"은", "는", "이", "가", "을", "를", "에", "의", "도", "으로", "and", "the", "to", "of"}
meaningful = [w.lower() for w in words if len(w) > 1 and w.lower() not in STOP]

if meaningful:
    top = Counter(meaningful).most_common(15)
    freq = pd.DataFrame(top, columns=["단어", "빈도"])
    tab1, tab2 = st.tabs(["빈출 단어 차트", "빈도 표"])
    with tab1:
        fig = px.bar(freq, x="빈도", y="단어", orientation="h")
        fig.update_traces(marker_color="#ff6c00")
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0), height=420,
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig, width="stretch")
    with tab2:
        st.dataframe(freq, width="stretch", height=420)
else:
    st.info("분석할 단어가 없습니다. 텍스트를 입력해 주세요.")

feature_note(
    "텍스트 분석기",
    [
        "`st.text_area`: 입력이 바뀔 때마다 아래 지표·차트가 즉시 재계산",
        "`st.metric` 4열로 핵심 수치를 한눈에 배치",
        "`st.tabs`: 같은 결과를 차트/표 탭으로 나눠 제공",
        "표준 파이썬(정규식·Counter)만으로 분석 로직 구현",
    ],
)
footer()

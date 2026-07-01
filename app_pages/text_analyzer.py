"""⑨ 텍스트 분석기."""

import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.sample_data import review_sample
from utils.theme import ORANGE, style_fig
from utils.ui import feature_note, footer, page_header, section

page_header("✍️", "텍스트 분석기", "입력하는 즉시 통계와 빈출 단어가 갱신")

STOP = {
    "은", "는", "이", "가", "을", "를", "에", "의", "도", "으로", "와", "과",
    "고", "라", "만", "에서", "에게", "한", "그", "저", "것", "수", "때",
    "and", "the", "to", "of", "a", "in", "is", "for", "on",
}


def analyze(text: str):
    """텍스트에서 기본 지표와 정제된 토큰을 계산한다."""
    chars = len(text)
    chars_no_space = len(re.sub(r"\s", "", text))
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", text)
    sentences = [s for s in re.split(r"[.!?。\n]", text) if s.strip()]
    meaningful = [w.lower() for w in tokens if len(w) >= 2 and w.lower() not in STOP]
    return chars, chars_no_space, tokens, sentences, meaningful


with st.container(border=True):
    text = st.text_area(
        "분석할 텍스트",
        value=review_sample(),
        height=200,
        help="글을 수정하면 아래 지표와 차트가 즉시 다시 계산됩니다.",
    )

if not text.strip():
    st.info("분석할 텍스트를 입력해 주세요.")
    footer()
    st.stop()

chars, chars_no_space, tokens, sentences, meaningful = analyze(text)
reading_min = len(tokens) / 200  # 분당 200단어 기준

section("기본 지표")
c1, c2, c3, c4 = st.columns(4)
c1.metric("글자 수", f"{chars:,}")
c2.metric("공백 제외", f"{chars_no_space:,}", delta=f"공백 {chars - chars_no_space:,}자")
c3.metric("단어 수", f"{len(tokens):,}")
c4.metric("문장 수", f"{len(sentences):,}")

if reading_min < 1:
    read_label = f"약 {int(reading_min * 60)}초"
else:
    read_label = f"약 {reading_min:.1f}분"
st.caption(f"예상 읽기 시간: {read_label} (분당 200단어 기준)")

section("빈출 단어")
if meaningful:
    top = Counter(meaningful).most_common(15)
    freq = pd.DataFrame(top, columns=["단어", "빈도"])
    freq.insert(0, "순위", range(1, len(freq) + 1))

    tab_chart, tab_table = st.tabs(["차트", "빈도표"])
    with tab_chart:
        fig = px.bar(freq, x="빈도", y="단어", orientation="h", text="빈도")
        fig.update_traces(marker_color=ORANGE, textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        fig = style_fig(fig, height=460, legend=False)
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="")
        st.plotly_chart(fig, width="stretch")
    with tab_table:
        st.dataframe(
            freq,
            width="stretch",
            hide_index=True,
            height=460,
            column_config={
                "빈도": st.column_config.ProgressColumn(
                    "빈도",
                    format="%d",
                    min_value=0,
                    max_value=int(freq["빈도"].max()),
                ),
            },
        )
else:
    st.info("불용어를 제외하고 나면 집계할 단어가 없습니다.")

feature_note(
    "텍스트 분석기",
    [
        "`st.text_area`: 입력이 바뀔 때마다 지표·차트가 즉시 재계산",
        "`st.metric` 4열로 핵심 수치를 카드로 배치, delta 로 공백 수 표기",
        "`st.tabs`: 같은 결과를 차트/빈도표로 분리 제공",
        "`st.column_config.ProgressColumn`: 표 안에서 빈도를 막대로 시각화",
        "표준 파이썬(정규식·Counter)만으로 토큰화·불용어 제거 구현",
    ],
)
footer()

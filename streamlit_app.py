"""Streamlit 쇼케이스 진입점.

st.navigation / st.Page 로 홈 + 데모 10개를 하나의 앱으로 묶는다.
파일명은 영문으로 두고 표시 제목만 한국어로 지정해 배포 환경에서
한글 파일명이 깨지는 문제를 피한다.
"""

import streamlit as st

st.set_page_config(
    page_title="Streamlit 쇼케이스 · Woka",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "시작": [
        st.Page("app_pages/home.py", title="홈 · 개요", icon="🏠", default=True),
    ],
    "데모 10선": [
        st.Page("app_pages/dashboard.py", title="① 매출 대시보드", icon="📊"),
        st.Page("app_pages/explorer.py", title="② 데이터 탐색기", icon="🔎"),
        st.Page("app_pages/chatbot.py", title="③ 챗봇", icon="💬"),
        st.Page("app_pages/predictor.py", title="④ 예측 시뮬레이터", icon="🤖"),
        st.Page("app_pages/fx.py", title="⑤ 환율 대시보드", icon="💱"),
        st.Page("app_pages/image_lab.py", title="⑥ 이미지 편집기", icon="🖼️"),
        st.Page("app_pages/survey.py", title="⑦ 설문 폼", icon="📝"),
        st.Page("app_pages/map_view.py", title="⑧ 지도 시각화", icon="🗺️"),
        st.Page("app_pages/text_analyzer.py", title="⑨ 텍스트 분석기", icon="✍️"),
        st.Page("app_pages/roi.py", title="⑩ ROI 계산기", icon="🧮"),
    ],
}

pg = st.navigation(pages)
pg.run()

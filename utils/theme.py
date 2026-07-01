"""디자인 시스템: 색 토큰, 전역 CSS 주입, 통일된 Plotly 스타일.

streamlit_app.py 에서 inject_css() 를 한 번 호출하면 모든 페이지에 적용된다.
차트는 style_fig() 로 감싸 색·폰트·여백을 통일한다.
"""

# ── 색 토큰 ─────────────────────────────
ORANGE = "#ff6c00"
ORANGE_DARK = "#e05f00"
INK = "#1f2430"
MUTED = "#6b7280"
BORDER = "#ececf0"
SOFT = "#fbf7f3"

# 차트용 팔레트 (오렌지 중심 + 보조색)
WOKA_SEQ = ["#ff6c00", "#ff9a4d", "#2a9d8f", "#4c6ef5", "#f4a261", "#e76f51", "#8d99ae", "#ffc199"]

_CSS = """
<style>
/* 불필요한 기본 크롬 정리 */
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stAppDeployButton"] { display: none; }

/* 본문 여백·최대폭 */
[data-testid="stMainBlockContainer"] {
  padding-top: 2.2rem;
  padding-bottom: 3rem;
  max-width: 1180px;
}

/* 사이드바 */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #fbf7f3 100%);
  border-right: 1px solid #ececf0;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: rgba(255,108,0,0.12);
  border-radius: 10px;
}

/* 히어로 헤더 */
.woka-hero {
  display: flex; align-items: center; gap: 18px;
  padding: 22px 26px; margin-bottom: 18px;
  background: linear-gradient(120deg, #fff3e9 0%, #fff8f2 55%, #ffffff 100%);
  border: 1px solid #ffe0c7; border-radius: 18px;
}
.woka-hero-icon {
  font-size: 34px; line-height: 1;
  width: 60px; height: 60px; flex: none;
  display: flex; align-items: center; justify-content: center;
  background: #ffffff; border: 1px solid #ffe0c7; border-radius: 16px;
  box-shadow: 0 4px 14px rgba(255,108,0,0.12);
}
.woka-hero-title { font-size: 26px; font-weight: 700; color: #1f2430; letter-spacing: -0.02em; }
.woka-hero-sub { font-size: 15px; color: #6b7280; margin-top: 4px; }

/* 섹션 헤더 */
.woka-section {
  display: flex; align-items: center; gap: 10px;
  font-size: 17px; font-weight: 700; color: #1f2430;
  margin: 10px 0 6px;
}
.woka-section .bar { width: 4px; height: 18px; background: #ff6c00; border-radius: 4px; }

/* 지표(metric) 카드화 */
[data-testid="stMetric"] {
  background: #ffffff; border: 1px solid #ececf0; border-radius: 14px;
  padding: 14px 16px; box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}
[data-testid="stMetricLabel"] p { color: #6b7280; font-weight: 500; }
[data-testid="stMetricValue"] { font-weight: 700; letter-spacing: -0.02em; }

/* 버튼 */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 10px; font-weight: 600; border: 1px solid #ececf0;
  transition: transform .05s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  box-shadow: 0 3px 10px rgba(255,108,0,0.18); transform: translateY(-1px);
}

/* 카드형 콘텐츠 컨테이너 (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 16px !important; border-color: #ececf0 !important;
}

/* 탭 */
[data-testid="stTabs"] button[aria-selected="true"] { color: #e05f00; }

/* expander 다듬기 */
[data-testid="stExpander"] details {
  border: 1px solid #ececf0; border-radius: 12px; background: #ffffff;
}

/* 데이터프레임 라운드 */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 12px; overflow: hidden; }

/* 푸터 배지 */
.woka-footer {
  margin-top: 8px; color: #9aa1ac; font-size: 12.5px; text-align: center;
}
</style>
"""


def inject_css() -> None:
    """전역 CSS 를 주입한다. 앱 진입점에서 1회 호출."""
    import streamlit as st

    st.markdown(_CSS, unsafe_allow_html=True)


def style_fig(fig, height: int = 340, legend: bool = True, show_ygrid: bool = True):
    """모든 Plotly 차트에 공통 스타일(폰트·색·여백)을 입힌다."""
    fig.update_layout(
        font=dict(family="Pretendard, sans-serif", size=13, color=INK),
        title=dict(font=dict(size=15, color=INK)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=34, b=8),
        height=height,
        colorway=WOKA_SEQ,
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Pretendard"),
    )
    if legend:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text="")
        )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor=BORDER, tickcolor=BORDER)
    fig.update_yaxes(showgrid=show_ygrid, gridcolor="#f2f3f6", zeroline=False)
    return fig

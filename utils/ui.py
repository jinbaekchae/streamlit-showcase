"""페이지 공용 UI 컴포넌트."""

import html

import streamlit as st


def page_header(icon: str, title: str, subtitle: str) -> None:
    """페이지 상단 히어로 헤더."""
    st.markdown(
        f"""
        <div class="woka-hero">
          <div class="woka-hero-icon">{icon}</div>
          <div>
            <div class="woka-hero-title">{html.escape(title)}</div>
            <div class="woka-hero-sub">{html.escape(subtitle)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(text: str) -> None:
    """왼쪽 오렌지 바가 붙은 섹션 헤더."""
    st.markdown(
        f'<div class="woka-section"><span class="bar"></span>{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def feature_note(title: str, items: list[str]) -> None:
    """이 데모가 보여주는 스트림릿 기능을 접이식 영역으로 정리한다."""
    with st.expander(f"🧩 이 데모가 보여주는 스트림릿 기능 — {title}"):
        for it in items:
            st.markdown(f"- {it}")


def footer() -> None:
    """모든 페이지 하단의 Woka 저작권 표기."""
    st.markdown('<div class="woka-footer">© Woka. All Rights Reserved</div>', unsafe_allow_html=True)

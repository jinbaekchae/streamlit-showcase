"""페이지 공용 UI 조각."""

import streamlit as st


def feature_note(title: str, items: list[str]) -> None:
    """이 데모가 보여주는 스트림릿 기능을 접이식 영역으로 정리한다."""
    with st.expander(f"🧩 이 데모가 보여주는 스트림릿 기능 — {title}"):
        for it in items:
            st.markdown(f"- {it}")


def footer() -> None:
    """모든 페이지 하단에 들어가는 Woka 저작권 표기."""
    st.divider()
    st.caption("© Woka. All Rights Reserved")

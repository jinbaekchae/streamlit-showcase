"""③ 챗봇."""

import time

import streamlit as st

from utils.ui import feature_note, footer

st.title("💬 챗봇")
st.caption("채팅 UI가 기본 제공됩니다. 대화 기록 유지와 글자가 흘러나오는 스트리밍을 보여줍니다.")

# 규칙 기반 응답 사전 (실제로는 이 자리에 Claude API 호출을 넣으면 됩니다)
FAQ = {
    ("배포", "deploy", "올리"): "Streamlit Community Cloud에 GitHub 저장소를 연결하면 무료로 배포됩니다. 코드를 push 하면 자동으로 다시 배포됩니다.",
    ("캐시", "cache", "느"): "무거운 계산은 `@st.cache_data`, 모델·연결 같은 자원은 `@st.cache_resource` 로 감싸면 한 번만 실행하고 재사용합니다.",
    ("상태", "session", "기억"): "`st.session_state` 라는 딕셔너리에 값을 넣으면 화면이 다시 실행돼도 값이 유지됩니다. 이 대화 기록도 거기에 저장됩니다.",
    ("차트", "그래프", "chart"): "`st.line_chart` 같은 기본 차트부터 Plotly·Altair 같은 인터랙티브 라이브러리까지 한 줄로 붙일 수 있습니다.",
    ("가격", "비용", "무료"): "개인·공개 앱은 Streamlit Community Cloud에서 무료로 배포할 수 있습니다.",
}

DEFAULT = (
    "저는 이 데모에 넣은 간단한 규칙 기반 도우미입니다. "
    "'배포', '캐시', '상태', '차트', '비용' 같은 단어를 넣어 물어보시면 관련 설명을 드립니다. "
    "이 자리에 Claude API를 연결하면 진짜 대화형 AI 챗봇이 됩니다."
)


def answer(text: str) -> str:
    for keys, resp in FAQ.items():
        if any(k in text for k in keys):
            return resp
    return DEFAULT


def stream(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요. Streamlit에 대해 궁금한 점을 물어보세요."}
    ]

# 지금까지의 대화 다시 그리기
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 새 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = st.write_stream(stream(answer(prompt)))
    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    if st.button("대화 초기화"):
        del st.session_state.messages
        st.rerun()

st.divider()
st.code(
    '''# 이 자리에 Claude API를 넣으면 진짜 AI 챗봇이 됩니다
from anthropic import Anthropic
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
resp = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=st.session_state.messages,
)''',
    language="python",
)

feature_note(
    "챗봇",
    [
        "`st.chat_message` / `st.chat_input`: 채팅 화면 요소를 기본 제공",
        "`st.session_state`: 화면이 다시 실행돼도 대화 기록을 유지",
        "`st.write_stream`: 글자가 한 조각씩 흘러나오는 스트리밍 출력",
        "`st.secrets`: API 키 같은 비밀값을 코드에 노출하지 않고 사용",
    ],
)
footer()

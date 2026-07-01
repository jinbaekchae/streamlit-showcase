"""③ 챗봇 — 채팅 UI·대화 기록 유지·스트리밍 데모."""

import time

import streamlit as st

from utils.ui import feature_note, footer, page_header, section

page_header("💬", "챗봇", "채팅 UI·대화 기록 유지·스트리밍이 기본 제공")

st.markdown(
    "몇 줄의 코드로 대화형 화면을 구성합니다. 아래 예시 질문을 누르거나 직접 입력하면 "
    "규칙 기반 도우미가 관련 안내를 스트리밍으로 답변합니다."
)

# ── 규칙 기반 응답 사전 (이 자리에 Claude API 호출을 넣으면 실제 AI 챗봇이 됩니다) ──
FAQ = {
    ("배포", "deploy", "올리"): (
        "Streamlit Community Cloud에 GitHub 저장소를 연결하면 무료로 배포됩니다. "
        "코드를 push 하면 자동으로 다시 배포됩니다."
    ),
    ("캐시", "cache", "느"): (
        "무거운 계산은 `@st.cache_data`, 모델·연결 같은 자원은 `@st.cache_resource` 로 "
        "감싸면 한 번만 실행하고 재사용합니다."
    ),
    ("상태", "session", "기억"): (
        "`st.session_state` 라는 딕셔너리에 값을 넣으면 화면이 다시 실행돼도 값이 유지됩니다. "
        "이 대화 기록도 거기에 저장됩니다."
    ),
    ("차트", "그래프", "chart"): (
        "`st.line_chart` 같은 기본 차트부터 Plotly·Altair 같은 인터랙티브 라이브러리까지 "
        "한 줄로 붙일 수 있습니다."
    ),
    ("가격", "비용", "무료"): (
        "개인·공개 앱은 Streamlit Community Cloud에서 무료로 배포할 수 있습니다."
    ),
    ("데이터", "data", "표"): (
        "`st.dataframe` 로 표를 인터랙티브하게 보여주고, `pandas` 로 불러온 데이터를 "
        "그대로 화면에 연결할 수 있습니다."
    ),
}

DEFAULT = (
    "저는 이 데모에 넣은 규칙 기반 도우미입니다. "
    "'배포', '캐시', '상태', '차트', '비용', '데이터' 같은 단어를 넣어 물어보시면 관련 설명을 드립니다. "
    "이 자리에 Claude API 키를 넣으면 실제 대화형 AI 챗봇이 됩니다."
)

GREETING = "안녕하세요. Streamlit에 대해 궁금한 점을 물어보세요."

EXAMPLES = [
    "배포는 어떻게 하나요?",
    "캐시가 뭔가요?",
    "차트도 그릴 수 있나요?",
    "데이터 표는 어떻게 보여주죠?",
]


def answer(text: str) -> str:
    """키워드를 찾아 안내 문구를 돌려줍니다."""
    for keys, resp in FAQ.items():
        if any(k in text for k in keys):
            return resp
    return DEFAULT


def stream(text: str):
    """단어 단위로 흘려보내는 스트리밍 제너레이터."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def ensure_messages():
    """세션 상태가 비어 있으면 인사말로 초기화합니다(초기화 후 KeyError 방어)."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": GREETING}]


ensure_messages()

# ── 예시 질문 버튼 ─────────────────────────────
pending = None
with st.container(border=True):
    st.markdown("**예시 질문**")
    cols = st.columns(len(EXAMPLES))
    for col, q in zip(cols, EXAMPLES):
        if col.button(q, key=f"ex_{q}", width="stretch"):
            pending = q

# ── 대화 지표 ─────────────────────────────
user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
c1, c2, c3 = st.columns(3)
c1.metric("주고받은 메시지", f"{len(st.session_state.messages)}건")
c2.metric("내 질문 수", f"{user_turns}건")
c3.metric("응답 주제", f"{len(FAQ)}개")

# ── 대화 영역 ─────────────────────────────
section("대화")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# chat_input 또는 예시 버튼에서 들어온 입력 처리
typed = st.chat_input("메시지를 입력하세요")
prompt = typed or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = st.write_stream(stream(answer(prompt)))
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ── 사이드바: 대화 초기화 ─────────────────────────────
with st.sidebar:
    section("챗봇 설정")
    if st.button("대화 초기화", width="stretch"):
        st.session_state.pop("messages", None)
        st.rerun()

# ── 실제 AI 연결 예시 ─────────────────────────────
section("Claude API 연결 예시")
st.markdown("규칙 기반 응답 자리를 아래 코드로 바꾸면 실제 대화형 AI 챗봇이 됩니다.")
st.code(
    '''from anthropic import Anthropic

client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
resp = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    # 첫 인사말(assistant)은 제외하고 전달합니다.
    # Anthropic 메시지 API는 첫 메시지 역할이 user 여야 합니다.
    messages=st.session_state.messages[1:],
)
reply = resp.content[0].text''',
    language="python",
)

feature_note(
    "챗봇",
    [
        "`st.chat_message` / `st.chat_input`: 채팅 화면 요소를 기본 제공",
        "`st.session_state`: 화면이 다시 실행돼도 대화 기록을 유지",
        "`st.write_stream`: 글자가 한 조각씩 흘러나오는 스트리밍 출력",
        "`st.secrets`: API 키 같은 비밀값을 코드에 노출하지 않고 사용",
        "`st.columns` + `st.button`: 예시 질문을 눌러 바로 대화 시작",
    ],
)
footer()

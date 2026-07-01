"""⑥ 이미지 편집기."""

import io

import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from utils.ui import feature_note, footer

st.title("🖼️ 이미지 편집기")
st.caption("이미지를 올리고 필터를 적용한 뒤 결과를 내려받습니다. 미디어 처리도 파이썬으로 합니다.")


@st.cache_data
def sample_image() -> Image.Image:
    """업로드가 없을 때 쓸 예시 이미지를 그려서 만든다."""
    img = Image.new("RGB", (640, 400), "#fff6ef")
    d = ImageDraw.Draw(img)
    for i in range(0, 640, 40):
        d.line([(i, 0), (i, 400)], fill="#ffd0a8", width=2)
    d.ellipse([180, 90, 460, 310], fill="#ff6c00")
    d.rectangle([250, 160, 390, 240], fill="#ffffff")
    return img


uploaded = st.file_uploader("이미지 업로드 (없으면 예시 이미지 사용)", type=["png", "jpg", "jpeg"])
src = Image.open(uploaded).convert("RGB") if uploaded else sample_image()

with st.sidebar:
    st.header("필터")
    gray = st.checkbox("흑백")
    blur = st.slider("흐림 정도", 0, 10, 0)
    bright = st.slider("밝기", 0.2, 2.0, 1.0, step=0.1)
    contrast = st.slider("대비", 0.2, 2.0, 1.0, step=0.1)
    rotate = st.slider("회전(도)", 0, 360, 0, step=15)

out = src
if gray:
    out = out.convert("L").convert("RGB")
if blur:
    out = out.filter(ImageFilter.GaussianBlur(blur))
if bright != 1.0:
    out = ImageEnhance.Brightness(out).enhance(bright)
if contrast != 1.0:
    out = ImageEnhance.Contrast(out).enhance(contrast)
if rotate:
    out = out.rotate(-rotate, expand=True, fillcolor="#ffffff")

left, right = st.columns(2)
left.markdown("**원본**")
left.image(src, width="stretch")
right.markdown("**결과**")
right.image(out, width="stretch")

buf = io.BytesIO()
out.save(buf, format="PNG")
st.download_button(
    "결과 이미지 다운로드 (PNG)",
    buf.getvalue(),
    file_name="edited.png",
    mime="image/png",
)

feature_note(
    "이미지 편집기",
    [
        "`st.file_uploader`: 사용자가 파일을 올리면 즉시 파이썬에서 처리",
        "Pillow(PIL)로 흑백·흐림·밝기·대비·회전 등 이미지 가공",
        "`st.image`: 두 열로 원본/결과 나란히 표시",
        "`st.download_button`: 가공한 이미지를 파일로 내려받기",
    ],
)
footer()

"""⑥ 이미지 편집기."""

import io

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from utils.ui import feature_note, footer, page_header, section

W, H = 640, 400


@st.cache_data
def sample_gradient() -> Image.Image:
    """가로·세로 선형 보간으로 만든 오렌지 그라디언트."""
    top_left = np.array([255, 137, 51], dtype=float)
    top_right = np.array([255, 108, 0], dtype=float)
    bot_left = np.array([255, 214, 170], dtype=float)
    bot_right = np.array([224, 95, 0], dtype=float)

    fx = np.linspace(0, 1, W)[None, :, None]
    fy = np.linspace(0, 1, H)[:, None, None]
    top = top_left * (1 - fx) + top_right * fx
    bot = bot_left * (1 - fx) + bot_right * fx
    arr = top * (1 - fy) + bot * fy
    return Image.fromarray(arr.astype("uint8"), "RGB")


@st.cache_data
def sample_geometric() -> Image.Image:
    """흰 배경에 오렌지 계열 원·사각형을 배치한 기하학 패턴."""
    img = Image.new("RGB", (W, H), "#fffaf5")
    d = ImageDraw.Draw(img, "RGBA")
    palette = [
        (255, 108, 0, 210),
        (255, 154, 77, 210),
        (255, 193, 153, 210),
        (224, 95, 0, 210),
        (255, 214, 170, 230),
    ]
    rng = np.random.default_rng(7)
    for _ in range(9):
        cx, cy = rng.integers(60, W - 60), rng.integers(60, H - 60)
        r = rng.integers(40, 110)
        color = palette[rng.integers(0, len(palette))]
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    for _ in range(6):
        x0, y0 = rng.integers(20, W - 160), rng.integers(20, H - 120)
        w, h = rng.integers(70, 170), rng.integers(60, 130)
        color = palette[rng.integers(0, len(palette))]
        d.rectangle([x0, y0, x0 + w, y0 + h], outline=color, width=8)
    return img


@st.cache_data
def sample_duotone() -> Image.Image:
    """밝기 그라디언트를 두 색 사이에서 보간한 듀오톤 노을."""
    shadow = np.array([46, 26, 71], dtype=float)   # 짙은 보라
    light = np.array([255, 154, 77], dtype=float)   # 노을 오렌지

    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    # 대각선 방향 밝기 + 부드러운 곡선
    lum = np.clip(0.65 * yy + 0.35 * xx, 0, 1)
    lum = lum ** 1.4
    lum = lum[:, :, None]
    arr = shadow * (1 - lum) + light * lum
    return Image.fromarray(arr.astype("uint8"), "RGB")


SAMPLES = {
    "오렌지 그라디언트": sample_gradient,
    "기하학 패턴": sample_geometric,
    "듀오톤 노을": sample_duotone,
}


page_header("🖼️", "이미지 편집기", "이미지 업로드·필터 적용·결과 다운로드")

# ── 사이드바 필터 ───────────────────────────
with st.sidebar:
    st.header("필터")
    gray = st.checkbox("흑백")
    blur = st.slider("흐림 정도", 0, 10, 0)
    bright = st.slider("밝기", 0.2, 2.0, 1.0, step=0.1)
    contrast = st.slider("대비", 0.2, 2.0, 1.0, step=0.1)
    rotate = st.slider("회전(도)", 0, 360, 0, step=15)

# ── 입력 선택 ──────────────────────────────
section("이미지 선택")
with st.container(border=True):
    uploaded = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
    if uploaded is None:
        sample_name = st.selectbox("내장 샘플 이미지", list(SAMPLES.keys()))
        st.caption("파일을 올리면 업로드한 이미지가 우선 적용됩니다.")

if uploaded is not None:
    src = Image.open(uploaded).convert("RGB")
    src_label = uploaded.name
else:
    src = SAMPLES[sample_name]()
    src_label = f"내장 샘플 · {sample_name}"

# ── 필터 적용 ──────────────────────────────
applied = []
out = src
if gray:
    out = out.convert("L").convert("RGB")
    applied.append("흑백")
if blur:
    out = out.filter(ImageFilter.GaussianBlur(blur))
    applied.append(f"흐림 {blur}")
if bright != 1.0:
    out = ImageEnhance.Brightness(out).enhance(bright)
    applied.append(f"밝기 {bright:.1f}")
if contrast != 1.0:
    out = ImageEnhance.Contrast(out).enhance(contrast)
    applied.append(f"대비 {contrast:.1f}")
if rotate:
    out = out.rotate(-rotate, expand=True, fillcolor="#ffffff")
    applied.append(f"회전 {rotate}°")

# ── 요약 지표 ──────────────────────────────
buf = io.BytesIO()
out.save(buf, format="PNG")
png_bytes = buf.getvalue()

c1, c2, c3 = st.columns(3)
c1.metric("적용 필터 수", f"{len(applied)}개")
c2.metric(
    "결과 해상도",
    f"{out.width}×{out.height}",
    delta=None if (out.width, out.height) == (src.width, src.height) else "회전 반영",
)
c3.metric("PNG 용량", f"{len(png_bytes) / 1024:.0f} KB")

if applied:
    st.caption("적용 순서: " + " → ".join(applied))
else:
    st.caption("적용된 필터가 없어 원본과 동일한 결과입니다.")

# ── 원본 / 결과 비교 ────────────────────────
section("원본 · 결과 비교")
left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.markdown("**원본**")
        st.caption(src_label)
        st.image(src, width="stretch")
with right:
    with st.container(border=True):
        st.markdown("**결과**")
        st.caption(", ".join(applied) if applied else "필터 미적용")
        st.image(out, width="stretch")

# ── 다운로드 ───────────────────────────────
section("결과 저장")
st.download_button(
    "결과 이미지 다운로드 (PNG)",
    png_bytes,
    file_name="edited.png",
    mime="image/png",
    width="stretch",
)

feature_note(
    "이미지 편집기",
    [
        "`st.file_uploader`: 업로드한 파일을 즉시 파이썬에서 처리",
        "업로드가 없으면 numpy·Pillow 로 생성한 내장 샘플 3종 제공",
        "Pillow(PIL) 로 흑백·흐림·밝기·대비·회전 필터 적용",
        "`st.image` 두 열 배치로 원본·결과 나란히 비교",
        "`st.download_button`: 가공 결과를 PNG 로 내려받기",
    ],
)
footer()

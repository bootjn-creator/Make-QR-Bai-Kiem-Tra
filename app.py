from __future__ import annotations

import io
import re
from urllib.parse import urlparse

import qrcode
import streamlit as st
from PIL import Image, ImageDraw


QR_THEMES = {
    "Hồng nổi bật": "#D81B60",
    "Tím hiện đại": "#6D28D9",
    "Xanh học đường": "#2563EB",
    "Xanh ngọc": "#00796B",
}

QUALITY_OPTIONS = {
    "Tiêu chuẩn": 14,
    "Chất lượng cao": 20,
    "Dùng để in ấn": 28,
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def normalize_url(value: str) -> str:
    value = value.strip()
    if value and "://" not in value:
        value = "https://" + value
    return value


def is_valid_web_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
            and "." in parsed.netloc
        )
    except ValueError:
        return False


def safe_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[^\w\- ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "_", value)
    value = value.strip("._-")
    return value or "qr_bai_kiem_tra"


def is_finder_module(row: int, col: int, size: int, border: int) -> bool:
    start = border
    end = size - border

    top_left = start <= row < start + 7 and start <= col < start + 7
    top_right = start <= row < start + 7 and end - 7 <= col < end
    bottom_left = end - 7 <= row < end and start <= col < start + 7

    return top_left or top_right or bottom_left


def create_modern_qr(
    data: str,
    qr_color: tuple[int, int, int],
    box_size: int,
) -> Image.Image:
    border = 4

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    matrix_size = len(matrix)
    image_size = matrix_size * box_size

    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image)
    dot_margin = max(1, round(box_size * 0.10))

    for row in range(matrix_size):
        for col in range(matrix_size):
            if not matrix[row][col]:
                continue

            left = col * box_size
            top = row * box_size
            right = left + box_size - 1
            bottom = top + box_size - 1

            if is_finder_module(row, col, matrix_size, border):
                draw.rounded_rectangle(
                    (left, top, right, bottom),
                    radius=max(1, box_size // 7),
                    fill=qr_color,
                )
            else:
                draw.ellipse(
                    (
                        left + dot_margin,
                        top + dot_margin,
                        right - dot_margin,
                        bottom - dot_margin,
                    ),
                    fill=qr_color,
                )

    return image


def image_to_png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


st.set_page_config(
    page_title="Tạo mã QR Bài kiểm tra",
    page_icon="📝",
    layout="centered",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(255, 79, 135, 0.10), transparent 28%),
                radial-gradient(circle at 88% 12%, rgba(109, 40, 217, 0.09), transparent 30%),
                linear-gradient(180deg, #fffafd 0%, #ffffff 46%, #fff9fc 100%);
        }

        .block-container {
            max-width: 880px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            text-align: center;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(216, 27, 96, 0.13);
            border-radius: 28px;
            padding: 2rem 1.2rem 1.7rem 1.2rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 18px 50px rgba(82, 29, 73, 0.08);
        }

        .hero::before,
        .hero::after {
            content: "";
            position: absolute;
            width: 125px;
            height: 125px;
            border-radius: 32px;
            transform: rotate(18deg);
            opacity: 0.10;
        }

        .hero::before {
            background: #ff4f87;
            top: -56px;
            left: -42px;
        }

        .hero::after {
            background: #6d28d9;
            right: -44px;
            bottom: -64px;
        }

        .eyebrow {
            color: #7c3aed;
            font-size: 0.86rem;
            font-weight: 800;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .exam-title {
            display: inline-block;
            margin: 0;
            font-size: clamp(2.35rem, 7vw, 4.5rem);
            line-height: 1;
            font-weight: 950;
            letter-spacing: -0.045em;
            background: linear-gradient(105deg, #d81b60 4%, #ff4f87 40%, #7c3aed 88%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 7px 18px rgba(216, 27, 96, 0.14));
        }

        .exam-subtitle {
            max-width: 620px;
            margin: 0.9rem auto 0 auto;
            color: #5f6470;
            font-size: 1rem;
            line-height: 1.65;
        }

        .feature-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.55rem;
            margin-top: 1.1rem;
        }

        .feature-chip {
            background: #fff4f8;
            border: 1px solid #ffd7e6;
            color: #a91652;
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            font-size: 0.82rem;
            font-weight: 700;
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #eedde6;
            border-radius: 22px;
            padding: 1.3rem 1.3rem 0.45rem 1.3rem;
            box-shadow: 0 12px 32px rgba(71, 33, 65, 0.07);
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            min-height: 3rem;
            border: 0;
            border-radius: 12px;
            font-weight: 850;
            letter-spacing: 0.025em;
            box-shadow: 0 9px 22px rgba(216, 27, 96, 0.18);
        }

        .privacy-note {
            text-align: center;
            color: #7b7280;
            font-size: 0.86rem;
            margin-top: 1.2rem;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .hero {
                border-radius: 22px;
                padding-top: 1.6rem;
            }

            .exam-title {
                letter-spacing: -0.035em;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Tạo mã QR nhanh</div>
        <h1 class="exam-title">BÀI KIỂM TRA</h1>
        <p class="exam-subtitle">
            Tạo mã QR cho biểu mẫu, bài tập, bài kiểm tra trực tuyến
            và các đường liên kết học tập chỉ trong vài giây.
        </p>
        <div class="feature-row">
            <span class="feature-chip">Không cần cài đặt</span>
            <span class="feature-chip">Tải ảnh PNG</span>
            <span class="feature-chip">Dễ quét trên điện thoại</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.form("qr_form"):
    url_input = st.text_input(
        "Đường liên kết bài kiểm tra",
        placeholder="Ví dụ: https://forms.gle/...",
        help="Có thể nhập liên kết có hoặc chưa có phần https://",
    )

    filename_input = st.text_input(
        "Tên tệp khi tải xuống",
        value="qr_bai_kiem_tra",
        help="Không cần nhập đuôi .png",
    )

    col1, col2 = st.columns(2)

    with col1:
        theme_name = st.selectbox(
            "Màu mã QR",
            options=list(QR_THEMES.keys()),
            index=0,
        )

    with col2:
        quality_label = st.selectbox(
            "Chất lượng ảnh",
            options=list(QUALITY_OPTIONS.keys()),
            index=1,
        )

    submitted = st.form_submit_button(
        "TẠO MÃ QR",
        type="primary",
        use_container_width=True,
    )

if submitted:
    normalized_url = normalize_url(url_input)

    if not normalized_url:
        st.error("Vui lòng nhập đường liên kết bài kiểm tra.")
    elif not is_valid_web_url(normalized_url):
        st.error(
            "Đường liên kết chưa hợp lệ. Vui lòng nhập theo dạng "
            "https://tenmien.vn"
        )
    else:
        try:
            qr_image = create_modern_qr(
                data=normalized_url,
                qr_color=hex_to_rgb(QR_THEMES[theme_name]),
                box_size=QUALITY_OPTIONS[quality_label],
            )

            st.session_state["qr_png"] = image_to_png_bytes(qr_image)
            st.session_state["qr_filename"] = safe_filename(filename_input) + ".png"
            st.session_state["qr_url"] = normalized_url
            st.session_state["qr_theme"] = theme_name

            st.success("Đã tạo mã QR thành công.")
        except Exception as exc:
            st.error(f"Không thể tạo mã QR. Chi tiết lỗi: {exc}")

if "qr_png" in st.session_state:
    st.subheader("Xem trước mã QR")

    left, center, right = st.columns([1, 3, 1])
    with center:
        st.image(st.session_state["qr_png"], use_container_width=True)

    st.caption(
        f"Liên kết đã mã hóa: {st.session_state['qr_url']}  •  "
        f"Màu: {st.session_state['qr_theme']}"
    )

    st.download_button(
        label="TẢI MÃ QR ĐỊNH DẠNG PNG",
        data=st.session_state["qr_png"],
        file_name=st.session_state["qr_filename"],
        mime="image/png",
        type="primary",
        use_container_width=True,
    )

st.markdown(
    '<div class="privacy-note">'
    "Ứng dụng tạo ảnh trực tiếp trong phiên làm việc và không lưu đường liên kết vào cơ sở dữ liệu."
    "</div>",
    unsafe_allow_html=True,
)

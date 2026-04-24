from __future__ import annotations

import io

import requests
from PIL import Image as PILImage
from PIL import ImageDraw
from reportlab.platypus import Image


MAX_IMAGE_WIDTH = 1400
MAX_IMAGE_HEIGHT = 1000
JPEG_QUALITY = 65


def download_image(url: str) -> io.BytesIO | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        buffer = io.BytesIO(response.content)
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def optimize_image_buffer(
    img: PILImage.Image,
    *,
    max_width: int = MAX_IMAGE_WIDTH,
    max_height: int = MAX_IMAGE_HEIGHT,
    quality: int = JPEG_QUALITY,
) -> io.BytesIO:
    img = img.convert("RGB")
    img.thumbnail((max_width, max_height))

    output = io.BytesIO()
    img.save(
        output,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
    )
    output.seek(0)
    return output


def create_image(img_buffer: io.BytesIO, max_width: float, max_height: float) -> Image:
    img_buffer.seek(0)

    try:
        pil_img = PILImage.open(img_buffer)
        optimized_buffer = optimize_image_buffer(pil_img)
    except Exception:
        optimized_buffer = img_buffer

    optimized_buffer.seek(0)
    img = Image(optimized_buffer)

    ratio = img.imageWidth / img.imageHeight
    img.drawWidth = max_width
    img.drawHeight = max_width / ratio

    if img.drawHeight > max_height:
        img.drawHeight = max_height
        img.drawWidth = max_height * ratio

    return img


def annotate_photo_with_damages(photo) -> io.BytesIO | None:
    img_buffer = download_image(photo.file_url)
    if img_buffer is None:
        return None

    try:
        img = PILImage.open(img_buffer).convert("RGBA")
    except Exception:
        return None

    damages = getattr(photo, "damages", None) or []

    if damages:
        draw = ImageDraw.Draw(img)
        width, height = img.size

        severity_colors = {
            "minor": (245, 158, 11, 255),
            "moderate": (249, 115, 22, 255),
            "severe": (239, 68, 68, 255),
        }

        default_color = (59, 130, 246, 255)
        radius = max(8, int(min(width, height) * 0.018))

        for index, damage in enumerate(damages, start=1):
            try:
                x_percent = float(getattr(damage, "x_percent", 0))
                y_percent = float(getattr(damage, "y_percent", 0))
            except Exception:
                continue

            x = max(0, min(width, int(width * x_percent / 100)))
            y = max(0, min(height, int(height * y_percent / 100)))

            severity_raw = getattr(damage, "severity", None)
            severity_value = getattr(severity_raw, "value", severity_raw)
            severity_key = str(severity_value).lower() if severity_value is not None else ""
            color = severity_colors.get(severity_key, default_color)

            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                outline=(255, 255, 255, 255),
                width=3,
                fill=color,
            )

            label_radius = int(radius * 0.72)
            label_x1 = x + radius - label_radius
            label_y1 = y - radius - label_radius
            label_x2 = x + radius + label_radius
            label_y2 = y - radius + label_radius

            draw.ellipse(
                (label_x1, label_y1, label_x2, label_y2),
                fill=(17, 24, 39, 230),
                outline=(255, 255, 255, 255),
                width=2,
            )

            text = str(index)
            text_pos = (label_x1 + label_radius - 4, label_y1 + label_radius - 6)
            draw.text(text_pos, text, fill=(255, 255, 255, 255))

    return optimize_image_buffer(img)
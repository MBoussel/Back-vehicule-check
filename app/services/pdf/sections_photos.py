from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.models.check import Check
from app.services.pdf.images import annotate_photo_with_damages, create_image
from app.services.pdf.sections_common import build_section_title
from app.services.pdf.utils import (
    build_damage_summary,
    get_photo_type_value,
    group_photos_by_type,
    normalize_damage_type_label,
    normalize_severity_label,
    translate_photo_label,
)


def build_single_damage_table(photo) -> Table:
    rows = build_damage_summary(photo)

    table = Table(rows, colWidths=[1.0 * cm, 4.0 * cm, 3.2 * cm, 7.6 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_photo_cell(photo, title: str, styles) -> list[Any]:
    photo_text_style = styles["Normal"]
    photo_title_style = ParagraphStyle(
        "PhotoCellTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )

    content: list[Any] = [Paragraph(title, photo_title_style), Spacer(1, 0.12 * cm)]

    if photo is None:
        content.append(Paragraph("Photo indisponible.", photo_text_style))
        return content

    annotated_buffer = annotate_photo_with_damages(photo)

    if annotated_buffer:
        try:
            img = create_image(annotated_buffer, 7.0 * cm, 4.6 * cm)
            content.append(img)
        except Exception:
            content.append(Paragraph("Image indisponible.", photo_text_style))
    else:
        content.append(Paragraph("Image indisponible.", photo_text_style))

    damages = getattr(photo, "damages", None) or []
    content.append(Spacer(1, 0.12 * cm))

    if damages:
        small_rows = [["#", "Type", "Gravité"]]
        for index, damage in enumerate(damages, start=1):
            small_rows.append(
                [
                    str(index),
                    normalize_damage_type_label(damage),
                    normalize_severity_label(damage),
                ]
            )

        small_table = Table(small_rows, colWidths=[0.8 * cm, 3.1 * cm, 2.6 * cm])
        small_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        content.append(small_table)
    else:
        content.append(Paragraph("Aucun dégât signalé.", photo_text_style))

    return content


def build_photo_comparison_grid(
    check: Check,
    previous_departure: Check | None,
    styles,
) -> list[Any]:
    elements: list[Any] = []

    elements.append(build_section_title("Comparaison visuelle départ / retour", styles))

    if previous_departure is None:
        elements.append(Paragraph("Aucun check de départ disponible pour la comparaison.", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    departure_photos = group_photos_by_type(previous_departure)
    return_photos = group_photos_by_type(check)

    ordered_types: list[str] = []

    for photo in sorted(previous_departure.photos or [], key=lambda item: item.display_order):
        photo_type = get_photo_type_value(photo)
        if photo_type not in ordered_types:
            ordered_types.append(photo_type)

    for photo in sorted(check.photos or [], key=lambda item: item.display_order):
        photo_type = get_photo_type_value(photo)
        if photo_type not in ordered_types:
            ordered_types.append(photo_type)

    for photo_type in ordered_types:
        section_label = translate_photo_label(photo_type)

        elements.append(
            Paragraph(
                section_label,
                ParagraphStyle(
                    "ComparePhotoTypeTitle",
                    parent=styles["Heading3"],
                    fontName="Helvetica-Bold",
                    fontSize=11,
                    textColor=colors.HexColor("#111827"),
                    spaceBefore=4,
                    spaceAfter=6,
                ),
            )
        )

        departure_photo = departure_photos.get(photo_type)
        return_photo = return_photos.get(photo_type)

        compare_table = Table(
            [[build_photo_cell(departure_photo, "Départ", styles), build_photo_cell(return_photo, "Retour", styles)]],
            colWidths=[8.0 * cm, 8.0 * cm],
        )
        compare_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E2E8F0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(compare_table)
        elements.append(Spacer(1, 0.35 * cm))

    return elements


def build_photo_grid(check: Check, styles) -> list[Any]:
    elements: list[Any] = []

    elements.append(build_section_title("Photographies du véhicule", styles))

    photo_title_style = ParagraphStyle(
        "PhotoTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )

    photo_text_style = styles["Normal"]
    sorted_photos = sorted(check.photos or [], key=lambda photo: photo.display_order)

    if not sorted_photos:
        elements.append(Paragraph("Aucune photo disponible.", photo_text_style))
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    for photo in sorted_photos:
        raw_label = getattr(photo.photo_type, "name", None) or getattr(photo.photo_type, "value", str(photo.photo_type))
        title = Paragraph(translate_photo_label(raw_label), photo_title_style)
        elements.append(title)

        annotated_buffer = annotate_photo_with_damages(photo)

        if annotated_buffer:
            try:
                img = create_image(annotated_buffer, 13.8 * cm, 7.2 * cm)
                elements.append(img)
            except Exception:
                elements.append(Paragraph("Image indisponible", photo_text_style))
        else:
            elements.append(Paragraph("Image indisponible", photo_text_style))

        damages = getattr(photo, "damages", None) or []

        if damages:
            elements.append(Spacer(1, 0.15 * cm))
            elements.append(build_single_damage_table(photo))

        elements.append(Spacer(1, 0.35 * cm))

    return elements
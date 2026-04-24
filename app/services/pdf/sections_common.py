from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

from app.core.config import settings


def build_logo_block() -> list[Any]:
    elements: list[Any] = []
    logo_path = Path(settings.agency_logo_path)

    if not logo_path.exists():
        return elements

    logo = Image(str(logo_path))
    ratio = logo.imageWidth / logo.imageHeight
    logo.drawWidth = 4.2 * cm
    logo.drawHeight = logo.drawWidth / ratio

    header_table = Table([[logo]], colWidths=[16.5 * cm])
    header_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * cm))
    return elements


def build_header(styles) -> list[Any]:
    title_style = ParagraphStyle(
        "MainTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "SubTitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=8,
    )

    badge_style = ParagraphStyle(
        "BadgeStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.white,
    )

    badge = Table(
        [[Paragraph("DOCUMENT CONTRACTUEL", badge_style)]],
        colWidths=[6.2 * cm],
    )
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1D4ED8")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0, colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    wrapper = Table([[badge]], colWidths=[16.5 * cm])
    wrapper.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    return [
        Paragraph("Contrat de location et état des lieux", title_style),
        Paragraph(
            "Document récapitulatif du véhicule, du locataire et du contrôle réalisé.",
            subtitle_style,
        ),
        wrapper,
        Spacer(1, 0.35 * cm),
    ]


def build_section_title(title: str, styles) -> Paragraph:
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#111827"),
        backColor=colors.HexColor("#F3F4F6"),
        borderPadding=6,
        spaceBefore=7,
        spaceAfter=7,
    )
    return Paragraph(title, section_style)


def build_info_table(rows: list[list[str]]) -> Table:
    table = Table(rows, colWidths=[5.4 * cm, 10.1 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#111827")),
            ]
        )
    )
    return table


def build_footer(styles) -> list[Any]:
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
    )

    return [
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Ce document récapitule les éléments contractuels et l'état constaté du véhicule au moment du contrôle.",
            footer_style,
        ),
    ]
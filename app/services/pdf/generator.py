from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate

from app.models.check import Check
from app.models.enums import CheckType
from app.services.pdf.sections_common import (
    build_footer,
    build_header,
    build_logo_block,
)
from app.services.pdf.sections_contract import (
    build_agent_block,
    build_check_block,
    build_comparison_block,
    build_contract_block,
    build_customer_block,
    build_financial_block,
    build_legal_block,
    build_notes_block,
    build_signature_block,
    build_terms_block,
    build_vehicle_block,
)
from app.services.pdf.sections_photos import (
    build_photo_comparison_grid,
    build_photo_grid,
)


def generate_check_pdf(check: Check, previous_departure: Check | None = None) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = Path(tmp.name)
    tmp.close()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.extend(build_logo_block())
    story.extend(build_header(styles))
    story.extend(build_contract_block(check, styles))
    story.extend(build_financial_block(check, styles))
    story.extend(build_customer_block(check, styles))
    story.extend(build_vehicle_block(check, styles))
    story.extend(build_check_block(check, styles))
    story.extend(build_agent_block(check, styles))
    story.extend(build_notes_block(check, previous_departure, styles))
    story.extend(build_comparison_block(check, previous_departure, styles))

    if check.type_check == CheckType.RETURN and previous_departure is not None:
        story.extend(build_photo_comparison_grid(check, previous_departure, styles))
    else:
        story.extend(build_photo_grid(check, styles))

    story.extend(build_signature_block(check, styles))
    story.extend(build_terms_block(check, styles))
    story.extend(build_legal_block(check, styles))
    story.extend(build_footer(styles))

    doc.build(story)

    return str(pdf_path)
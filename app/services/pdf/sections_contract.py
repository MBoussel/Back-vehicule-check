from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.models.check import Check
from app.models.enums import CheckType
from app.services.check_comparator import compare_checks
from app.services.pdf.images import create_image, download_image
from app.services.pdf.sections_common import build_info_table, build_section_title
from app.services.pdf.utils import (
    format_date_fr,
    format_datetime_fr,
    format_enum_label,
    format_money,
    safe_text,
    translate_value,
)


def build_image_from_url(image_url: str | None, max_width: float, max_height: float):
    if not image_url:
        return None

    img_buffer = download_image(image_url)
    if img_buffer is None:
        return None

    try:
        return create_image(img_buffer, max_width, max_height)
    except Exception:
        return None


def build_license_images_block(
    title_prefix: str,
    front_image_url: str | None,
    back_image_url: str | None,
    styles,
) -> list[Any]:
    elements: list[Any] = []

    title_style = ParagraphStyle(
        "LicensePhotoTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.HexColor("#111827"),
        spaceBefore=4,
        spaceAfter=4,
    )

    text_style = styles["Normal"]

    front_content: list[Any] = [Paragraph(f"{title_prefix} - recto", title_style)]
    front_img = build_image_from_url(front_image_url, 7.5 * cm, 5.2 * cm)
    if front_img is not None:
        front_content.append(front_img)
    else:
        front_content.append(Paragraph("Image indisponible.", text_style))

    back_content: list[Any] = [Paragraph(f"{title_prefix} - verso", title_style)]
    back_img = build_image_from_url(back_image_url, 7.5 * cm, 5.2 * cm)
    if back_img is not None:
        back_content.append(back_img)
    else:
        back_content.append(Paragraph("Image indisponible.", text_style))

    table = Table([[front_content, back_content]], colWidths=[8.0 * cm, 8.0 * cm])
    table.setStyle(
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

    elements.append(table)
    elements.append(Spacer(1, 0.25 * cm))
    return elements


def build_contract_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []
    contract = check.contract

    elements.append(build_section_title("Informations du contrat", styles))

    if contract is None:
        elements.append(
            build_info_table(
                [
                    ["Numéro de contrat", safe_text(check.booking_reference)],
                    ["Mode de signature", "Signature sur place"],
                    ["Statut", "Document sans contrat associé"],
                    ["Lieu de remise", "-"],
                    ["Lieu de restitution", "-"],
                    ["Frais de livraison", "-"],
                ]
            )
        )
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    elements.append(
        build_info_table(
            [
                ["Numéro de contrat", safe_text(contract.contract_number)],
                ["Début de location", format_datetime_fr(contract.start_date)],
                ["Fin de location", format_datetime_fr(contract.end_date)],
                ["Montant location", format_money(contract.rental_price)],
                ["Mode de signature", translate_value(contract.signature_mode)],
                ["Statut du contrat", translate_value(contract.status)],
                ["Lieu de remise", safe_text(getattr(contract, "pickup_location", None))],
                ["Lieu de restitution", safe_text(getattr(contract, "return_location", None))],
                ["Frais de livraison", format_money(getattr(contract, "delivery_fee", None))],
            ]
        )
    )
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_financial_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []
    vehicle = check.vehicle
    contract = check.contract

    deposit_amount = getattr(contract, "deposit_amount", None) if contract else None
    franchise_amount = getattr(contract, "franchise_amount", None) if contract else None
    included_km = getattr(vehicle, "included_km", None)
    extra_km_price = getattr(vehicle, "extra_km_price", None)
    immobilization_fee_per_day = getattr(vehicle, "immobilization_fee_per_day", None)
    key_loss_fee = getattr(vehicle, "key_loss_fee", None)
    delivery_fee = getattr(contract, "delivery_fee", None) if contract else None

    extra_km_price_text = "-"
    if extra_km_price is not None:
        extra_km_price_text = f"{extra_km_price:.2f} €/km"

    rental_price = getattr(contract, "rental_price", None) if contract else None

    elements.append(build_section_title("Récapitulatif financier", styles))

    rows = [
        ["Montant location", format_money(rental_price)],
        ["Caution", format_money(deposit_amount)],
        ["Franchise", format_money(franchise_amount)],
        ["Kilométrage inclus", safe_text(included_km)],
        ["Prix kilomètre supplémentaire", extra_km_price_text],
        ["Frais immobilisation / jour", format_money(immobilization_fee_per_day)],
        ["Perte de clé / carte", format_money(key_loss_fee)],
        ["Frais de livraison", format_money(delivery_fee)],
    ]

    elements.append(build_info_table(rows))
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_customer_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []
    contract = check.contract

    elements.append(build_section_title("Informations du locataire", styles))

    if contract is None:
        elements.append(
            build_info_table(
                [
                    ["Nom", safe_text(check.client_name)],
                    ["Référence réservation", safe_text(check.booking_reference)],
                ]
            )
        )
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    full_name = f"{safe_text(contract.customer_first_name)} {safe_text(contract.customer_last_name)}"

    elements.append(
        build_info_table(
            [
                ["Nom complet", full_name],
                ["Email", safe_text(contract.customer_email)],
                ["Téléphone", safe_text(contract.customer_phone)],
                ["Adresse", safe_text(contract.customer_address)],
                ["Numéro de permis", safe_text(contract.license_number)],
                ["Date de délivrance", format_date_fr(contract.license_issue_date)],
                ["Pays de délivrance", safe_text(contract.license_country)],
            ]
        )
    )
    elements.append(Spacer(1, 0.15 * cm))
    elements.extend(
        build_license_images_block(
            "Permis du conducteur principal",
            getattr(contract, "license_front_photo_url", None),
            getattr(contract, "license_back_photo_url", None),
            styles,
        )
    )

    has_secondary_driver = any(
    [
        getattr(contract, "secondary_driver_first_name", None),
        getattr(contract, "secondary_driver_last_name", None),
        getattr(contract, "secondary_license_number", None),
    ]
)

    if has_secondary_driver:
        secondary_name = (
            f"{safe_text(getattr(contract, 'secondary_driver_first_name', None))} "
            f"{safe_text(getattr(contract, 'secondary_driver_last_name', None))}"
        )

        elements.append(build_section_title("Conducteur secondaire", styles))
        elements.append(
            build_info_table(
                [
                    ["Nom complet", secondary_name],
                    ["Email", safe_text(getattr(contract, "secondary_driver_email", None))],
                    ["Téléphone", safe_text(getattr(contract, "secondary_driver_phone", None))],
                    ["Numéro de permis", safe_text(getattr(contract, "secondary_license_number", None))],
                    ["Date de délivrance", format_date_fr(getattr(contract, "secondary_license_issue_date", None))],
                    ["Pays de délivrance", safe_text(getattr(contract, "secondary_license_country", None))],
                ]
            )
        )
        elements.append(Spacer(1, 0.15 * cm))
        elements.extend(
            build_license_images_block(
                "Permis du conducteur secondaire",
                getattr(contract, "secondary_license_front_photo_url", None),
                getattr(contract, "secondary_license_back_photo_url", None),
                styles,
            )
        )

    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_vehicle_block(check: Check, styles) -> list[Any]:
    vehicle = check.vehicle
    elements: list[Any] = []

    elements.append(build_section_title("Informations du véhicule", styles))
    elements.append(
        build_info_table(
            [
                ["Marque", safe_text(vehicle.brand)],
                ["Modèle", safe_text(vehicle.model)],
                ["Immatriculation", safe_text(vehicle.plate_number)],
                ["Carburant véhicule", format_enum_label(vehicle.fuel_type)],
            ]
        )
    )
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_check_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []

    elements.append(build_section_title("État des lieux", styles))
    elements.append(
        build_info_table(
            [
                ["Type de contrôle", format_enum_label(check.type_check)],
                ["Date du contrôle", format_datetime_fr(check.check_date)],
                ["Kilométrage relevé", safe_text(check.mileage)],
                ["Niveau de carburant", format_enum_label(check.fuel_level)],
                ["Niveau de propreté", format_enum_label(check.cleanliness)],
                ["Statut du contrôle", format_enum_label(check.status)],
            ]
        )
    )
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_agent_block(check: Check, styles) -> list[Any]:
    user = check.user
    elements: list[Any] = []

    elements.append(build_section_title("Agent ayant réalisé le contrôle", styles))

    if user is None:
        elements.append(build_info_table([["Nom", "-"], ["Email", "-"]]))
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    elements.append(
        build_info_table(
            [
                ["Nom", f"{safe_text(user.first_name)} {safe_text(user.last_name)}"],
                ["Email", safe_text(user.email)],
            ]
        )
    )
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_notes_block(check: Check, previous_departure: Check | None, styles) -> list[Any]:
    elements: list[Any] = []

    elements.append(build_section_title("Observations", styles))
    rows = [["Notes du contrôle", safe_text(check.notes)]]

    if previous_departure is not None and check.type_check == CheckType.RETURN:
        rows.append(["Notes au départ", safe_text(previous_departure.notes)])
        rows.append(["Notes au retour", safe_text(check.notes)])

    elements.append(build_info_table(rows))
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_comparison_block(check: Check, previous_departure: Check | None, styles) -> list[Any]:
    elements: list[Any] = []

    if check.type_check != CheckType.RETURN or previous_departure is None:
        return elements

    comparison = compare_checks(previous_departure, check)

    comparison_data = [
        ["Champ", "Départ", "Retour", "Écart / évolution"],
        [
            "Kilométrage",
            safe_text(comparison.get("departure_mileage")),
            safe_text(comparison.get("return_mileage")),
            safe_text(comparison.get("km_diff")),
        ],
        [
            "Carburant",
            safe_text(comparison.get("departure_fuel_level")),
            safe_text(comparison.get("return_fuel_level")),
            f"{safe_text(comparison.get('fuel_diff'))} %",
        ],
        [
            "Propreté",
            safe_text(comparison.get("departure_cleanliness")),
            safe_text(comparison.get("return_cleanliness")),
            "Modifiée" if comparison.get("cleanliness_changed") else "Identique",
        ],
        [
            "Observations",
            safe_text(comparison.get("departure_notes")),
            safe_text(comparison.get("return_notes")),
            "Changement détecté" if comparison.get("possible_new_damage") else "Aucun changement notable",
        ],
    ]

    elements.append(build_section_title("Comparaison départ / retour", styles))

    table = Table(comparison_data, colWidths=[4.1 * cm, 3.8 * cm, 3.8 * cm, 4.3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_signature_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []

    elements.append(build_section_title("Signatures", styles))

    acknowledgement_style = ParagraphStyle(
    "SignatureAcknowledgement",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#111827"),
    spaceAfter=8,
)

    elements.append(
    Paragraph(
        "Le client reconnaît avoir pris connaissance de l’état du véhicule, du récapitulatif financier et des conditions générales de location.",
        acknowledgement_style,
    )
)

    signature_text_style = ParagraphStyle(
        "SignatureText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#334155"),
    )

    label_style = ParagraphStyle(
        "SignatureLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6,
    )

    def build_signature_cell(title: str, image_url: str | None, approval_text: str) -> list[Any]:
        cell_content: list[Any] = [Paragraph(title, label_style)]

        if image_url:
            img_buffer = download_image(image_url)
            if img_buffer:
                try:
                    img = create_image(img_buffer, 5.5 * cm, 2.2 * cm)
                    cell_content.append(img)
                except Exception:
                    cell_content.append(Paragraph("Signature indisponible.", signature_text_style))
            else:
                cell_content.append(Paragraph("Signature indisponible.", signature_text_style))
        else:
            cell_content.append(Paragraph("Aucune signature disponible.", signature_text_style))

        cell_content.append(Spacer(1, 0.15 * cm))
        cell_content.append(Paragraph(approval_text, signature_text_style))
        return cell_content

    client_cell = build_signature_cell(
        "Signature du client",
        check.signature_url,
        "Lu et approuvé par le client",
    )

    agent_name = "-"
    if check.user is not None:
        agent_name = f"{safe_text(check.user.first_name)} {safe_text(check.user.last_name)}"

    agent_cell = build_signature_cell(
        "Signature de l'agent",
        check.agent_signature_url,
        f"Contrôle réalisé par : {agent_name}",
    )

    table = Table([[client_cell, agent_cell]], colWidths=[8 * cm, 8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 0.3 * cm))
    return elements


def build_terms_block(check: Check, styles) -> list[Any]:
    contract = check.contract
    elements: list[Any] = []

    if contract is None and not check.signature_url and not check.agent_signature_url:
        return elements

    elements.append(build_section_title("Validation et mentions", styles))

    terms = "-"
    if contract is not None and contract.terms_and_conditions:
        terms = contract.terms_and_conditions

    signature_mode = "Sur place"
    if contract is not None and contract.signature_mode:
        signature_mode = translate_value(contract.signature_mode)

    rows = [
        ["Document validé par signatures", "Oui" if (check.signature_url or check.agent_signature_url) else "Non"],
        ["Mode de signature", signature_mode],
        ["Mentions", safe_text(terms)],
    ]

    elements.append(build_info_table(rows))
    elements.append(Spacer(1, 0.2 * cm))
    return elements


def build_legal_block(check: Check, styles) -> list[Any]:
    elements: list[Any] = []
    contract = check.contract

    deposit_amount = format_money(getattr(contract, "deposit_amount", None) if contract else None)
    franchise_amount = format_money(getattr(contract, "franchise_amount", None) if contract else None)
    immobilization_fee = format_money(getattr(check.vehicle, "immobilization_fee_per_day", None))
    key_loss_fee = format_money(getattr(check.vehicle, "key_loss_fee", None))

    legal_style = ParagraphStyle(
    "LegalText",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor("#111827"),
    alignment=TA_LEFT,
    spaceAfter=7,
)

    title_style = ParagraphStyle(
    "LegalMiniTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    textColor=colors.HexColor("#0F172A"),
    spaceBefore=5,
    spaceAfter=2,
)

    elements.append(build_section_title("Conditions générales de location", styles))

    legal_sections = [
        ("1. Objet",
         "Le présent contrat encadre la mise à disposition du véhicule au locataire, "
         "qui en a la garde et la responsabilité pendant toute la durée de la location, "
         "de la remise des clés jusqu’à sa restitution complète."),

        ("2. Conditions de location",
         "Le locataire doit présenter une pièce d’identité valide, un permis de conduire valide "
         "(minimum 3 ans sauf accord contraire) et une carte bancaire au nom du locataire pour le dépôt de garantie. "
         "L’âge minimum est fixé à 21 ans sauf accord contraire. "
         "Seuls les conducteurs mentionnés au contrat sont autorisés à conduire. "
         "Le loueur peut refuser la location en cas de documents manquants ou invalides, "
         "d’impossibilité de dépôt de garantie ou d’impayé antérieur."),

        ("3. Utilisation du véhicule",
         "Le véhicule doit être utilisé conformément à sa destination et au Code de la route. "
         "Il est interdit de sous-louer ou prêter le véhicule, d’utiliser le véhicule pour du transport rémunéré "
         "(VTC, livraison…), de conduire sous alcool ou stupéfiants, d’utiliser le véhicule sur circuit ou hors route, "
         "de fumer dans le véhicule ou de sortir du territoire sans accord écrit. "
         "Le locataire est responsable des infractions, péages et stationnements. "
         "Le locataire autorise le loueur à transmettre ses coordonnées aux autorités compétentes. "
         "Frais de gestion : 15 € par infraction."),

        ("4. Durée et restitution",
         "Le véhicule doit être restitué à la date, à l’heure et au lieu convenus. "
         "En cas de retard : 25 € par heure, journée supplémentaire possible, "
         "et 50 € en cas de retard supérieur à 24 heures. Ces frais sont cumulables. "
         "Le loueur peut récupérer le véhicule aux frais du locataire en cas de non-restitution."),

        ("5. Tarifs et carburant / énergie",
         "Le prix de la location est défini au contrat. "
         "Les kilomètres supplémentaires sont facturés selon le tarif prévu. "
         "Le véhicule doit être restitué avec le même niveau de carburant ou de charge qu’au départ. "
         "À défaut : carburant facturé au tarif en vigueur + 10 €, recharge au coût réel + 10 €."),

        ("6. Dépôt de garantie",
         f"Un dépôt de garantie de {deposit_amount} est exigé avant la remise du véhicule. "
         "Il couvre les dommages, frais, retards et infractions. "
         "Il peut être conservé partiellement ou totalement. "
         "Restitution sous 8 jours maximum après vérification. "
         "Tout dépassement reste dû par le locataire."),

        ("7. État des lieux",
         "Un état des lieux est réalisé au départ et au retour. "
         "Sans réserve du locataire, le véhicule est réputé conforme. "
         "Photos et observations ont valeur contractuelle."),

        ("8. Propreté",
         "Le véhicule doit être rendu propre. "
         "Frais : extérieur 20 €, intérieur 30 €, nettoyage important 70 à 200 €, "
         "odeur tabac 120 €."),

        ("9. Assurance et responsabilité",
         f"Le véhicule est assuré pour les conducteurs autorisés. "
         f"Franchise : {franchise_amount}. "
         "Le locataire reste redevable des dommages non couverts. "
         "Exclusions : alcool, stupéfiants, conducteur non autorisé, usage interdit. "
         "Dans ces cas, les dommages sont intégralement à la charge du locataire."),

        ("10. Sinistre et accident",
         "Le locataire doit prévenir immédiatement le loueur, établir un constat, "
         "fournir les informations des tiers, prendre des photos et déclarer sous 24h. "
         "Plainte obligatoire en cas de vol. À défaut, les réparations peuvent être facturées."),

        ("11. Entretien",
         "Le locataire doit surveiller voyants, pneus et niveaux. "
         "Toute intervention sans accord est interdite."),

        ("12. Frais additionnels",
         f"Carburant manquant : tarif + 10 €. Recharge : coût réel + 10 €. "
         f"Infractions : montant + 15 €. "
         f"Perte de clé : {key_loss_fee}. "
         f"Dommages facturés au forfait ou sur devis. "
         f"Immobilisation : {immobilization_fee}/jour (perte d’exploitation). "
         f"Les montants sont indicatifs et ajustables."),

        ("13. Résiliation",
         "Le contrat peut être résilié immédiatement en cas de non-respect ou de non-paiement. "
         "Aucun remboursement ne sera dû."),

        ("14. Données personnelles",
         "Les données sont utilisées uniquement pour la gestion de la location conformément à la réglementation en vigueur."),

        ("15. Réclamations",
         "Toute réclamation doit être adressée au loueur. "
         "En cas de litige, recours possible à un médiateur de la consommation."),

        ("16. Droit applicable",
         "Le contrat est soumis au droit français."),
    ]

    for section_title, section_text in legal_sections:
        elements.append(Paragraph(section_title, title_style))
        elements.append(Paragraph(section_text, legal_style))

    elements.append(Spacer(1, 0.3 * cm))
    return elements
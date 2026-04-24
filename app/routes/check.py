from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.check import Check
from app.models.check_photo import CheckPhoto
from app.models.enums import CheckStatus, CheckType, VehicleStatus
from app.models.rental_contract import RentalContract
from app.models.user import User
from app.models.vehicle import Vehicle
from app.routes.auth import get_current_user
from app.schemas.check import CheckCreate, CheckResponse
from app.services.check_comparator import compare_checks
from app.services.check_photo_rules import validate_check_required_photos
from app.services.pdf import generate_check_pdf

router = APIRouter(prefix="/checks", tags=["Checks"])


@router.post("/", response_model=CheckResponse)
def create_check(
    payload: CheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = db.get(Vehicle, payload.vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if payload.contract_id is not None:
        contract = db.get(RentalContract, payload.contract_id)
        if contract is None:
            raise HTTPException(status_code=404, detail="Contract not found")

        if contract.vehicle_id != payload.vehicle_id:
            raise HTTPException(
                status_code=400,
                detail="This contract is not linked to the selected vehicle",
            )

    if payload.mileage < vehicle.current_mileage:
        raise HTTPException(
            status_code=400,
            detail="Mileage cannot be lower than current vehicle mileage",
        )

    db_check = Check(
        vehicle_id=payload.vehicle_id,
        user_id=current_user.id,
        contract_id=payload.contract_id,
        type_check=payload.type_check,
        mileage=payload.mileage,
        fuel_level=payload.fuel_level,
        cleanliness=payload.cleanliness,
        notes=payload.notes,
        booking_reference=payload.booking_reference,
        client_name=payload.client_name,
        status=payload.status,
    )

    db.add(db_check)

    vehicle.current_mileage = payload.mileage

    if payload.type_check == CheckType.DEPARTURE:
        vehicle.status = VehicleStatus.RENTED
    elif payload.type_check == CheckType.RETURN:
        vehicle.status = VehicleStatus.AVAILABLE

    db.commit()
    db.refresh(db_check)

    created_check = (
        db.query(Check)
        .options(
            joinedload(Check.photos).joinedload(CheckPhoto.damages),
            joinedload(Check.vehicle),
            joinedload(Check.user),
            joinedload(Check.contract),
        )
        .filter(Check.id == db_check.id)
        .first()
    )

    if created_check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    return created_check


@router.put("/{check_id}/complete", response_model=CheckResponse)
def complete_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    check = (
        db.query(Check)
        .options(
            joinedload(Check.photos).joinedload(CheckPhoto.damages),
            joinedload(Check.contract),
            joinedload(Check.vehicle),
            joinedload(Check.user),
        )
        .filter(Check.id == check_id)
        .first()
    )

    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    check.status = CheckStatus.COMPLETED

    try:
        validate_check_required_photos(check)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    db.commit()
    db.refresh(check)

    return check


@router.get("/", response_model=list[CheckResponse])
def get_checks(db: Session = Depends(get_db)):
    return (
        db.query(Check)
        .options(
            joinedload(Check.photos).joinedload(CheckPhoto.damages),
            joinedload(Check.contract),
            joinedload(Check.vehicle),
            joinedload(Check.user),
        )
        .order_by(Check.check_date.desc())
        .all()
    )


@router.get("/{check_id}", response_model=CheckResponse)
def get_check(check_id: int, db: Session = Depends(get_db)):
    check = (
        db.query(Check)
        .options(
            joinedload(Check.photos).joinedload(CheckPhoto.damages),
            joinedload(Check.contract),
            joinedload(Check.vehicle),
            joinedload(Check.user),
        )
        .filter(Check.id == check_id)
        .first()
    )

    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    return check


@router.get("/{check_id}/compare")
def compare_with_departure(check_id: int, db: Session = Depends(get_db)):
    current_check = db.get(Check, check_id)

    if current_check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    if current_check.type_check != CheckType.RETURN:
        raise HTTPException(
            status_code=400,
            detail="Comparison only available for RETURN checks",
        )

    if current_check.contract_id is not None:
        departure = (
            db.query(Check)
            .filter(
                Check.contract_id == current_check.contract_id,
                Check.type_check == CheckType.DEPARTURE,
                Check.check_date < current_check.check_date,
            )
            .order_by(Check.check_date.desc())
            .first()
        )
    else:
        departure = (
            db.query(Check)
            .filter(
                Check.vehicle_id == current_check.vehicle_id,
                Check.type_check == CheckType.DEPARTURE,
                Check.check_date < current_check.check_date,
            )
            .order_by(Check.check_date.desc())
            .first()
        )

    if departure is None:
        raise HTTPException(
            status_code=404,
            detail="No departure check found for this vehicle or contract",
        )

    return compare_checks(departure, current_check)


@router.get("/{check_id}/pdf")
def generate_check_state_pdf(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user

    check = (
        db.query(Check)
        .options(
            joinedload(Check.photos).joinedload(CheckPhoto.damages),
            joinedload(Check.vehicle),
            joinedload(Check.user),
            joinedload(Check.contract),
        )
        .filter(Check.id == check_id)
        .first()
    )

    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")

    previous_departure = None

    if check.type_check == CheckType.RETURN:
        if check.contract_id is not None:
            previous_departure = (
                db.query(Check)
                .filter(
                    Check.contract_id == check.contract_id,
                    Check.type_check == CheckType.DEPARTURE,
                    Check.check_date < check.check_date,
                )
                .order_by(Check.check_date.desc())
                .first()
            )
        else:
            previous_departure = (
                db.query(Check)
                .filter(
                    Check.vehicle_id == check.vehicle_id,
                    Check.type_check == CheckType.DEPARTURE,
                    Check.check_date < check.check_date,
                )
                .order_by(Check.check_date.desc())
                .first()
            )

    pdf_path = generate_check_pdf(check, previous_departure)

    filename = f"etat-des-lieux-check-{check.id}.pdf"

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
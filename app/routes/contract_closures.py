from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.check import Check
from app.models.contract_closure import ContractClosure
from app.models.enums import CheckStatus, CheckType
from app.models.rental_contract import RentalContract
from app.schemas.contract_closure import (
    ContractClosureCreate,
    ContractClosureResponse,
    ContractClosureUpdate,
)

router = APIRouter(prefix="/contracts", tags=["Contract closures"])


def _money(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _get_rental_days(start_date: datetime, end_date: datetime) -> int:
    days = (end_date.date() - start_date.date()).days
    return max(days, 1)


def _get_completed_checks(db: Session, contract_id: int) -> tuple[Check, Check]:
    departure = (
        db.query(Check)
        .filter(
            Check.contract_id == contract_id,
            Check.type_check == CheckType.DEPARTURE,
            Check.status == CheckStatus.COMPLETED,
        )
        .order_by(Check.check_date.desc())
        .first()
    )

    return_check = (
        db.query(Check)
        .filter(
            Check.contract_id == contract_id,
            Check.type_check == CheckType.RETURN,
            Check.status == CheckStatus.COMPLETED,
        )
        .order_by(Check.check_date.desc())
        .first()
    )

    if departure is None:
        raise HTTPException(status_code=400, detail="Departure check is required")

    if return_check is None:
        raise HTTPException(status_code=400, detail="Return check is required")

    return departure, return_check


def _get_base_revenue(contract: RentalContract) -> Decimal:
    """
    For internal contracts, the base revenue is the rental price.
    For external contracts, the base revenue is the net revenue after platform fees.
    """
    if getattr(contract, "is_external", False):
        net_revenue = getattr(contract, "net_revenue", None)

        if net_revenue is not None:
            return _money(net_revenue)

        rental_price = _money(getattr(contract, "rental_price", None))
        platform_fee = _money(getattr(contract, "platform_fee", None))
        return rental_price - platform_fee

    return _money(getattr(contract, "rental_price", None))


def _calculate_closure_data(
    contract: RentalContract,
    departure: Check | None,
    return_check: Check | None,
    payload: ContractClosureCreate | ContractClosureUpdate,
):
    rental_days = _get_rental_days(contract.start_date, contract.end_date)

    if getattr(contract, "is_external", False):
        departure_mileage = int(getattr(contract, "external_start_mileage", None) or 0)
        return_mileage = int(getattr(contract, "external_end_mileage", None) or 0)
    else:
        if departure is None or return_check is None:
            raise HTTPException(
                status_code=400,
                detail="Departure and return checks are required",
            )

        departure_mileage = int(departure.mileage or 0)
        return_mileage = int(return_check.mileage or 0)

    driven_km = max(return_mileage - departure_mileage, 0)

    included_km_per_day = getattr(contract.vehicle, "included_km", None) or 0
    included_km = int(included_km_per_day) * rental_days

    extra_km = max(driven_km - included_km, 0)

    base_revenue = _get_base_revenue(contract)

    extra_km_fee = _money(getattr(payload, "extra_km_fee", None))
    fuel_fee = _money(getattr(payload, "fuel_fee", None))
    cleaning_fee = _money(getattr(payload, "cleaning_fee", None))
    damage_fee = _money(getattr(payload, "damage_fee", None))
    other_fee = _money(getattr(payload, "other_fee", None))
    discount_amount = _money(getattr(payload, "discount_amount", None))

    final_total = (
        base_revenue
        + extra_km_fee
        + fuel_fee
        + cleaning_fee
        + damage_fee
        + other_fee
        - discount_amount
    )

    return {
        "rental_days": rental_days,
        "departure_mileage": departure_mileage,
        "return_mileage": return_mileage,
        "driven_km": driven_km,
        "included_km": included_km,
        "extra_km": extra_km,
        "rental_price": base_revenue,
        "extra_km_fee": extra_km_fee,
        "fuel_fee": fuel_fee,
        "cleaning_fee": cleaning_fee,
        "damage_fee": damage_fee,
        "other_fee": other_fee,
        "discount_amount": discount_amount,
        "final_total": final_total,
        "notes": getattr(payload, "notes", None),
        "status": getattr(payload, "status", None) or "draft",
    }


@router.get("/{contract_id}/closure", response_model=ContractClosureResponse)
def get_contract_closure(contract_id: int, db: Session = Depends(get_db)):
    closure = (
        db.query(ContractClosure)
        .filter(ContractClosure.contract_id == contract_id)
        .first()
    )

    if closure is None:
        raise HTTPException(status_code=404, detail="Contract closure not found")

    return closure


@router.post("/{contract_id}/closure", response_model=ContractClosureResponse)
def create_contract_closure(
    contract_id: int,
    payload: ContractClosureCreate,
    db: Session = Depends(get_db),
):
    contract = (
        db.query(RentalContract)
        .options(joinedload(RentalContract.vehicle))
        .filter(RentalContract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    existing_closure = (
        db.query(ContractClosure)
        .filter(ContractClosure.contract_id == contract_id)
        .first()
    )

    if existing_closure is not None:
        raise HTTPException(status_code=400, detail="Contract closure already exists")

    departure = None
    return_check = None

    if not getattr(contract, "is_external", False):
        departure, return_check = _get_completed_checks(db, contract_id)

    closure_data = _calculate_closure_data(contract, departure, return_check, payload)

    closure = ContractClosure(
        contract_id=contract_id,
        **closure_data,
    )

    db.add(closure)
    db.commit()
    db.refresh(closure)

    return closure


@router.put("/{contract_id}/closure", response_model=ContractClosureResponse)
def update_contract_closure(
    contract_id: int,
    payload: ContractClosureUpdate,
    db: Session = Depends(get_db),
):
    contract = (
        db.query(RentalContract)
        .options(joinedload(RentalContract.vehicle))
        .filter(RentalContract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    closure = (
        db.query(ContractClosure)
        .filter(ContractClosure.contract_id == contract_id)
        .first()
    )

    if closure is None:
        raise HTTPException(status_code=404, detail="Contract closure not found")

    departure = None
    return_check = None

    if not getattr(contract, "is_external", False):
        departure, return_check = _get_completed_checks(db, contract_id)

    current_payload = ContractClosureUpdate(
        extra_km_fee=payload.extra_km_fee if payload.extra_km_fee is not None else closure.extra_km_fee,
        fuel_fee=payload.fuel_fee if payload.fuel_fee is not None else closure.fuel_fee,
        cleaning_fee=payload.cleaning_fee if payload.cleaning_fee is not None else closure.cleaning_fee,
        damage_fee=payload.damage_fee if payload.damage_fee is not None else closure.damage_fee,
        other_fee=payload.other_fee if payload.other_fee is not None else closure.other_fee,
        discount_amount=payload.discount_amount if payload.discount_amount is not None else closure.discount_amount,
        notes=payload.notes if payload.notes is not None else closure.notes,
        status=payload.status if payload.status is not None else closure.status,
    )

    closure_data = _calculate_closure_data(contract, departure, return_check, current_payload)

    for key, value in closure_data.items():
        setattr(closure, key, value)

    db.commit()
    db.refresh(closure)

    return closure

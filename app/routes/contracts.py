from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from datetime import datetime
from app.models.rental_contract import RentalContract
from app.models.vehicle import Vehicle
from app.schemas.rental_contract import (
    RentalContractCreate,
    RentalContractResponse,
    RentalContractUpdate,
)

router = APIRouter(prefix="/contracts", tags=["Contracts"])
def generate_contract_number(db: Session) -> str:
    year = datetime.utcnow().year

    last_contract = (
        db.query(RentalContract)
        .filter(RentalContract.contract_number.like(f"CTR-{year}-LOC-%"))
        .order_by(RentalContract.id.desc())
        .first()
    )

    if not last_contract:
        next_number = 1
    else:
        try:
            last_number = int(last_contract.contract_number.split("-")[-1])
            next_number = last_number + 1
        except Exception:
            next_number = 1

    return f"CTR-{year}-LOC-{next_number}"

def _get_vehicle_or_404(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def _copy_vehicle_financial_defaults(
    data: dict,
    vehicle: Vehicle,
    *,
    force_deposit: bool = False,
    force_franchise: bool = False,
) -> dict:
    vehicle_deposit_amount = getattr(vehicle, "deposit_amount", None)
    vehicle_franchise_amount = getattr(vehicle, "franchise_amount", None)

    if force_deposit or data.get("deposit_amount") is None:
        data["deposit_amount"] = vehicle_deposit_amount

    if force_franchise or data.get("franchise_amount") is None:
        data["franchise_amount"] = vehicle_franchise_amount

    return data


@router.post("/", response_model=RentalContractResponse)
def create_contract(payload: RentalContractCreate, db: Session = Depends(get_db)):

    contract_data = payload.model_dump()

    # 🔥 génération auto si absent ou TEMP
    if not contract_data.get("contract_number") or contract_data["contract_number"] == "TEMP":
        contract_data["contract_number"] = generate_contract_number(db)

    else:
        existing_contract = (
            db.query(RentalContract)
            .filter(RentalContract.contract_number == contract_data["contract_number"])
            .first()
        )
        if existing_contract:
            raise HTTPException(status_code=400, detail="Contract number already exists")

    vehicle = _get_vehicle_or_404(db, payload.vehicle_id)

    contract_data = _copy_vehicle_financial_defaults(contract_data, vehicle)

    db_contract = RentalContract(**contract_data)

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


@router.get("/", response_model=list[RentalContractResponse])
def get_contracts(db: Session = Depends(get_db)):
    return (
        db.query(RentalContract)
        .options(joinedload(RentalContract.vehicle))
        .order_by(RentalContract.id.desc())
        .all()
    )


@router.get("/{contract_id}", response_model=RentalContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = (
        db.query(RentalContract)
        .options(
            joinedload(RentalContract.vehicle),
            joinedload(RentalContract.checks),
        )
        .filter(RentalContract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    return contract


@router.put("/{contract_id}", response_model=RentalContractResponse)
def update_contract(
    contract_id: int,
    payload: RentalContractUpdate,
    db: Session = Depends(get_db),
):
    contract = db.get(RentalContract, contract_id)

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "contract_number" in update_data:
        existing_contract = (
            db.query(RentalContract)
            .filter(
                RentalContract.contract_number == update_data["contract_number"],
                RentalContract.id != contract_id,
            )
            .first()
        )
        if existing_contract is not None:
            raise HTTPException(status_code=400, detail="Contract number already exists")

    if "vehicle_id" in update_data:
        vehicle = _get_vehicle_or_404(db, update_data["vehicle_id"])
        update_data = _copy_vehicle_financial_defaults(
            update_data,
            vehicle,
            force_deposit=("deposit_amount" not in update_data),
            force_franchise=("franchise_amount" not in update_data),
        )

    for key, value in update_data.items():
        setattr(contract, key, value)

    db.commit()
    db.refresh(contract)

    return contract


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.get(RentalContract, contract_id)

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    db.delete(contract)
    db.commit()

    return {"message": "Contract deleted"}
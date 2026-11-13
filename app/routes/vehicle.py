from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.contract_closure import ContractClosure
from app.models.rental_contract import RentalContract
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def _sync_current_mileage_from_closed_contracts(
    vehicles: list[Vehicle],
    db: Session,
) -> None:
    """
    Reconcile vehicle mileage with all validated historical contract closures.
    This also repairs vehicles whose contracts were closed before automatic
    mileage synchronization was introduced. Never decrease current mileage.
    """
    if not vehicles:
        return

    vehicle_ids = [vehicle.id for vehicle in vehicles]
    latest_mileages = (
        db.query(
            RentalContract.vehicle_id,
            func.max(ContractClosure.return_mileage).label("max_return_mileage"),
        )
        .join(ContractClosure, ContractClosure.contract_id == RentalContract.id)
        .filter(
            RentalContract.vehicle_id.in_(vehicle_ids),
            ContractClosure.status == "closed",
        )
        .group_by(RentalContract.vehicle_id)
        .all()
    )

    mileage_by_vehicle = {
        vehicle_id: int(max_mileage or 0)
        for vehicle_id, max_mileage in latest_mileages
    }

    changed = False
    for vehicle in vehicles:
        closed_contract_mileage = mileage_by_vehicle.get(vehicle.id)
        if (
            closed_contract_mileage is not None
            and closed_contract_mileage > int(vehicle.current_mileage or 0)
        ):
            vehicle.current_mileage = closed_contract_mileage
            changed = True

    if changed:
        db.commit()


@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    vehicle_data = vehicle.model_dump()
    if vehicle_data.get("initial_mileage") is None:
        vehicle_data["initial_mileage"] = vehicle_data.get("current_mileage", 0)
    db_vehicle = Vehicle(**vehicle_data)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    _sync_current_mileage_from_closed_contracts(vehicles, db)
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    _sync_current_mileage_from_closed_contracts([vehicle], db)
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()

    return {"message": "Vehicle deleted"}

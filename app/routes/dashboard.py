from collections import defaultdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.contract_closure import ContractClosure
from app.models.rental_contract import RentalContract
from app.models.vehicle import Vehicle

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


def decimal_to_float(value: Decimal | None) -> float:
    if value is None:
        return 0.0

    return float(value)


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    contracts = (
        db.query(RentalContract)
        .options(
            joinedload(RentalContract.vehicle),
            joinedload(RentalContract.closure),
        )
        .all()
    )

    vehicles = db.query(Vehicle).all()

    total_revenue = 0.0
    total_net_revenue = 0.0
    total_contracts = len(contracts)
    total_km = 0

    source_distribution: dict[str, float] = defaultdict(float)
    revenue_by_vehicle: dict[str, float] = defaultdict(float)
    net_by_vehicle: dict[str, float] = defaultdict(float)
    km_by_vehicle: dict[str, int] = defaultdict(int)
    contracts_by_vehicle: dict[str, int] = defaultdict(int)

    revenue_by_month: dict[str, float] = defaultdict(float)
    contracts_by_month: dict[str, int] = defaultdict(int)

    for contract in contracts:
        vehicle_name = (
            f"{contract.vehicle.brand} {contract.vehicle.model}"
            if contract.vehicle
            else "Véhicule inconnu"
        )

        month_key = contract.start_date.strftime("%Y-%m")

        contracts_by_vehicle[vehicle_name] += 1
        contracts_by_month[month_key] += 1

        revenue = 0.0
        net_revenue = 0.0
        driven_km = 0

        # =========================
        # CONTRAT EXTERNE
        # =========================
        if contract.is_external:
            revenue = decimal_to_float(contract.rental_price)
            net_revenue = decimal_to_float(contract.net_revenue)

            if (
                contract.external_start_mileage is not None
                and contract.external_end_mileage is not None
            ):
                driven_km = max(
                    0,
                    contract.external_end_mileage
                    - contract.external_start_mileage,
                )

            source_key = contract.source or "Autre"
            source_distribution[source_key] += net_revenue

        # =========================
        # CONTRAT INTERNE
        # =========================
        else:
            closure: ContractClosure | None = contract.closure

            if closure is not None:
                revenue = decimal_to_float(closure.final_total)
                net_revenue = decimal_to_float(closure.final_total)
                driven_km = closure.driven_km or 0

            source_distribution["Interne"] += net_revenue

        total_revenue += revenue
        total_net_revenue += net_revenue
        total_km += driven_km

        revenue_by_vehicle[vehicle_name] += revenue
        net_by_vehicle[vehicle_name] += net_revenue
        km_by_vehicle[vehicle_name] += driven_km

        revenue_by_month[month_key] += revenue

    vehicles_stats = []

    for vehicle in vehicles:
        vehicle_name = f"{vehicle.brand} {vehicle.model}"

        vehicles_stats.append(
            {
                "vehicle": vehicle_name,
                "contracts": contracts_by_vehicle.get(vehicle_name, 0),
                "revenue": round(
                    revenue_by_vehicle.get(vehicle_name, 0),
                    2,
                ),
                "net_revenue": round(
                    net_by_vehicle.get(vehicle_name, 0),
                    2,
                ),
                "km": km_by_vehicle.get(vehicle_name, 0),
            }
        )

    vehicles_stats.sort(
        key=lambda item: item["revenue"],
        reverse=True,
    )

    return {
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_net_revenue": round(total_net_revenue, 2),
            "total_contracts": total_contracts,
            "total_km": total_km,
        },
        "source_distribution": [
            {
                "name": key,
                "value": round(value, 2),
            }
            for key, value in source_distribution.items()
        ],
        "vehicles": vehicles_stats,
        "revenue_by_vehicle": [
            {
                "name": key,
                "value": round(value, 2),
            }
            for key, value in revenue_by_vehicle.items()
        ],
        "km_by_vehicle": [
            {
                "name": key,
                "value": value,
            }
            for key, value in km_by_vehicle.items()
        ],
        "revenue_by_month": [
            {
                "month": key,
                "value": round(value, 2),
            }
            for key, value in sorted(revenue_by_month.items())
        ],
        "contracts_by_month": [
            {
                "month": key,
                "value": value,
            }
            for key, value in sorted(contracts_by_month.items())
        ],
    }

import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "emission_factors.json"
)


def load_emission_factors():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_transport_emissions(
    distance_km: float,
    vehicle_type: str
) -> dict:
    """
    Calculate transport-related emissions.

    Public transport factors use passenger-km.
    Private vehicle factors currently use illustrative vehicle-km.
    """

    if distance_km <= 0:
        raise ValueError("Distance must be greater than zero.")

    factors = load_emission_factors()

    vehicle = factors["transport"].get(vehicle_type)

    if vehicle is None:
        raise ValueError(
            f"Unsupported transport mode: {vehicle_type}"
        )

    emissions = distance_km * vehicle["factor"]

    return {
        "category": "transport",
        "vehicle": vehicle_type,
        "distance_km": distance_km,
        "emissions_kg_co2e": round(emissions, 3),
        "emission_factor": vehicle["factor"],
        "unit": vehicle["unit"],
        "basis": vehicle["basis"],
        "source": vehicle["source"],
        "verified": vehicle["verified"]
    }


def calculate_electricity_emissions(
    consumption_kwh: float
) -> dict:
    """
    Calculate electricity-related emissions.
    """

    if consumption_kwh < 0:
        raise ValueError("Consumption cannot be negative.")

    factors = load_emission_factors()

    factor = factors["electricity"]["grid"]

    emissions = consumption_kwh * factor["factor"]

    return {
        "category": "electricity",
        "consumption_kwh": consumption_kwh,
        "emissions_kg_co2e": round(emissions, 3),
        "emission_factor": factor["factor"],
        "unit": factor["unit"],
        "source": factor["source"],
        "verified": factor["verified"]
    }

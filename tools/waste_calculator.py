
from .carbon_calculator import load_emission_factors


def calculate_waste_emissions(
    waste_type: str,
    quantity_grams: float
) -> dict:
    """
    Calculate waste-related carbon emissions.

    Supported waste types:
    - organic_composting
    - organic_landfill

    Args:
        waste_type: Waste type and treatment method.
        quantity_grams: Waste quantity in grams.

    Returns:
        Dictionary containing emissions and source details.
    """

    if quantity_grams <= 0:
        raise ValueError(
            "Waste quantity must be greater than zero."
        )

    waste_type = waste_type.lower().strip()

    factors = load_emission_factors()

    waste_factors = factors.get("waste", {})

    waste = waste_factors.get(waste_type)

    if waste is None:
        raise ValueError(
            f"Unsupported waste type: {waste_type}. "
            f"Supported types: {', '.join(waste_factors.keys())}"
        )

    # Convert grams into kilograms
    quantity_kg = quantity_grams / 1000

    # Calculate emissions using the JSON factor
    emissions = quantity_kg * waste["factor"]

    return {
        "category": "waste",
        "waste_type": waste_type,
        "treatment": waste["treatment"],
        "quantity_grams": quantity_grams,
        "quantity_kg": round(quantity_kg, 3),
        "emissions_kg_co2e": round(emissions, 3),
        "emission_factor": waste["factor"],
        "unit": waste["unit"],
        "source": waste["source"],
        "region": waste.get("region", "Not specified"),
        "verified": waste["verified"]
    }

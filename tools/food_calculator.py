
from .carbon_calculator import load_emission_factors


def calculate_food_emissions(
    food_type: str,
    quantity_grams: float
) -> dict:
    """
    Calculate food-related carbon emissions.

    Args:
        food_type: rice, vegetables, chicken or mutton.
        quantity_grams: Quantity of food consumed in grams.

    Returns:
        Dictionary containing calculated emissions and source.
    """

    if quantity_grams <= 0:
        raise ValueError("Food quantity must be greater than zero.")

    food_type = food_type.lower().strip()

    factors = load_emission_factors()

    food_factors = factors.get("food", {})

    food = food_factors.get(food_type)

    if food is None:
        raise ValueError(
            f"Unsupported food type: {food_type}. "
            f"Supported types: {', '.join(food_factors.keys())}"
        )

    quantity_kg = quantity_grams / 1000

    emissions = quantity_kg * food["factor"]

    return {
        "category": "food",
        "food_type": food_type,
        "quantity_grams": quantity_grams,
        "quantity_kg": round(quantity_kg, 3),
        "emissions_kg_co2e": round(emissions, 3),
        "emission_factor": food["factor"],
        "unit": food["unit"],
        "source": food["source"],
        "region": food.get("region", "Not specified"),
        "verified": food["verified"]
    }

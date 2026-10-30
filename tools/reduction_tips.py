
from datetime import datetime, timezone
from .carbon_calculator import load_emission_factors
from .activity_logger import load_activities


def _get_period_start(period: str):
    """Return the UTC start of the requested reporting period."""
    now = datetime.now(timezone.utc)

    if period == "day":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "week":
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return today.replace(day=today.day) - __import__(
            "datetime"
        ).timedelta(days=today.weekday())

    if period == "month":
        return now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

    raise ValueError("Period must be day, week, or month.")


def _get_period_activities(period: str):
    start = _get_period_start(period)
    activities = load_activities()
    filtered = []

    for activity in activities:
        try:
            timestamp = datetime.fromisoformat(
                activity["timestamp"].replace("Z", "+00:00")
            )

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            if timestamp >= start:
                filtered.append(activity)

        except (KeyError, ValueError, TypeError):
            continue

    return filtered


def suggest_reductions(period: str = "week") -> dict:
    """
    Generate personalized carbon reduction scenarios
    using the user's recorded activities and configured factors.

    Potential savings are scenarios, not achieved reductions.
    """

    if period not in {"day", "week", "month"}:
        return {"error": "Period must be day, week, or month."}

    try:
        factors = load_emission_factors()
        activities = _get_period_activities(period)
    except (ValueError, KeyError, OSError) as error:
        return {"error": str(error)}

    suggestions = []

    for activity in activities:
        category = activity.get("category")
        details = activity.get("details", {})
        emissions = float(activity.get("emissions_kg_co2e", 0))

        # TRANSPORT
        if category == "transport":
            vehicle = (
                details.get("vehicle")
                or details.get("vehicle_type")
                or details.get("mode")
            )

            distance = details.get("distance_km")

            if not vehicle or not distance:
                continue

            if vehicle in {"petrol_bike", "petrol_car"}:
                current_factor = factors["transport"][vehicle]["factor"]
                bus_factor = factors["transport"]["bus"]["factor"]

                # Scenario assumes one passenger and uses the
                # configured vehicle-km factor for the current vehicle.
                # The current petrol factor is an illustrative placeholder.
                potential_savings = max(
                    0, (current_factor - bus_factor) * float(distance)
                )

                if potential_savings > 0:
                    suggestions.append({
                        "category": "transport",
                        "tip": "Consider taking a bus instead of this petrol vehicle journey.",
                        "current_emissions_kg_co2e": round(emissions, 3),
                        "estimated_savings_kg_co2e": round(
                            potential_savings, 3
                        ),
                        "scenario": "Replace this journey with bus travel.",
                        "assumptions": [
                            "Assumes one passenger.",
                            "Petrol vehicle factor is an illustrative placeholder.",
                            "Bus factor is a source-referenced estimate.",
                            "Actual results depend on occupancy and route."
                        ],
                        "status": "scenario_estimate"
                    })

        # ELECTRICITY
        elif category == "electricity":
            consumption = details.get("consumption_kwh")

            if consumption is None:
                continue

            factor_data = factors["electricity"]["grid"]
            factor = float(factor_data["factor"])

            reduced_consumption = float(consumption) * 0.10
            savings = reduced_consumption * factor

            suggestions.append({
                "category": "electricity",
                "tip": "Try reducing unnecessary electricity consumption.",
                "current_emissions_kg_co2e": round(emissions, 3),
                "estimated_savings_kg_co2e": round(savings, 3),
                "scenario": "Reduce electricity consumption by 10%.",
                "assumptions": [
                    "Assumes a 10% reduction in electricity consumption.",
                    "Uses the configured electricity emission factor.",
                    "Electricity factor is an illustrative placeholder."
                ],
                "status": "scenario_estimate"
            })

        # FOOD
        elif category == "food":
            food_type = details.get("food_type")
            quantity_grams = details.get("quantity_grams")

            if not food_type or quantity_grams is None:
                continue

            food_factors = factors["food"]

            if food_type not in {"chicken", "mutton"}:
                continue

            if "vegetables" not in food_factors:
                continue

            quantity_kg = float(quantity_grams) / 1000

            current_factor = float(
                food_factors[food_type]["factor"]
            )
            alternative_factor = float(
                food_factors["vegetables"]["factor"]
            )

            savings = max(
                0,
                (current_factor - alternative_factor) * quantity_kg
            )

            if savings > 0:
                suggestions.append({
                    "category": "food",
                    "tip": "Consider replacing some meat portions with vegetables.",
                    "current_emissions_kg_co2e": round(emissions, 3),
                    "estimated_savings_kg_co2e": round(savings, 3),
                    "scenario": (
                        f"Replace {quantity_grams} grams of {food_type} "
                        "with the same mass of vegetables."
                    ),
                    "assumptions": [
                        "Compares equal food weights.",
                        "Uses global-average food emission factors.",
                        "Actual nutritional and dietary needs may differ."
                    ],
                    "status": "scenario_estimate"
                })

        # WASTE
        elif category == "waste":
            waste_type = details.get("waste_type")
            quantity_grams = details.get("quantity_grams")

            if quantity_grams is None:
                continue

            if waste_type != "organic_landfill":
                continue

            quantity_kg = float(quantity_grams) / 1000

            landfill_factor = float(
                factors["waste"]["organic_landfill"]["factor"]
            )
            compost_factor = float(
                factors["waste"]["organic_composting"]["factor"]
            )

            savings = max(
                0,
                (landfill_factor - compost_factor) * quantity_kg
            )

            if savings > 0:
                suggestions.append({
                    "category": "waste",
                    "tip": "Compost organic waste instead of sending it to landfill.",
                    "current_emissions_kg_co2e": round(emissions, 3),
                    "estimated_savings_kg_co2e": round(savings, 3),
                    "scenario": "Switch the same quantity of organic waste to composting.",
                    "assumptions": [
                        "Compares the same quantity of organic waste.",
                        "Uses configured India waste treatment factors.",
                        "Actual results depend on local waste treatment."
                    ],
                    "status": "scenario_estimate"
                })

    total_potential_savings = sum(
        item["estimated_savings_kg_co2e"]
        for item in suggestions
    )

    return {
        "period": period,
        "suggestion_count": len(suggestions),
        "total_potential_savings_kg_co2e": round(
            total_potential_savings, 3
        ),
        "suggestions": suggestions,
        "note": (
            "These are hypothetical savings scenarios, not achieved "
            "reductions. Estimates depend on emission factors and "
            "assumptions. Some configured factors are illustrative "
            "or global averages."
        )
    }

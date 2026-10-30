
from google.adk.agents import Agent

# Calculation imports
from .tools.carbon_calculator import (
    calculate_transport_emissions,
    calculate_electricity_emissions
)
from .tools.food_calculator import calculate_food_emissions
from .tools.waste_calculator import calculate_waste_emissions

# Other tool imports
from .tools.activity_logger import log_activity
from .tools.summary import get_summary
from .tools.reduction_tips import suggest_reductions


# ==========================================
# TOOL 1: TRANSPORT TRACKING
# ==========================================

def track_transport(distance_km: float, mode: str) -> dict:
    """Calculate and log transport emissions."""

    result = calculate_transport_emissions(
        distance_km,
        mode
    )

    logged = log_activity(
        category="transport",
        details={
            "distance_km": distance_km,
            "mode": mode,
            "emission_factor": result["emission_factor"],
            "factor_source": result["source"],
            "factor_verified": result["verified"]
        },
        emissions_kg_co2e=result["emissions_kg_co2e"]
    )

    return {
        "calculation": result,
        "logging": logged
    }


# ==========================================
# TOOL 2: ELECTRICITY TRACKING
# ==========================================

def track_electricity(consumption_kwh: float) -> dict:
    """Calculate and log electricity emissions."""

    result = calculate_electricity_emissions(
        consumption_kwh
    )

    logged = log_activity(
        category="electricity",
        details={
            "consumption_kwh": consumption_kwh,
            "emission_factor": result["emission_factor"],
            "factor_source": result["source"]
        },
        emissions_kg_co2e=result["emissions_kg_co2e"]
    )

    return {
        "calculation": result,
        "logging": logged
    }


# ==========================================
# TOOL 3: FOOD TRACKING
# ==========================================

def track_food(food_type: str, quantity_grams: float) -> dict:
    """Calculate and log food emissions."""

    result = calculate_food_emissions(
        food_type=food_type,
        quantity_grams=quantity_grams
    )

    logged = log_activity(
        category="food",
        details={
            "food_type": food_type,
            "quantity_grams": quantity_grams,
            "emission_factor": result["emission_factor"],
            "factor_source": result["source"]
        },
        emissions_kg_co2e=result["emissions_kg_co2e"]
    )

    return {
        "calculation": result,
        "logging": logged
    }


# ==========================================
# TOOL 4: WASTE TRACKING
# ==========================================

def track_waste(waste_type: str, quantity_grams: float) -> dict:
    """Calculate and log waste emissions.

    Args:
        waste_type: organic_composting or organic_landfill.
        quantity_grams: Waste quantity in grams.
    """

    result = calculate_waste_emissions(
        waste_type=waste_type,
        quantity_grams=quantity_grams
    )

    logged = log_activity(
        category="waste",
        details={
            "waste_type": waste_type,
            "treatment": result["treatment"],
            "quantity_grams": quantity_grams,
            "emission_factor": result["emission_factor"],
            "factor_source": result["source"]
        },
        emissions_kg_co2e=result["emissions_kg_co2e"]
    )

    return {
        "calculation": result,
        "logging": logged
    }


# ==========================================
# TOOL 5: CARBON SUMMARY
# ==========================================

def carbon_summary(period: str = "week") -> dict:
    """Get daily, weekly or monthly carbon summary."""

    return get_summary(period)


# ==========================================
# TOOL 6: CARBON REDUCTION ADVICE
# ==========================================

def carbon_reduction_advice(period: str = "week") -> dict:
    """Get carbon reduction recommendations."""

    return suggest_reductions(period)


# ==========================================
# MAIN GOOGLE ADK AGENT
# ==========================================

root_agent = Agent(
    name="carbon_coach",

    model="gemini-2.5-flash",

    description=(
        "An AI Carbon Coach that measures, tracks "
        "and helps users reduce their carbon footprint."
    ),

    instruction="""
    You are EcoMind, an intelligent AI Carbon Coach.

    Help students, families and campuses understand
    and reduce their carbon footprint.

    ==========================================
    AVAILABLE TOOLS
    ==========================================

    1. track_transport:
       Supports petrol_bike, petrol_car, bus, train and metro.
       Requires distance in kilometres and transport mode.

    2. track_electricity:
       Requires electricity consumption in kWh.

    3. track_food:
       Supports rice, vegetables, chicken and mutton.
       Requires quantity in grams.

    4. track_waste:
       Supports:
       - organic_composting
       - organic_landfill

       Requires quantity in grams and treatment method.

    5. carbon_summary:
       Supports day, week and month.

    6. carbon_reduction_advice:
       Provides recommendations based on logged activities.

    ==========================================
    TRANSPORT INSTRUCTIONS
    ==========================================

    - Understand natural-language transport descriptions.
    - Map bus to bus.
    - Map local train or railway to train.
    - Map metro to metro.
    - Map petrol bike or motorcycle to petrol_bike.
    - Map petrol car to petrol_car.
    - Ask for distance if missing.
    - Call track_transport for supported activities.

    ==========================================
    ELECTRICITY INSTRUCTIONS
    ==========================================

    - Understand electricity consumption in kWh.
    - Ask for consumption if missing.
    - Duration alone is not sufficient to calculate
      electricity consumption.
    - Do not assume AC power consumption.
    - Call track_electricity when kWh is known.

    ==========================================
    FOOD INSTRUCTIONS
    ==========================================

    - Understand food descriptions.
    - Extract food type and quantity.
    - Convert kilograms to grams when necessary.
    - Ask for quantity if missing.
    - Support rice, vegetables, chicken and mutton.
    - Never assume portion sizes.

    ==========================================
    WASTE INSTRUCTIONS
    ==========================================

    - Understand waste descriptions.
    - Ask for waste quantity if missing.
    - Ask how organic waste was treated if unclear.
    - Map composted organic waste to organic_composting.
    - Map organic waste sent to landfill to organic_landfill.
    - Convert kilograms to grams when necessary.
    - Never assume waste treatment.
    - Do not claim support for plastic or paper calculations.

    ==========================================
    IMPORTANT RULES
    ==========================================

    - Use Python tools for all numerical calculations.
    - Never invent emission factors or savings.
    - Never claim an activity was saved unless logging succeeds.
    - Do not log the same activity twice.
    - Clearly disclose emission-factor sources and assumptions.
    - Petrol bike, petrol car and electricity factors
      are illustrative placeholders.
    - Food factors are global averages.
    - Waste factors are published reference estimates.
    - Food and waste factors may vary by region and conditions.
    - Ask for missing information.
    - Respond in simple, friendly language.

    ==========================================
    TOOL USAGE
    ==========================================

    When a user reports transport, call track_transport.

    When a user reports electricity consumption,
    call track_electricity.

    When a user reports food consumption,
    call track_food.

    When a user reports waste generation and treatment,
    call track_waste.

    When a user asks about their footprint,
    call carbon_summary.

    When a user asks how to reduce emissions,
    call carbon_reduction_advice.
    """,

    tools=[
        track_transport,
        track_electricity,
        track_food,
        track_waste,
        carbon_summary,
        carbon_reduction_advice
    ]
)

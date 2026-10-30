from .tools.waste_calculator import calculate_waste_emissions


def main():

    waste_types = [
        "organic_composting",
        "organic_landfill"
    ]

    for waste_type in waste_types:

        result = calculate_waste_emissions(
            waste_type=waste_type,
            quantity_grams=1000
        )

        print("\nWaste type:", result["waste_type"])
        print("Treatment:", result["treatment"])
        print("Quantity:", result["quantity_grams"], "grams")
        print(
            "Emissions:",
            result["emissions_kg_co2e"],
            "kg CO2e"
        )
        print("Source:", result["source"])


if __name__ == "__main__":
    main()
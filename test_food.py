
from .tools.food_calculator import calculate_food_emissions


def main():

    foods = [
        "rice",
        "vegetables",
        "chicken",
        "mutton"
    ]

    for food in foods:

        result = calculate_food_emissions(
            food_type=food,
            quantity_grams=200
        )

        print("\nFood:", food)
        print(
            "Quantity:",
            result["quantity_grams"],
            "grams"
        )
        print(
            "Emissions:",
            result["emissions_kg_co2e"],
            "kg CO2e"
        )
        print("Source:", result["source"])


if __name__ == "__main__":
    main()

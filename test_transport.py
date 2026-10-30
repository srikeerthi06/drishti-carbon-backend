from .tools.carbon_calculator import calculate_transport_emissions


def main():
    modes = [
        "bus",
        "train",
        "metro",
        "petrol_bike",
        "petrol_car"
    ]

    for mode in modes:
        result = calculate_transport_emissions(
            distance_km=12,
            vehicle_type=mode
        )

        print("\nTransport:", mode)
        print(
            "Emissions:",
            result["emissions_kg_co2e"],
            "kg CO2e"
        )
        print("Source:", result["source"])
        print("Verified:", result["verified"])


if __name__ == "__main__":
    main()
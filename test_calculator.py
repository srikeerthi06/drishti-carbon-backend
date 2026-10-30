
from tools.carbon_calculator import (
    calculate_transport_emissions,
    calculate_electricity_emissions
)

bike_result = calculate_transport_emissions(
    distance_km=15,
    vehicle_type="petrol_bike"
)

electricity_result = calculate_electricity_emissions(
    consumption_kwh=5
)

print("Transport:", bike_result)
print("Electricity:", electricity_result)

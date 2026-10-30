
from tools.activity_logger import log_activity, load_activities

result = log_activity(
    category="transport",
    details={
        "vehicle": "petrol_bike",
        "distance_km": 15
    },
    emissions_kg_co2e=1.5
)

print(result)
print("Total activities:", len(load_activities()))

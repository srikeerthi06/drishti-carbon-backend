
import json
from pathlib import Path
from datetime import datetime, timezone

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "activities.json"
)


def load_activities():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def log_activity(
    category: str,
    details: dict,
    emissions_kg_co2e: float
) -> dict:
    """Save a calculated carbon activity."""

    if category not in {
        "transport", "electricity", "food", "waste"
    }:
        raise ValueError("Unsupported activity category.")

    if emissions_kg_co2e < 0:
        raise ValueError("Emissions cannot be negative.")

    activities = load_activities()

    record = {
        "id": len(activities) + 1,
        "category": category,
        "details": details,
        "emissions_kg_co2e": round(emissions_kg_co2e, 3),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    activities.append(record)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(activities, file, indent=4)

    return {
        "success": True,
        "message": "Activity logged successfully.",
        "activity": record
    }

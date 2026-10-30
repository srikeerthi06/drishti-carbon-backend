
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "activities.json"
)


def load_activities():
    """Load all saved carbon activities."""

    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_timestamp(timestamp):
    """Convert an ISO timestamp into a timezone-aware datetime."""

    try:
        parsed = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except (ValueError, TypeError, AttributeError):
        return None


def get_period_start(period, now):
    """Get the beginning of the requested reporting period."""

    if period == "day":
        return now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    elif period == "week":
        start = now - timedelta(days=now.weekday())

        return start.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    elif period == "month":
        return now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

    else:
        raise ValueError(
            "Period must be day, week or month."
        )


def calculate_category_totals(activities):
    """Calculate emissions for each activity category."""

    category_totals = {}

    for activity in activities:

        category = activity.get("category", "unknown")

        emissions = float(
            activity.get("emissions_kg_co2e", 0)
        )

        category_totals[category] = (
            category_totals.get(category, 0) + emissions
        )

    return {
        category: round(total, 3)
        for category, total in category_totals.items()
    }


def get_summary(period="week"):
    """
    Calculate carbon footprint summary.

    Supported periods:
    day, week and month.
    """

    now = datetime.now(timezone.utc)

    start = get_period_start(period, now)

    activities = load_activities()

    filtered_activities = []

    for activity in activities:

        timestamp = parse_timestamp(
            activity.get("timestamp")
        )

        if timestamp is None:
            continue

        if start <= timestamp <= now:
            filtered_activities.append(activity)

    category_totals = calculate_category_totals(
        filtered_activities
    )

    total_emissions = sum(
        category_totals.values()
    )

    highest_category = (
        max(category_totals, key=category_totals.get)
        if category_totals else None
    )

    return {
        "period": period,
        "total_emissions_kg_co2e": round(
            total_emissions, 3
        ),
        "activity_count": len(filtered_activities),
        "category_totals": category_totals,
        "highest_emission_category": highest_category
    }


def get_monthly_trend(months=6):
    """
    Return monthly emissions for the last N months.

    Useful for the dashboard's monthly emissions chart.
    """

    if not isinstance(months, int) or months < 1 or months > 24:
        raise ValueError("Months must be between 1 and 24.")

    now = datetime.now(timezone.utc)

    activities = load_activities()

    monthly_data = []

    # Generate month labels from oldest to newest.
    year = now.year
    month = now.month

    for _ in range(months - 1):
        month -= 1

        if month == 0:
            month = 12
            year -= 1

    for _ in range(months):

        monthly_data.append({
            "year": year,
            "month": month,
            "label": datetime(
                year, month, 1
            ).strftime("%b %Y"),
            "total_emissions_kg_co2e": 0.0,
            "activity_count": 0
        })

        month += 1

        if month == 13:
            month = 1
            year += 1

    month_lookup = {
        (item["year"], item["month"]): item
        for item in monthly_data
    }

    for activity in activities:

        timestamp = parse_timestamp(
            activity.get("timestamp")
        )

        if timestamp is None:
            continue

        key = (timestamp.year, timestamp.month)

        if key not in month_lookup:
            continue

        item = month_lookup[key]

        item["total_emissions_kg_co2e"] += float(
            activity.get("emissions_kg_co2e", 0)
        )

        item["activity_count"] += 1

    for item in monthly_data:

        item["total_emissions_kg_co2e"] = round(
            item["total_emissions_kg_co2e"], 3
        )

        # Remove internal fields from chart output.
        item.pop("year")
        item.pop("month")

    return monthly_data


def get_weekly_trend():
    """Return daily emissions for the current week."""

    now = datetime.now(timezone.utc)

    start = get_period_start("week", now)

    activities = load_activities()

    daily_data = []

    for day_offset in range(7):

        current_day = start + timedelta(days=day_offset)

        daily_data.append({
            "date": current_day.strftime("%Y-%m-%d"),
            "label": current_day.strftime("%a"),
            "total_emissions_kg_co2e": 0.0,
            "activity_count": 0
        })

    daily_lookup = {
        item["date"]: item
        for item in daily_data
    }

    for activity in activities:

        timestamp = parse_timestamp(
            activity.get("timestamp")
        )

        if timestamp is None:
            continue

        date_key = timestamp.strftime("%Y-%m-%d")

        if date_key not in daily_lookup:
            continue

        item = daily_lookup[date_key]

        item["total_emissions_kg_co2e"] += float(
            activity.get("emissions_kg_co2e", 0)
        )

        item["activity_count"] += 1

    for item in daily_data:

        item["total_emissions_kg_co2e"] = round(
            item["total_emissions_kg_co2e"], 3
        )

    return daily_data


def get_dashboard_data():
    """
    Return all data required by the carbon dashboard.
    """

    return {
        "daily_summary": get_summary("day"),
        "weekly_summary": get_summary("week"),
        "monthly_summary": get_summary("month"),
        "monthly_trend": get_monthly_trend(6),
        "weekly_trend": get_weekly_trend()
    }

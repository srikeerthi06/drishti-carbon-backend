
from .tools.summary import (
    get_summary,
    get_monthly_trend,
    get_weekly_trend,
    get_dashboard_data
)


def main():

    print("\n========== DAILY SUMMARY ==========")
    print(get_summary("day"))

    print("\n========== WEEKLY SUMMARY ==========")
    print(get_summary("week"))

    print("\n========== MONTHLY SUMMARY ==========")
    print(get_summary("month"))

    print("\n========== MONTHLY TREND ==========")
    print(get_monthly_trend(6))

    print("\n========== WEEKLY TREND ==========")
    print(get_weekly_trend())

    print("\n========== COMPLETE DASHBOARD DATA ==========")
    print(get_dashboard_data())


if __name__ == "__main__":
    main()

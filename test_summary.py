
from tools.summary import get_summary

print("TODAY'S CARBON FOOTPRINT")

result = get_summary("day")

print(result)

print("\nWEEKLY CARBON FOOTPRINT")

result = get_summary("week")

print(result)

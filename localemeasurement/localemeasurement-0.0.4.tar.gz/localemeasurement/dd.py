from localeconversion import unitConversion
from localeconversion import DISTANCE
a = {"km": [10]}
print(unitConversion(DISTANCE, "hi_IN", **{"km": [10, 1]}))

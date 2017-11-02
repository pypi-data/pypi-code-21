
from aget.models import _merge_intervals, _find_gaps


intervals = [
    (0, 0),
    (2, 10),
    (3, 8),
    (3, 4),
    (9, 20),
    (30, 40),
    (40, 40)
]


intervals = _merge_intervals(intervals)
print(intervals)

gaps = _find_gaps(intervals)
print(gaps)

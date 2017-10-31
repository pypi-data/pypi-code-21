from typing import Tuple


def increment_mean(mean : float, count : int, new_value : float) -> Tuple[float, int]:
    new_count = count + 1 
    new_mean = mean + ((new_value - mean) / new_count)
    return new_mean, new_count 
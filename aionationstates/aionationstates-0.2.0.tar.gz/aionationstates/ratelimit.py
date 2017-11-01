"""Decorators for compliance with NationStates' API and web rate limits."""

import time
import asyncio
from functools import partial


# Measured in seconds between each request:
# (with a bit of wiggle room added)
api_limit = 0.6 + 0.1  # https://www.nationstates.net/pages/api.html#ratelimits
web_limit = 6 + 0.5    # https://forum.nationstates.net/viewtopic.php?p=16394966#p16394966


# A hack to make them mutable
last_time_called_api = [0]
last_time_called_web = [0]


def _rate_limiter(func, limit, last_time_called):
    async def wrapper(*args, **kwargs):
        elapsed = time.perf_counter() - last_time_called[0]
        left_to_wait = limit - elapsed
        if left_to_wait > 0:
            last_time_called[0] = time.perf_counter() + left_to_wait
            await asyncio.sleep(left_to_wait)
        else:
            last_time_called[0] = time.perf_counter()

        return await func(*args, **kwargs)
    return wrapper


api = partial(
    _rate_limiter,
    limit=api_limit, last_time_called=last_time_called_api
)

web = partial(
    _rate_limiter,
    limit=web_limit, last_time_called=last_time_called_web
)



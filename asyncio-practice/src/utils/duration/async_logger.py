import time
import functools
from datetime import datetime
import asyncio

def async_logger(func):
    @functools.wraps(func)
    async def wapper(*args, **kwargs):
        enter_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        start_time = time.perf_counter()
        print(f">>> [ASYNC START]: {func.__name__} at {enter_time}")

        result = await func(*args, **kwargs)

        end_time = time.perf_counter()
        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f">>> [ASYNC END]: {func.__name__} at {exit_time}, duration: {end_time - start_time:.4f} s")
        return result
    return wapper

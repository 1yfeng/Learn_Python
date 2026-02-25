import time 
import functools
from datetime import datetime

def logger(func):
    @functools.wraps(func)
    def wapper(*args, **kwargs):
        enter_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        start_time = time.perf_counter()
        print(f">>> start: {func.__name__} at {enter_time}")

        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f">>> end: {func.__name__} at {exit_time}, duration: {end_time - start_time:.4f} s")
        return result
    return wapper

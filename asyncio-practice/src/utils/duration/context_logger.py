from contextlib import contextmanager
from datetime import datetime
import time

@contextmanager
def timer(label):
        enter_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        start_time = time.perf_counter()
        print(f">>> start: {label} at {enter_time}")
        try:
            yield
        finally:
            end_time = time.perf_counter()
            exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f">>> end: {label} at {exit_time}, duration: {end_time - start_time:.4f} s")
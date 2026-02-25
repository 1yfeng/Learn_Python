import asyncio
import time
from datetime import datetime


class EventLoopExperiment:
    def mook_io_operation(self, id: int):
        time.sleep(id)
        print(f"IO operation for id={id} completed")

    async def async_mook_io_operation(self, id: int):
        await asyncio.sleep(id)
        print(f"IO operation for id={id} completed")

""" 
def main():
    enter_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    start_time = time.perf_counter()
    print(f">>> start: at {enter_time}")
    exp = EventLoopExperiment()
    exp.mook_io_operation(1)
    exp.mook_io_operation(2)
    exp.mook_io_operation(3)
    
    end_time = time.perf_counter()
    exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f">>> end: at {exit_time}, duration: {end_time - start_time:.4f} s")

 """
async def main():
    enter_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    start_time = time.perf_counter()
    print(f">>> start: at {enter_time}")
    print("experiment only asyncio.create_task")
    exp = EventLoopExperiment()
    # await exp.async_mook_io_operation(1)
    # await exp.async_mook_io_operation(2)
    # await exp.async_mook_io_operation(3)

    # await asyncio.gather(
    #     exp.async_mook_io_operation(1),
    #     exp.async_mook_io_operation(2),
    #     exp.async_mook_io_operation(3),
    # )

    task1 = asyncio.create_task(exp.async_mook_io_operation(1))
    task2 = asyncio.create_task(exp.async_mook_io_operation(2))
    task3 = asyncio.create_task(exp.async_mook_io_operation(3))
    await task3
    print("task3 end")
    await task2
    print("task2 end")
    await task1
    print("task1 end")

    end_time = time.perf_counter()
    exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f">>> end: at {exit_time}, duration: {end_time - start_time:.4f} s")


if __name__ == "__main__":
    # main()
    asyncio.run(main())

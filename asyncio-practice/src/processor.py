import asyncio
import time
from utils.duration.async_logger import async_logger
from utils.duration.logger import logger

class Processor:
    async def async_mock_io_operation(self, id: int):
        await asyncio.sleep(1)
        print(f"IO operation for id={id} completed")

    @logger
    def mock_call(self, id: int):
        for i in range(5):
            time.sleep(1)
            print(f"Processing id={id}: step {i + 1}/5")

    @async_logger
    async def async_mock_call(self, id: int):
        for i in range(5):
            await self.async_mock_io_operation(i)

    
    @async_logger
    async def async_gather_mock_call(self, id: int):
        tasks = []
        for i in range(5):
            tasks.append(self.async_mock_io_operation(id))
        await asyncio.gather(*tasks)
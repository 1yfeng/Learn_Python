import pytest
from processor import Processor

class TestAsyncAPI:
    def test_mock_call_api(self):
        print()
        processor = Processor()
        processor.mock_call(1)

    async def test_async_mock_call_api(self):
        print()
        processor = Processor()
        await processor.async_mock_call(1)


    async def test_async_gather_mock_call_api(self):
        print()
        processor = Processor()
        await processor.async_gather_mock_call(1)

        
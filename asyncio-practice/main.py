import asyncio

from core.operation import Operation


async def main():
    op = Operation()
    result = await op.htttp_get("https://www.example.com")
    print("GET request result:", result.text[:100])  # Print the first 100 characters of the response


if __name__ == "__main__":
    asyncio.run(main())

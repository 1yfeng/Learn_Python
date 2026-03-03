import httpx
class Operation:
    async def htttp_get(self, url: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            print(f"GET request to {url} completed with status code {response.status_code}")
            return response
        
    async def htttp_post(self, url: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            print(f"POST request to {url} completed with status code {response.status_code}")
            return response
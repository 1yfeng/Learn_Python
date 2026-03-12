from pymilvus import MilvusClient as PyMilvusClients
import asyncio 
class MilvusClient:
    def __init__(self, uri = "http://localhost:19530"):
        self.client = PyMilvusClients(uri)

    async def create_collection(self, name: str, dim: int):
        await asyncio.to_thread(self.client.create_collection, collection_name=name, dimension=dim)
        print(f"Collection '{name}' created with dimension {dim}.")

    async def insert(self, collection_name: str, vectors:list, texts: list, metadatas: list = None):
        data = []
        for i, (vec, text) in enumerate(zip(vectors, texts)):
            row = {
                "vector": vec,
                "text": text
            }
            if metadatas:
                row["metadata"] = metadatas[i]
            data.append(row)

        result = await asyncio.to_thread(
            self.client.insert, 
            collection_name = collection_name,
            data = data
            )
        print(f"Inserted {len(vectors)} vectors into '{collection_name}'. Result: {result}")
        return result
    async def search(self, collection_name: str, query_vector: list, limit: int = 3):
        results = await asyncio.to_thread(
            self.client.search,
            collection_name = collection_name,
            data = [query_vector],
            limit = limit,
            output_fields = ["text", "metadata"]
        )
        return results
    
    async def close(self):
        await asyncio.to_thread(self.client.close)
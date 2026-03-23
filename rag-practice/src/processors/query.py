import asyncio
import time

print("[Init] 加载 Embedding 模块...", flush=True)
from src.processors.embedding_processor import EmbeddingProcessor
print("[Init] 加载 Milvus 客户端模块...", flush=True)
from clients.async_milvus_client import AsyncMilvusClient
print("[Init] 模块加载完成")


class QueryProcessor:
    def __init__(self, collection_name: str = "pdf_chunks_recursive_collection"):
        self.collection_name = collection_name
        print("[Init] 加载 Embedding 模型 (shibing624/text2vec-base-chinese)...", flush=True)
        t0 = time.time()
        self.embedder = EmbeddingProcessor()
        print(f"[Init] Embedding 模型加载完成 ({time.time() - t0:.1f}s)")
        print("[Init] 连接 Milvus...", flush=True)
        self.milvus = AsyncMilvusClient()
        print("[Init] Milvus 连接就绪")

    async def query(self, question: str, collection_name: str = "pdf_chunks_recursive_collection", top_k: int = 3):
        """将问题 embedding 后检索 Milvus，返回最相似的 top_k 个结果"""
        print(f"\n[Query] 问题: {question}")

        print(f"[Query] 生成问题的向量表示...")
        query_vector = self.embedder.model.embed_query(question)
        print(f"[Query] 向量维度: {len(query_vector)}")
        print(f"{'─'*80}")
        print(f"[Query 向量]: {query_vector}")
        print(f"{'─'*80}")
        
        print(f"[Query] 检索 Collection: '{collection_name}', top_k={top_k}")
        results = await self.milvus.search(collection_name, query_vector, limit=top_k)

        # 解析结果
        hits = results[0] if results else []
        print(f"\n[Query] 返回 {len(hits)} 条结果")
        print(f"{'='*80}")
        for i, hit in enumerate(hits):
            score = hit.get("distance", 0)
            text = hit.get("entity", {}).get("text", "")
            metadata = hit.get("entity", {}).get("metadata", {})
            vector = hit.get("entity", {}).get("vector", [])
            print(f"  [{i+1}] 相似度: {score:.4f}")
            print(f"       来源: {metadata}")
            print(f"       内容: {text}")
            print(f"       向量: {vector}")
            print(f"{'─'*80}")

        return hits

    async def close(self):
        await self.milvus.close()


if __name__ == "__main__":

    async def main():
        qp = QueryProcessor()
        results = await qp.query("分代收集原理", top_k=3)
        await qp.close()

    asyncio.run(main())

import asyncio
import uuid
from pathlib import Path
from processors.embedding_processor import EmbeddingProcessor
from clients.async_milvus_client import AsyncMilvusClient

class PageIndexEngine:
    def __init__(self, llm_client, milvus: AsyncMilvusClient, embeddings: EmbeddingProcessor, persist_directory="./storage", llm_client=None):

        self.milvus = milvus
        self.embedder = embeddings
        self.llm_client = llm_client

        self.docstore_path = Path(persist_directory)
        self.docstore_path.mkdir(parents=True, exist_ok=True)

    async def init_collection(self, collection_name: str):
        dim = self.embedder.get_dim()
        await self.milvus.create_collection(collection_name, dim)

    async def _generate_summary(self, text: str) -> str:
        if self.llm_client:
            return await self.llm_client.generate_summary(text)
        return text[:200]
    
    async def _save_page(self, page_id: str, page: PageNode):
        file = self.docstore_path / f"{page_id}.json"
        file.write_text(page.model_dump_json(ensure_ascii=False), encoding="utf-8")
    
    def _load_page(self, page_id: str) -> PageNode | None:
        file = self.docstore_path / f"{page_id}.json"
        if not file.exists():
            return None
        return PageNode.model_validate_json(file.read_text(encoding="utf-8"))
    
    """ build index  """
    async def add_pages(self, pages: list[PageNode], source: str = "unknow"):
        print(f"start to add {len(pages)} pages to index...")

        summary_task = [self._generate_summary(p.content) for p in pages]
        summaries = await asyncio.gather(*summary_task)

        vectors = self.embed_text(summaries)

        texts = []
        metadatas = []
        for page, summary in zip(pages, summaries):
            pid = str(uuid.uuid4())
            texts.append(summary)
            metadatas.append({
                self.id_key: pid,
                "source": source,
                "page_label": page.page_label
            })
            page.summary = summary
            self._save_page(pid, page)
        
        await self.milvus.insert(
            collection_name = self.collection_name,
            vectors=vectors,
            texts=texts,
            metadatas = metadatas
        )
        print(f"✅ {len(pages)} pages added to index successfully!")
        


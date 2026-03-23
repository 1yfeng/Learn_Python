import os
import sys
import asyncio
import threading
import time
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.processors.embedding_processor import EmbeddingProcessor
from clients.async_milvus_client import AsyncMilvusClient

class PdfProcessor:

    def _spinner(self, stop_event: threading.Event, prefix: str = ""):
        """后台线程：显示动态 loading 动画"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while not stop_event.is_set():
            print(f"\r{prefix} {frames[idx % len(frames)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)
        print(f"\r{prefix}   ", end="\r", flush=True)  # 清除 spinner

    def get_pdf_paths(self, pdf_folder: str):
        paths = []
        for root, _, files in os.walk(pdf_folder):
            for file in files:
                if file.endswith(".pdf"):
                    paths.append(os.path.join(root, file))
        return paths
    
    def load_pdf(self, pdf_path: str) -> list[Document]:
        loader = PyPDFLoader(pdf_path)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # 抑制 pypdf 的格式警告
            try:
                pages = loader.load()
            except Exception as e:
                print(f"  ⚠️ 加载 {os.path.basename(pdf_path)} 出错: {e}，尝试逐页加载...")
                pages = self._load_pdf_safe(pdf_path)
        return pages

    def _load_pdf_safe(self, pdf_path: str) -> list[Document]:
        """逐页加载，跳过有问题的页面"""
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    text = page.extract_text() or ""
                pages.append(Document(
                    page_content=text,
                    metadata={"source": pdf_path, "page": i}
                ))
            except Exception as e:
                print(f"  ⚠️ 跳过第 {i+1} 页: {e}")
        return pages
    
    async def process(self, pdf_folder: str, start_page: int = None, end_page: int = None):
        # --- 步骤 1: 扫描 PDF ---
        print(f"[步骤 1] 扫描目录: {pdf_folder}")
        pdf_paths = self.get_pdf_paths(pdf_folder)
        print(f"[步骤 1] 找到 {len(pdf_paths)} 个 PDF 文件")

        print(f"[步骤 2] 加载 PDF 内容...")
        all_pages: list[Document] = []
        for i, pdf__path in enumerate(pdf_paths, 1):
            file_name = os.path.basename(pdf__path)
            file_size = os.path.getsize(pdf__path) / 1024 / 1024  # MB
            prefix = f"  [{i}/{len(pdf_paths)}] 正在加载: {file_name} ({file_size:.1f} MB)..."
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=self._spinner, args=(stop_event, prefix), daemon=True)
            spinner_thread.start()
            pages = self.load_pdf(pdf__path)
            stop_event.set()
            spinner_thread.join()
            all_pages.extend(pages)
            print(f"{prefix} ✔ {len(pages)} 页")

        print(f"[步骤 2] 加载完成，共 {len(all_pages)} 页")

        # 按页码范围过滤（页码从1开始）
        if start_page or end_page:
            s = (start_page or 1) - 1  # 转为0-based索引
            e = end_page or len(all_pages)
            all_pages = all_pages[s:e]
            print(f"[步骤 2] 过滤后保留第 {start_page or 1} ~ {end_page or '末尾'} 页，共 {len(all_pages)} 页")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=60,
            separators = ["\n\n", "\n", ".","!","?"," ","。","！","？"," ",""]
            )
        
        
        # --- 步骤 4: 两种策略对比 ---

        # 策略A: 按页直接用（不切分，每页=一个chunk）
        chunks_page_only = all_pages

        # 策略B: 递归切分（每页再按 600 字符切细）
        chunks_recursive = text_splitter.split_documents(all_pages)

        # --- 步骤 5: 输出对比 ---
        print(f"\n[对比结果]")
        print(f"  A-按页切分: {len(chunks_page_only)} 个切片")
        print(f"  B-递归切分: {len(chunks_recursive)} 个切片")

        for label, chunks in [("A-按页", chunks_page_only), ("B-递归", chunks_recursive)]:
            if chunks:
                lengths = [len(c.page_content) for c in chunks]
                print(f"  [{label}] 长度: 最小={min(lengths)}, 最大={max(lengths)}, 平均={sum(lengths)//len(lengths)}")
 
        print(f"\n[步骤 3] 初始化 Embedding 模型和 Milvus 客户端...")
        embedder = EmbeddingProcessor()
        milvus = AsyncMilvusClient()
        print(f"[步骤 3] Embedding 模型: {embedder.model.model_name}, 维度: {embedder.get_dim()}")
        print(f"[步骤 3] Milvus 连接就绪")

        # be careful list order！！！！
        print(f"\n[步骤 4] 准备数据...")
        texts = [chunk.page_content  for chunk in chunks_recursive]
        metadatas = [chunk.metadata  for chunk in chunks_recursive]
        print(f"[步骤 4] texts: {len(texts)} 条, metadatas: {len(metadatas)} 条")
        
        print(f"\n[步骤 5] 生成向量 (共 {len(texts)} 条文本)...")
        vectors = embedder.embed_text(texts)
        print(f"[步骤 5] 向量生成完成, 共 {len(vectors)} 个, 维度: {len(vectors[0]) if vectors else 'N/A'}")

        collection_name = "pdf_chunks_recursive_collection"
        print(f"\n[步骤 6] 创建 Milvus Collection: '{collection_name}'...")
        await milvus.create_collection(name=collection_name, dim=embedder.get_dim())
        print(f"[步骤 6] Collection 创建完成")

        print(f"\n[步骤 7] 写入 Milvus (共 {len(vectors)} 条记录)...")
        await milvus.insert(collection_name, vectors, texts, metadatas)
        print(f"[步骤 7] ✅ 写入完成!")
     
        return 
    
    # ai generate 
    def print_chunks(self, chunks: list[Document], max_display: int = sys.maxsize):
        """输出所有切片完整内容"""
        print(f"\n{'='*80}")
        print(f"共 {len(chunks)} 个切片")
        print(f"{'='*80}")
        for i, chunk in enumerate(chunks):
            if i > max_display:
                break
            print(f"\n--- 切片 #{i+1} ---")
            print(f"  元数据: {chunk.metadata}")
            print(f"  长度: {len(chunk.page_content)} 字符")
            print(f"  内容:\n{chunk.page_content[:max_display]}{'...' if len(chunk.page_content) > max_display else ''}")
        print(f"\n{'='*80}")


if __name__ == "__main__":
    processor = PdfProcessor()
    asyncio.run(processor.process(r"C:\Users\yufengli\my_work_space\Resources", start_page=3, end_page=192))
    
    
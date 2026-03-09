import asyncio
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
# TODO: 调通图片处理后取消注释
# from clients.copilot_client_enricher import CopilotClientEnricher


class MarkdownProcessor:
    def get_md_paths(self, md_folder: str):
        paths = []
        for root, _, files in os.walk(md_folder):
            for file in files:
                if file.endswith(".md"):
                    paths.append(os.path.join(root, file))
        return paths

    def load_docs(self, md_folder: str) -> list[Document]:
        loader = DirectoryLoader(md_folder, glob="**/*.md", loader_cls=TextLoader)
        raw_docs = loader.load()
        print(f"Loaded Markdown from: {md_folder}, total documents: {len(raw_docs)}")
        return raw_docs

    # --- 第二步：结构化标题切分 (保留上下文) ---
    def struct_spplit(self):
        headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ]
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        return header_splitter

    def get_image_descriptions(self, image_path: str) -> str:

        # Placeholder for actual image description extraction logic
        return ["Image description 1", "Image description 2"]

    async def process(self, md_folder: str):
        print(f"[步骤 1/5] 扫描目录: {md_folder}")
        file_paths = self.get_md_paths(md_folder)
        print(f"[步骤 1/5] 找到 {len(file_paths)} 个 Markdown 文件")

        final_chunks = []
        # TODO: 调通图片处理后取消注释，启用图片描述enrichment
        # print(f"[步骤 2/5] 开始异步处理文件（图片描述等）...")
        # async with CopilotClientEnricher(concurrrency_limit=5) as enricher:
        #     tasks = [
        #         enricher.process_single_file(file_path, enricher)
        #         for file_path in file_paths
        #     ]
        #     raw_docs = await asyncio.gather(*tasks)
        # print(f"[步骤 2/5] 异步处理完成，得到 {len(raw_docs)} 个文档")

        # 临时：直接读取文件内容，跳过图片处理
        print(f"[步骤 2/5] 读取文件内容（跳过图片处理）...")
        raw_docs = []
        for fp in file_paths:
            with open(fp, 'r', encoding='utf-8') as f:
                raw_docs.append(f.read())
        print(f"[步骤 2/5] 读取完成，得到 {len(raw_docs)} 个文档")

        print(f"[步骤 3/5] 初始化切分器...")
        header_splitter = self.struct_spplit()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=60,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""],
        )
        print(f"[步骤 3/5] 切分器就绪（标题切分 + 递归字符切分）")

        print(f"[步骤 4/5] 开始切分文档...")
        for i, (content, file_path) in enumerate(zip(raw_docs, file_paths)):
            file_name = os.path.basename(file_path)
            splits_struct = header_splitter.split_text(content)
            chunks = text_splitter.split_documents(splits_struct)
            for chunk in chunks:
                chunk.metadata["source"] = file_name
                final_chunks.append(chunk)
            print(f"  [{i+1}/{len(raw_docs)}] {file_name}: 标题切分 {len(splits_struct)} 段 → 最终 {len(chunks)} 个切片")
        
        # --- 验证结果 ---
        print(f"[步骤 5/5] ✅ 最终生成 {len(final_chunks)} 个高质量切片")
        if final_chunks:
            print(f"  [切片示例] 元数据: {final_chunks[0].metadata}")
            print(f"  [切片示例] 内容预览: {final_chunks[0].page_content[:150]}...")
        return final_chunks

    def print_chunks(self, chunks: list[Document], max_content_len: int = 200):
        """输出所有切片的详细信息，方便调试查看。"""
        print(f"\n{'='*80}")
        print(f"共 {len(chunks)} 个切片")
        print(f"{'='*80}")
        for i, chunk in enumerate(chunks):
            print(f"\n--- 切片 #{i+1} ---")
            print(f"  元数据: {chunk.metadata}")
            content_preview = chunk.page_content[:max_content_len]
            if len(chunk.page_content) > max_content_len:
                content_preview += "..."
            print(f"  长度: {len(chunk.page_content)} 字符")
            print(f"  内容: {content_preview}")
        print(f"\n{'='*80}")
        print(f"输出完毕，共 {len(chunks)} 个切片")


if __name__ == "__main__":
    processor = MarkdownProcessor()
    chunks = asyncio.run(processor.process(r"C:\Users\yufengli\OneDrive - Microsoft\Documents - IGS STCA\MPHP\pipeline_notes\Knowledge\DRIGuide"))
    processor.print_chunks(chunks)

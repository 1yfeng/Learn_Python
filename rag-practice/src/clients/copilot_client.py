from copilot import CopilotClient
import base64
import asyncio
import os
import re

class CopilotClientEnricher:
    def __init__(self, concurrrency_limit: int = 5):
        self.client = CopilotClient()
        self.semaphore = asyncio.Semaphore(concurrrency_limit)
        self.session = None

    async def __aenter__(self):
        await self.client.start()
        self.session = await self.client.create_session({"model":"gpt-4o"})
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close_session(self.session)
        await self.client.stop()


    async def get_describe_image(self, image_path: str) -> str:
        if not image_path or not os.path.exists(image_path):
            return "[missing image]"
        async with self.semaphore:
            try:
                with open(image_path, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode("utf-8")
                    response = await self.session.send_and_wait({
                        "prompt": "描述此架构图的核心组件，用于 RAG 检索",
                        "attachments": [{"type": "image", "data": image_base64}]
                    })
                    return response['content']
            except Exception as e:
                return f"[解析异常: {str(e)}]"
    
    async def process_single_file(self, file_path: str, enricher):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        img_pattern = r'!\[.*?\]\((.*?)\)'
        img_paths = re.findall(img_pattern, content)

        tasks = [enricher.get_describe_image(os.path.join(os.path.dirname(file_path), img_path)) for img_path in img_paths]
        descriptions = await asyncio.gather(*tasks)
        for img_path, desc in zip(img_paths, descriptions):
            content = content.replace(f'![]({img_path})', f'![{desc}]({img_path})')
        return content
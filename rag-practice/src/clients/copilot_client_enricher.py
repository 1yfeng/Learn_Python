from copilot import CopilotClient, PermissionHandler
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
        print("  [Enricher] 启动 CopilotClient...")
        await self.client.start()
        print("  [Enricher] CopilotClient 已启动，创建 session...")
        self.session = await self.client.create_session({
            "model": "gpt-4o",
            "on_permission_request": PermissionHandler.approve_all
        })
        print("  [Enricher] Session 创建成功")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("  [Enricher] 关闭 session...")
        await self.session.destroy()
        print("  [Enricher] 停止 CopilotClient...")
        await self.client.stop()
        print("  [Enricher] 已清理完毕")


    async def get_describe_image(self, image_path: str) -> str:
        if not image_path or not os.path.exists(image_path):
            print(f"  [Enricher] 图片不存在: {image_path}")
            return "[missing image]"
        async with self.semaphore:
            try:
                abs_path = os.path.abspath(image_path)
                print(f"  [Enricher] 解析图片: {os.path.basename(image_path)}")
                response = await self.session.send_and_wait({
                    "prompt": "描述此架构图的核心组件和流程，用简洁中文总结，用于 RAG 检索",
                    "attachments": [{"type": "file", "path": abs_path}]
                }, timeout=150)
                print(f"  [Enricher] 收到响应: {os.path.basename(image_path)}")
                return response['content']
            except Exception as e:
                print(f"  [Enricher] 解析异常: {os.path.basename(image_path)} - {e}")
                return f"[解析异常: {str(e)}]"
    
    async def process_single_file(self, file_path: str, enricher):
        file_name = os.path.basename(file_path)
        print(f"  [Enricher] 处理文件: {file_name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        img_pattern = r'!\[.*?\]\((.*?)\)'
        img_paths = re.findall(img_pattern, content)
        print(f"  [Enricher] {file_name}: 找到 {len(img_paths)} 张图片")

        if not img_paths:
            print(f"  [Enricher] {file_name}: 无图片，直接返回")
            return content

        tasks = [enricher.get_describe_image(os.path.join(os.path.dirname(file_path), img_path)) for img_path in img_paths]
        descriptions = await asyncio.gather(*tasks)
        for img_path, desc in zip(img_paths, descriptions):
            content = content.replace(f'![]({img_path})', f'![{desc}]({img_path})')
        print(f"  [Enricher] {file_name}: 图片描述替换完成")
        return content
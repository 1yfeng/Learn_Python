import os
import logging
from typing import Optional
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkerHTMLConverter:
    """
    基于 Marker AI 的高精度 HTML/PDF 转 Markdown 工具
    """
    def __init__(self, device: str = "cpu"):
        # device 可以是 "cuda" (NVIDIA GPU) 或 "cpu"
        logger.info(f"正在加载 Marker AI 模型 (运行设备: {device})...")
        try:
            self.artifact_dict = create_model_dict()
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def convert(self, input_path: str, output_dir: str = "data/output_md") -> Optional[str]:
        """
        将单个文件转换为 Markdown
        """
        if not os.path.exists(input_path):
            logger.error(f"输入文件不存在: {input_path}")
            return None

        os.makedirs(output_dir, exist_ok=True)

        try:
            logger.info(f"正在转换: {input_path}")

            config_parser = ConfigParser({"output_format": "markdown"})
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=self.artifact_dict,
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
            )
            rendered = converter(input_path)
            full_text, _, images = text_from_rendered(rendered)

            # 生成文件名
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.md")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            logger.info(f"转换成功，保存至: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"转换过程中出错: {e}")
            return None

    def convert_pdf(self, pdf_path: str, output_dir: str = "data/output_md", page_range: str = None) -> Optional[str]:
        """
        PDF → Markdown (使用 Marker AI)
        
        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            page_range: 页码范围，如 "0,5-10,20"
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF 文件不存在: {pdf_path}")
            return None

        os.makedirs(output_dir, exist_ok=True)

        try:
            logger.info(f"[PDF→MD] 正在转换: {pdf_path}")

            config = {"output_format": "markdown"}
            if page_range:
                config["page_range"] = page_range

            config_parser = ConfigParser(config)
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=self.artifact_dict,
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
            )
            rendered = converter(pdf_path)
            full_text, _, images = text_from_rendered(rendered)

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.md")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            # 保存提取的图片
            if images:
                img_dir = os.path.join(output_dir, f"{base_name}_images")
                os.makedirs(img_dir, exist_ok=True)
                for img_name, img_data in images.items():
                    img_path = os.path.join(img_dir, img_name)
                    with open(img_path, "wb") as img_f:
                        img_f.write(img_data)
                logger.info(f"[PDF→MD] 保存了 {len(images)} 张图片到: {img_dir}")

            logger.info(f"[PDF→MD] 转换成功，保存至: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[PDF→MD] 转换失败: {e}")
            return None

    def convert_folder(self, folder: str, output_dir: str = "data/output_md", ext: str = ".pdf") -> list[str]:
        """
        批量转换目录中的文件
        
        Args:
            folder: 输入目录
            output_dir: 输出目录
            ext: 文件扩展名过滤，如 ".pdf", ".html"
        """
        results = []
        files = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
        logger.info(f"[批量转换] 找到 {len(files)} 个 {ext} 文件")

        for i, file_name in enumerate(files, 1):
            file_path = os.path.join(folder, file_name)
            logger.info(f"[批量转换] ({i}/{len(files)}) {file_name}")
            if ext == ".pdf":
                result = self.convert_pdf(file_path, output_dir)
            else:
                result = self.convert(file_path, output_dir)
            if result:
                results.append(result)

        logger.info(f"[批量转换] 完成: {len(results)}/{len(files)} 成功")
        return results

if __name__ == "__main__":
    converter = MarkerHTMLConverter()  # 如果有 NVIDIA GPU，使用 "cuda" 加速
    input_file = r"C:\Users\yufengli\OneDrive - Microsoft\AI\agent_in_out_folder\input\About _ Bond_files.pdf"  # 替换为你的 PDF 文件路径
    output_file = r"C:\Users\yufengli\OneDrive - Microsoft\AI\agent_in_out_folder\output\About_Bond.md"  # 替换为你的 PDF 文件路径
    converter.convert_pdf(input_file, output_dir=os.path.dirname(output_file))
import subprocess
import os

def html_to_md_pandoc(html_path: str, output_dir: str = "data/output_md") -> str:
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(html_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.md")

    subprocess.run([
        "pandoc",
        html_path,
        "-f", "html",
        "-t", "markdown",           # 或 gfm (GitHub Flavored Markdown)
        "--wrap=none",               # 不自动折行
        "--extract-media=./media",   # 提取图片
        "-o", output_path
    ], check=True)
    return output_path


if __name__ == "__main__":
    input_file = r"C:\Users\yufengli\OneDrive - Microsoft\AI\agent_in_out_folder\input\Guidance_for_updating_Bond.html"  # 替换为你的 HTML 文件路径
    output_dir = r"C:\Users\yufengli\OneDrive - Microsoft\AI\agent_in_out_folder\output_pdf"  # 输出目录
    html_to_md_pandoc(input_file, output_dir=output_dir)
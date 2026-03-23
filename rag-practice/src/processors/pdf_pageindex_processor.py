import fitz
from models.pdf_model import PageNode
from pathlib import Path


class PDFPageIndexProcessor:
    def __init__(self, skip_headers_footers: bool = True):
        self.skip_headers_footers = skip_headers_footers

    def to_pages(self, file_path: str) -> list[PageNode]:
        path = Path(file_path)
        pages = []

        with fitz.open(str(path)) as doc:
            for page_num, page in enumerate(doc):
                rect = page.rect
                if self.skip_headers_footers:
                    clip = fitz.Rect(0, 50, rect.width, rect.height - 50)
                    text = page.get_text(clip = clip).strip()
                else:
                    text  = page.get_text().strip()

                if not text:
                    continue

                metadata = {
                    "source": path.name,
                    "page_number": page_num + 1,
                    "total_pages": len(doc),
                    "content_type": "text_page",
                    "file_path": str(path)
                }

                pages.append(PageNode(
                    page_label=f"page_{page_num + 1}",
                    content=text
                ))

        return pages
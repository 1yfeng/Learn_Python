from pydantic import BaseModel
from typing import List, Optional

class PageNode(BaseModel):
    page_label: str
    content: str
    summary: Optional[str] = None

class ProcessedDoc(BaseModel):
    title: str
    pages: List[PageNode]
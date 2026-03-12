from langchain_huggingface import HuggingFaceEmbeddings
import torch

class EmbeddingProcessor:
    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        self.model = HuggingFaceEmbeddings(
            model_name = model_name,
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )

    def embed_text(self, texts: list[str]):
        return self.model.embed_documents(texts)
    
    def get_dim(self):
        return len(self.model.embed_query("test"))
    


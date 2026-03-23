Plan
# Todo 
1. support Pageindex


project struct

```
rag-practice/
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
├── uv.lock
├── experiments/
│   ├── first_embedding_experiments.py
│   ├── query_vectors_experiment.md
│   └── similarity.py
└── src/
    ├── __init__.py
    ├── clients/
    │   ├── __init__.py
    │   ├── copilot_client_enricher.py
    │   └── milvus_client.py
    └── processors/
        ├── __init__.py
        ├── embedding_processor.py
        ├── markdown_processor.py
        ├── pdf_processor.py
        └── query.py

```




embedding  HuggingFaceEmbeddings   model=shibing624/text2vec-base-chinese
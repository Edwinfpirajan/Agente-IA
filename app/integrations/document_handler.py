from app.vectorstore.FAISS_vector import FAISSVectorHandler
from typing import Dict, Any, Optional


class DocumentHandler:
    def __init__(self):
        self.vector_handler = FAISSVectorHandler(index_path="vectorstore_clientes")  # tu carpeta FAISS

    def ingest_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        return self.vector_handler.ingest_file(file_path, metadata)

    def ingest_file_bytes(self, file_bytes: bytes, file_name: str, metadata: Optional[Dict[str, Any]] = None):
        return self.vector_handler.ingest_file_bytes(file_bytes, file_name, metadata)

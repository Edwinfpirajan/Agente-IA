import os
import tempfile
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader


def load_document_chunks(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)


class FAISSVectorHandler:
    def __init__(self, index_path: str = "faiss_index"):
        self.embeddings = OpenAIEmbeddings()
        self.index_path = index_path

    def ingest_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        chunks = load_document_chunks(file_path)

        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)

        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(self.index_path)
        return f"Ingested {len(chunks)} chunks from {file_path} into FAISS."

    def ingest_file_bytes(self, file_bytes: bytes, file_name: str, metadata: Optional[Dict[str, Any]] = None):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        try:
            return self.ingest_file(tmp_path, metadata)
        finally:
            os.remove(tmp_path)

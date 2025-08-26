from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_docx_chunks(docx_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    loader = Docx2txtLoader(docx_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return chunks

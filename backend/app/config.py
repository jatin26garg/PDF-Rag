import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GEMINI_API_KEY:str = os.getenv("GEMINI_API_KEY","")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "local")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "documents")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "qwen3:8b")

    
    CHROMA_PERSIST_DIR:str = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "my_documents")

    DENSE_VECTOR_SIZE: int = 1024
    SPARSE_VECTOR_SIZE:int = 250000  
    
    MAX_FILE_SIZE : int = int(os.getenv("MAX_FILE_SIZE", 10485760))
    ALLOWED_EXTENSIONS: List[str] = ['.pdf', '.docx', '.txt']

    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    def __init__(self):

        pass

settings = Settings() 
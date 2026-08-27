import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GEMINI_API_KEY:str = os.getenv("GEMINI_API_KEY","")
    CHROMA_PERSIST_DIR:str = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "my_documents")

    MAX_FILE_SIZE : int = int(os.getenv("MAX_FILE_SIZE", 10485760))
    ALLOWED_EXTENSIONS: List[str] = ['.pdf', '.docx', '.txt']

    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    def __init__(self):

        if not self.GEMINI_API_KEY:
            raise ValueError(
                "Gemmini api key is missing !"
            )

settings = Settings() 
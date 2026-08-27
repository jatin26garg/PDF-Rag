from fastapi import FastAPI, UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.config import settings
from app.models import QueryRequest
from app.services import rag_service

rag = rag_service

app = FastAPI(
    title="Document RAG API",
    description="upload que and ask que with rag",
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return{
        "status" : "healthy",
        "service" : "Document RAG API",
        "version" : "1.0.0"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_name = file.filename
        if not file_name:
            raise HTTPException(400,"no fileName provided")
        
        import os
        ext = os.path.splitext(file_name)[1].lower()
        if not ext in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"file type {ext} not allowed ")
        
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(400,f"file is too large")
        
        if file_size == 0:
            raise HTTPException(400,"file is empty")
        
        doc_id = rag.process_document(content,file_name)
        
        return{
            "status" : "success",
            "document_id" : doc_id,
            "file_name" : file_name,
            "message" : f"Successfully proccessed {file_name}"
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        print(f"upload error : {str(e)}")
        raise HTTPException(400, detail=str(e))
        
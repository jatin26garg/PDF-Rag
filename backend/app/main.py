from fastapi import FastAPI, UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.config import settings
from app.models import QueryRequest,QueryResponse,Documentinfo
from app.services.rag_service import RAGService

rag = RAGService()

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
        "embedding_model": "BAAI/bge-m3",
        "vector_db": "Qdrant",
        "embedding_dimension": 1024,
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
    
@app.post("/query",response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(400,"Question is empty")
        result = rag.query(question =request.question, top_k = request.top_k)
        print(f"the result is {result}")
        return result
    
    except Exception as e:
        print(f" Query Error : {str(e)}")
        raise HTTPException(500, detail=f"internal error {str(e)}")
    
@app.get("/documents", response_model=List[Documentinfo])
async def list_documents():
    return rag.get_documents

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id:str):
    try:
        success = rag.delete_document(doc_id)
        if not success:
            raise HTTPException(404, f" document {doc_id} not found")
        return {
            "status" : "success",
            "message" : f" document {doc_id} deleted successfully!"
        }
    except Exception as e:
        print(f" couldnt delete")
        raise HTTPException(500, detail=f" internal error : {str(e)}")
    
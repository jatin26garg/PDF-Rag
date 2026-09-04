

from typing import Dict, Any, List, Optional
from app.services.rag_service import RAGService

class RAGTool:
    
    def __init__(self):
        self.rag_service = RAGService()
    
    def search(self, query:str, top_k:int = 3)->Dict[str, Any]:
        
        try:
            result = self.rag_service.query(query, top_k)
            
            return {
                "success" : True,
                "query" : query,
                "results" : result.get("sources" , []),
                "answer" : result.get("answer", ""),
                "total_found" : len(result.get("sources", []))
            }
        except Exception as e:
            return {
                "success" : False,
                "error" : str(e),
                "query" : query,
            }
            
    def get_document_summary(self,document_id: str) -> Dict[str, Any]:
        
        chunks = self.rag_service.get_chunks_for_document(document_id)
        
        if not chunks:
            return {
                "success" : False,
                "error"  :"Document Not Found",
                "document_id" :document_id
            }
        full_text  ="\n\n".join([chunk["content"] for chunk in chunks])
        
        return {
            "success" : True,
            "document_id" : document_id,
            "chunk_count" : len(chunks),
            "preview" : full_text[:500] + "...",
            "full_text" : full_text,
        }
    
    
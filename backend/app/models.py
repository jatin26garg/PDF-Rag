from pydantic import BaseModel
from typing import List,Optional,Dict,Any
from datetime import datetime


class QueryRequest(BaseModel):
    question : str
    top_k :int = 3
    
class SourceInfo(BaseModel):
    source_index:int
    file_name:str
    rrf_score: float
    content_preview : str
    chunk_id:str
    
class QueryResponse(BaseModel):
    answer : str
    sources : List[SourceInfo] = []
    timestamp:datetime = datetime.now()

class Documentinfo(BaseModel):
    id: Optional[str] = None
    file_name: str
    chunk_count: Optional[int] = None
    uploaded_at: Optional[str] = None
    file_path: Optional[str] = None
    type: Optional[str] = None

class DocumentChunk(BaseModel):
    id:str
    content:str
    metadata:Dict[str,Any]
    embedding:Optional[List[float]] = None
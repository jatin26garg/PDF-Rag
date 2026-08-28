import os
import uuid
from typing import List, Dict,Any
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from qdrant_client import QdrantClient,models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import settings
from app.utils.chunking import chunk_document
from app.utils.file_handlers import extract_text_from_file

from FlagEmbedding import BGEM3FlagModel


class RAGService:
    
    def __init__(self):

        
        self.client = QdrantClient(
                            host= settings.QDRANT_HOST,
                            port= settings.QDRANT_PORT,
                            timeout=60.0,
                            )
        
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        

        self.embeddings = BGEM3FlagModel(
            settings.EMBEDDING_MODEL,
            use_fp16=False,
            device="cpu"
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model= "gemini-2.5-flash",
            google_api_key = settings.GEMINI_API_KEY,
            temperature = 0.3,
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant that answers questions based on the provided context.

            IMPORTANT RULES:
            1. Answer ONLY using the context provided below.
            2. If the answer is not in the context, say "I don't have information about that."
            3. DO NOT make up information.
            4. Cite which source you're using (e.g., "According to the policy document...").
            5. If multiple sources have relevant info, combine them into a cohesive answer.
            6. Be concise but complete.

            CONTEXT:
            {context}

            QUESTION:
            {question}

            ANSWER: 
            """)
        self._documents = {}
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        collections = self.client.get_collections().collections
        
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            
            print(f" creating collectiion: {self.collection_name}")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.DENSE_VECTOR_SIZE,
                    distance=models.Distance.COSINE
                ),
            )
            print(f"collection {self.collection_name} created !")
    
    def _get_embeddings(self, texts:List[str])->List[List[float]]:
        
        output = self.embeddings.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        
        dense_embeddings = output['dense_vecs']
        return dense_embeddings
    def _get_query_embeddings(self, query:str)->List[float]:
        
        output = self.embeddings.encode(
            query,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )
        return output['dense_vecs']
        
    def process_document(self, file_content : bytes , file_name:str)->str:
        
        print(f"extracting text from  :{file_name}")
        
        text = extract_text_from_file(file_content, file_name)
        
        if not text or len(text.strip()) == 0:
            raise ValueError(f"No text could be extarcted from {file_name}")
        
        print(f"  Extracted file has {len(text)} chars")
        
        
        print(f" creating chunks")
        
        chunks_with_metadata = chunk_document(
            text=text,
            metadata={
                "file_name":file_name,
                "uploadedAt" : datetime.now().isoformat(),
            },
            chunk_size= 500,
            chunk_overlap=50
        )
        
        print(f" created {len(chunks_with_metadata)} chunks")
        
        doc_id = str(uuid.uuid4())
        
        print(f" generating embeddings with BGE-M3")
        
        chunks_text = [chunk["content"] for chunk in chunks_with_metadata]
        
        dense_embeddings = self._get_embeddings(chunks_text)
        
        print(f" generated {len(dense_embeddings)} embeddings")
        
        points = []
        
        for i,chunk_data in enumerate(chunks_with_metadata):
            chunk_id = str(uuid.uuid4())
            
            point = models.PointStruct(
                id = chunk_id,
                vector=  dense_embeddings[i],
                payload={
                    "content" : chunk_data["content"],
                    "file_name": file_name,
                    "document_id":doc_id,
                    "chunk_index": i,
                    "total_chunks":len(chunks_with_metadata),
                    "uploaded_at":datetime.now().isoformat(),
                }
            )
            points.append(point)
        
        print(f" uploading {len(points)} points to Qdrant")
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        print(f" uploaded complete")
        
        self._documents[doc_id]={
            "id" : doc_id,
            "file_name": file_name,
            "chunk_count": len(chunks_with_metadata),
            "uploaded_at": datetime.now().isoformat(),
        }
        
        return doc_id
        

    def query(self, question:str, top_k: int = 3)->Dict[str,Any]:
        
        if not self._documents:
            return{
                "answer"  : ("no documents have been been uploaded .. please upload the document first"),
                "sources" : [],
            },
        
        print(f" processing the document")
        query_embedding = self._get_query_embeddings(question)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        ) 
        
        
        if not results.points:
            return {
                "answer": "I couldn't find any relevant information in your documents.",
                "sources": [],
            }
        
        
             
        context_parts  = []
        source_info  = []
        
        for i,point in enumerate(results.points,1):
            
            playload = point.payload or {}
            
            content = playload.get("content","")
            
            content = " ".join(content.split())
            
            context_parts.append(f"[Source{i}] {content}")
            
            source_info.append({
                "source_index" : i,
                "file_name" : playload.get("file_name","Unknown"),
                "score"  :round(point.score,4),
                "chunk_id":point.id, 
                "content_preview"  :content[:200] + "..." if len(content) > 200 else content,
            })
        context = "\n\n".join(context_parts)
        
        print(f" generating answer --")
        
        chain = (
            {
                "context"  : lambda x:x["context"],
                "question" : lambda x:x["question"],
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain.invoke({
            "context" : context,
            "question" :question,
        })
        
        return {
            "answer" : answer,
            "sources" : source_info,
        }
    
    def get_documents(self)->List[Dict[str,Any]]:
        return list(self._documents.values())
    
    def delete_document(self,doc_id :str)->bool:
        points_to_delete =[]
        scroll_limit = 100
        
        while True:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=doc_id),
                        )
                    ]
                ),
                limit=scroll_limit,
                with_payload=False,
                with_vectors=False,
            )
            points= scroll_result[0]
            if not points:
                break
            points_to_delete.extend([p.id for p in points])
            
            if len(points) < scroll_limit:
                break
        
        if not points_to_delete:
            if doc_id in self._documents:
                del self._documents[doc_id]
            return False
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=points_to_delete),
        )
        
        if doc_id in self._documents:
            del self._documents[doc_id]
        
        print(f" document deleted finally")
        
        return True
    
            
        
        
        
        
        
        
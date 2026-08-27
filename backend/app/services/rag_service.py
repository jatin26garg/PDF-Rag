import os
import uuid
from typing import List, Dict,Any
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.utils.chunking import chunk_document
from app.utils.file_handlers import extract_text_from_file


class RAGService:
    
    def __init__(self):

        self.chroma_client = chromadb.PersistentClient(
            path =settings.CHROMA_PERSIST_DIR
        )

        self.collection = self.chroma_client.get_or_create_collection(
             name = settings.CHROMA_COLLECTION_NAME,
             metadata={"hnsw:space": "cosine"}
        )

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model = "models/gemini-embedding-001",
            google_api_key = settings.GEMINI_API_KEY
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
        
        ids = []
        documents = []
        metadatas  = []
        
        for i,chunk_data in enumerate(chunks_with_metadata):
            chunk_id = f"{doc_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk_data["content"])
            metadatas.append({
                **chunk_data["metadata"],
                "document_id" : doc_id,
                "chunk_index" : i,
                "total_chunks":len(chunks_with_metadata),
            })
        
        print(f" generate embidings")
      

        print("DOCUMENTS:", documents)
        print("DOCUMENT TYPE:", type(documents))

        for doc in documents:
            print("EACH DOC TYPE:", type(doc))

        embeddings = self.embeddings.embed_documents(documents)
        print(f" generated {len(embeddings)} embidings")
        
        
        self.collection.add(
            ids = ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        self._documents[doc_id] = {
            "id": doc_id,
            "file_name": file_name,
            "chunk_count": len(chunks_with_metadata),
            "uploaded_at": datetime.now().isoformat(),
        }
        print(f"  Document processed successfully: {file_name} (ID: {doc_id})")
        
        return doc_id

    def query(self, question:str, top_k: int = 3)->Dict[str,Any]:
        
        if not self._documents:
            return{
                "answer"  : ("no documents have been been uploaded .. please upload the document first"),
                "sources" : [],
            },
        
        print(f" processing the document")
        query_embedding = self.embeddings.embed_query(question)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas","distances"]
        ) 
        chunks = []
        
        if results and results['documents']:
            for i in range (len(results['documents'][0])):
                similarity = 1 - (results['distances'][0][i]  / 2)
                chunks.append({
                    "content": results['documents'][0][i],
                    "metadata" : results['metadatas'][0][i],
                    "similarity" : similarity,
                })
        if not chunks:
            return{
                "answer" : (
                    "couldnt find relevant info about the query .  could you please elaborate your query"
                ),
                "sources" : []
            }
            
        context_parts  = []
        source_info  = []
        
        for i,chunk in enumerate(chunks,1):
            context_parts.append(f"[Source{i}] {chunk['content']}")
            source_info.append({
                "source_index" : i,
                "file_name" : chunk['metadata'].get('file_name', 'Unknown'),
                "similarity"  :round(chunk['similarity'], 3),
                "content_preview"  :chunk['content'][:200] + "...",
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
        results =self.collection.get(
            where={"document_id" : doc_id}
        )
        if results and results['ids']:
            self.collection.delete(ids= results['ids'])
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False
        
        
        
        
        
        
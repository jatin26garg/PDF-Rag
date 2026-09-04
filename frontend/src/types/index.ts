
export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    sources?: Source[];
    isStreaming?: boolean;
}

export interface Source {
    source_index: number;
    filename: string;
    score?: number;
    rrf_score?: number;
    dense_rank?: number;
    sparse_rank?: number;
    chunk_id: string;
    content_preview: string;
}

export interface Document {
    id: string;
    filename: string;
    chunk_count: number;
    uploaded_at: string;
}

export interface QueryRequest {
    question: string;
    top_k: number;
}

export interface QueryResponse {
    answer: string;
    sources: Source[];
}

export interface UploadResponse {
    status: string;
    document_id: string;
    filename: string;
    message: string;
    total_chunks: number;
}

export interface SystemStatus {
    status: string;
    service: string;
    version: string;
    chat_model: string;
    embedding_model: string;
    vector_db: string;
    total_chunks: number;
    documents: number;
}
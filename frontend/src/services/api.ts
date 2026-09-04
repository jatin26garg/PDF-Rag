// ===================================================
// API SERVICE - Using Native Fetch (No Axios)
// ===================================================

import {
    QueryResponse,
    UploadResponse,
    Document,
    SystemStatus,
    QueryRequest,
} from '@/src/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ===================================================
// FETCH WRAPPER WITH ERROR HANDLING
// ===================================================

async function fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}

// ===================================================
// HEALTH CHECK
// ===================================================

export const checkHealth = async (): Promise<SystemStatus> => {
    return fetchAPI<SystemStatus>('/');
};

// ===================================================
// DOCUMENT MANAGEMENT
// ===================================================

export const uploadDocument = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${API_BASE_URL}/upload`;
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }

    return response.json();
};

export const getDocuments = async (): Promise<Document[]> => {
    return fetchAPI<Document[]>('/documents');
};

export const deleteDocument = async (documentId: string): Promise<void> => {
    const url = `${API_BASE_URL}/documents/${documentId}`;
    const response = await fetch(url, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Delete failed: ${response.status}`);
    }
};

// ===================================================
// QUERY
// ===================================================

export const queryRAG = async (request: QueryRequest): Promise<QueryResponse> => {
    return fetchAPI<QueryResponse>('/query', {
        method: 'POST',
        body: JSON.stringify(request),
    });
};

// ===================================================
// STREAMING QUERY (Using Fetch + ReadableStream)
// ===================================================

export const queryRAGStream = async (
    request: QueryRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
) => {
    try {
        const url = `${API_BASE_URL}/query`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
            throw new Error('No reader available');
        }

        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        onComplete();
                        return;
                    }
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.answer) {
                            onChunk(parsed.answer);
                        }
                    } catch (e) {
                        // If not JSON, treat as plain text
                        onChunk(data);
                    }
                }
            }
        }
        onComplete();
    } catch (error) {
        onError(error as Error);
    }
};
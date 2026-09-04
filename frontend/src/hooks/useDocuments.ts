// ===================================================
// USE DOCUMENTS HOOK
// ===================================================

import { useState, useCallback, useEffect } from 'react';
import { Document, UploadResponse } from '@/src/types';
import { ragService } from '@/src/services/ragService';

export function useDocuments() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [uploadProgress, setUploadProgress] = useState<number>(0);

    const loadDocuments = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const docs = await ragService.list();
            setDocuments(docs);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load documents');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const uploadDocument = useCallback(async (file: File): Promise<UploadResponse | null> => {
        setUploadProgress(0);
        setError(null);
        
        // Simulate progress (since fetch doesn't support upload progress easily)
        const progressInterval = setInterval(() => {
            setUploadProgress(prev => Math.min(prev + 10, 90));
        }, 300);
        
        try {
            const result = await ragService.upload(file);
            clearInterval(progressInterval);
            setUploadProgress(100);
            await loadDocuments(); // Refresh list
            return result;
        } catch (err) {
            clearInterval(progressInterval);
            setError(err instanceof Error ? err.message : 'Upload failed');
            return null;
        } finally {
            setTimeout(() => setUploadProgress(0), 1000);
        }
    }, [loadDocuments]);

    const deleteDocument = useCallback(async (documentId: string) => {
        setError(null);
        try {
            await ragService.delete(documentId);
            await loadDocuments(); // Refresh list
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Delete failed');
        }
    }, [loadDocuments]);

    // Load documents on mount
    useEffect(() => {
        loadDocuments();
    }, [loadDocuments]);

    return {
        documents,
        isLoading,
        error,
        uploadProgress,
        uploadDocument,
        deleteDocument,
        refreshDocuments: loadDocuments,
    };
}
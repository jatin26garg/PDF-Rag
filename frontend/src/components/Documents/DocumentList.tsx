'use client';

import { DocumentCard } from './DocumentCard';
import { Document } from '@/src/types';
import { FolderOpen, Loader2, FileText, Plus } from 'lucide-react';

interface DocumentListProps {
    documents: Document[];
    isLoading: boolean;
    onDelete: (id: string) => void;
}

export function DocumentList({ documents, isLoading, onDelete }: DocumentListProps) {
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading documents...</p>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="text-center py-12 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg">
                <FolderOpen className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400 font-medium">No documents uploaded yet</p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                    Upload a PDF, DOCX, or TXT file to get started
                </p>
                <div className="mt-4 flex justify-center gap-2 text-xs text-gray-400 dark:text-gray-500">
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">📄 PDF</span>
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">📝 DOCX</span>
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">📃 TXT</span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {/* Header with count */}
            <div className="flex items-center justify-between px-1">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    {documents.length} document{documents.length !== 1 ? 's' : ''} uploaded
                </p>
                <span className="text-xs text-gray-400 dark:text-gray-500">
                    {documents.reduce((acc, doc) => acc + doc.chunk_count, 0)} total chunks
                </span>
            </div>

            {/* Document Cards */}
            <div className="space-y-2">
                {documents.map((document) => (
                    <DocumentCard
                        key={document.id}
                        document={document}
                        onDelete={onDelete}
                    />
                ))}
            </div>

            {/* Footer */}
            <div className="pt-2 text-xs text-gray-400 dark:text-gray-500 text-center border-t border-gray-100 dark:border-gray-800">
                Documents are stored locally and never leave your infrastructure
            </div>
        </div>
    );
}
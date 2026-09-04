'use client';

import { FolderOpen, Trash2, FileText, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

// Define the Document type locally or import from your types file
interface Document {
    id: string;
    filename: string;
    chunk_count: number;
    uploaded_at: string;
}

interface DocumentCardProps {
    document: Document;
    onDelete: (id: string) => void;
}

export function DocumentCard({ document, onDelete }: DocumentCardProps) {
    const getFileIcon = (filename: string) => {
        const ext = filename.split('.').pop()?.toLowerCase();
        switch (ext) {
            case 'pdf': return '📄';
            case 'docx': return '📝';
            case 'txt': return '📃';
            default: return '📎';
        }
    };

    const getFileType = (filename: string) => {
        const ext = filename.split('.').pop()?.toUpperCase() || 'FILE';
        return ext;
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                    <div className="text-2xl">
                        {getFileIcon(document.filename)}
                    </div>
                    <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                            {document.filename}
                        </h4>
                        <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                <FileText className="w-3 h-3" />
                                {getFileType(document.filename)}
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                <FolderOpen className="w-3 h-3" />
                                {document.chunk_count} chunks
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {formatDistanceToNow(new Date(document.uploaded_at), { addSuffix: true })}
                            </span>
                        </div>
                    </div>
                </div>
                <button
                    onClick={() => onDelete(document.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete document"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
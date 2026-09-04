'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface DocumentUploadProps {
    onUpload: (file: File) => Promise<void>;
    isLoading: boolean;
    progress?: number;
}

export function DocumentUpload({ onUpload, isLoading, progress = 0 }: DocumentUploadProps) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFile = async (file: File) => {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!allowedTypes.includes(file.type)) {
            setErrorMessage('Please upload PDF, DOCX, or TXT files only.');
            setUploadStatus('error');
            return;
        }

        if (file.size > maxSize) {
            setErrorMessage('File size exceeds 10MB limit.');
            setUploadStatus('error');
            return;
        }

        setSelectedFile(file);
        setUploadStatus('uploading');
        setErrorMessage(null);

        try {
            await onUpload(file);
            setUploadStatus('success');
            setSelectedFile(null);
        } catch (err) {
            setErrorMessage(err instanceof Error ? err.message : 'Upload failed');
            setUploadStatus('error');
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragActive(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
    };

    return (
        <div className="space-y-3">
            {/* Drag and Drop Area */}
            <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                } ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
                onDragEnter={() => setDragActive(true)}
                onDragLeave={() => setDragActive(false)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleChange}
                    className="hidden"
                    disabled={isLoading}
                />

                <div className="flex flex-col items-center gap-3">
                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                        <Upload className="w-8 h-8 text-blue-500" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Drag & drop your document here
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Supports PDF, DOCX, TXT (max 10MB)
                        </p>
                    </div>
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        disabled={isLoading}
                    >
                        Browse Files
                    </button>
                </div>
            </div>

            {/* Upload Progress */}
            {uploadStatus === 'uploading' && (
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                            Uploading {selectedFile?.name}...
                        </span>
                    </div>
                    <div className="mt-2 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Success */}
            {uploadStatus === 'success' && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-sm text-green-700 dark:text-green-300">
                        Upload successful!
                    </span>
                </div>
            )}

            {/* Error */}
            {uploadStatus === 'error' && errorMessage && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <span className="text-sm text-red-700 dark:text-red-300">
                        {errorMessage}
                    </span>
                    <button
                        onClick={() => setUploadStatus('idle')}
                        className="ml-auto text-red-500 hover:text-red-700"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}
        </div>
    );
}
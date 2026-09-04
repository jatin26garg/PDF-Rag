'use client';

import { useState } from 'react';
import { ChatContainer } from '@/src/components/Chat/ChatContainer';
import { DocumentUpload } from '@/src/components/Documents/DocumentUpload';
import { DocumentList } from '@/src/components/Documents/DocumentList';
import { useDocuments } from '@/src/hooks/useDocuments';
import { Menu, X, Database, MessageSquare, Upload, FileText } from 'lucide-react';

export default function Home() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');
    const { documents, isLoading, uploadProgress, uploadDocument, deleteDocument } = useDocuments();

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
            {/* ============================================
                SIDEBAR
            ============================================ */}
            <aside className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-hidden flex-shrink-0`}>
                <div className="p-4 h-full flex flex-col">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <h1 className="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                            <Database className="w-5 h-5 text-blue-500" />
                            DocAI
                        </h1>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="lg:hidden text-gray-500 hover:text-gray-700"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="space-y-2 mb-6">
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                                activeTab === 'chat'
                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                            }`}
                        >
                            <MessageSquare className="w-4 h-4" />
                            Chat
                        </button>
                        <button
                            onClick={() => setActiveTab('documents')}
                            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                                activeTab === 'documents'
                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                            }`}
                        >
                            <FileText className="w-4 h-4" />
                            Documents
                            <span className="ml-auto text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                                {documents.length}
                            </span>
                        </button>
                    </nav>

                    {/* Content based on active tab */}
                    <div className="flex-1 overflow-y-auto">
                        {activeTab === 'documents' && (
                            <div className="space-y-4">
                                <DocumentUpload
                                    onUpload={uploadDocument}
                                    isLoading={isLoading}
                                    progress={uploadProgress}
                                />
                                <DocumentList
                                    documents={documents}
                                    isLoading={isLoading}
                                    onDelete={deleteDocument}
                                />
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
                            v1.0.0 • Powered by Qwen3-8B + BGE-M3
                        </p>
                    </div>
                </div>
            </aside>

            {/* ============================================
                MAIN CONTENT
            ============================================ */}
            <main className="flex-1 flex flex-col min-w-0">
                {/* Mobile Header */}
                <header className="lg:hidden flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                    >
                        <Menu className="w-5 h-5" />
                    </button>
                    <h1 className="font-semibold text-gray-800 dark:text-white">DocAI</h1>
                    <div className="w-8" /> {/* Spacer */}
                </header>

                {/* Chat Interface */}
                {activeTab === 'chat' ? (
                    <ChatContainer />
                ) : (
                    <div className="flex-1 flex items-center justify-center p-8">
                        <div className="text-center text-gray-500 dark:text-gray-400">
                            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p className="text-lg font-medium">Documents Mode</p>
                            <p className="text-sm">Upload documents from the sidebar</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
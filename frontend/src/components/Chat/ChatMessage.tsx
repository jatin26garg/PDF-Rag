'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { User, Bot, Copy, Check, Link2 } from 'lucide-react';
import { useState } from 'react';
import type { CSSProperties } from 'react';
import { Source } from '@/src/types';

interface ChatMessageProps {
    message: {
        id: string;
        role: 'user' | 'assistant' | 'system';
        content: string;
        sources?: Source[];
        isStreaming?: boolean;
    };
}

export function ChatMessage({ message }: ChatMessageProps) {
    const [copied, setCopied] = useState(false);
    const isUser = message.role === 'user';
    const isSystem = message.role === 'system';

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (isSystem) {
        return (
            <div className="flex justify-center my-4">
                <div className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-sm px-4 py-2 rounded-full">
                    {message.content}
                </div>
            </div>
        );
    }

    return (
        <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'}`}>
                {isUser ? (
                    <User className="w-4 h-4 text-white" />
                ) : (
                    <Bot className="w-4 h-4 text-gray-700 dark:text-gray-300" />
                )}
            </div>

            {/* Message Content */}
            <div className={`max-w-[80%] ${isUser ? 'ml-auto' : ''}`}>
                <div className={`rounded-lg p-4 ${isUser ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'}`}>
                    {isUser ? (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                    ) : (
                        <>
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    code({ className, children, ...props }) {
                                        const match = /language-(\w+)/.exec(className || '');
                                        return match ? (
                                            <SyntaxHighlighter
                                                style={vscDarkPlus as any}
                                                language={match[1]}
                                                PreTag="div"
                                            >
                                                {String(children).replace(/\n$/, '')}
                                            </SyntaxHighlighter>
                                        ) : (
                                            <code className={className} {...props}>
                                                {children}
                                            </code>
                                        );
                                    },
                                    a({ href, children }) {
                                        return (
                                            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                                                {children}
                                            </a>
                                        );
                                    },
                                }}
                            >
                                {message.content}
                            </ReactMarkdown>

                            {/* Sources */}
                            {message.sources && message.sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1">
                                        <Link2 className="w-3 h-3" />
                                        Sources:
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {message.sources.map((source, idx) => (
                                            <span
                                                key={idx}
                                                className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded"
                                                title={`Score: ${source.rrf_score || source.score || 'N/A'}`}
                                            >
                                                {source.filename} #{source.source_index}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Copy Button */}
                            {message.content && !message.isStreaming && (
                                <button
                                    onClick={handleCopy}
                                    className="mt-2 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 flex items-center gap-1 transition-colors"
                                >
                                    {copied ? (
                                        <Check className="w-3 h-3" />
                                    ) : (
                                        <Copy className="w-3 h-3" />
                                    )}
                                    {copied ? 'Copied!' : 'Copy'}
                                </button>
                            )}
                        </>
                    )}
                </div>

                {/* Streaming Indicator */}
                {message.isStreaming && (
                    <div className="mt-1 text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
                        <span className="animate-pulse">●</span>
                        <span>Streaming...</span>
                    </div>
                )}
            </div>
        </div>
    );
}
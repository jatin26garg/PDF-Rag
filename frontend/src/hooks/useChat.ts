

import { useState, useCallback, useRef } from 'react';
import { Message, Source } from '@/src/types';
import { ragService } from '@/src/services/ragService';

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: '👋 Hello! I\'m your Document AI assistant. Upload a document and ask me anything about it!',
            timestamp: new Date(),
        },
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sources, setSources] = useState<Source[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim() || isLoading) return;

        // Add user message
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: content.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);
        scrollToBottom();

        // Create assistant message placeholder
        const assistantMessageId = (Date.now() + 1).toString();
        const assistantMessage: Message = {
            id: assistantMessageId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isStreaming: true,
        };

        setMessages(prev => [...prev, assistantMessage]);

        try {
            let accumulatedAnswer = '';
            
            await ragService.askStream(
                content,
                // On chunk
                (chunk) => {
                    accumulatedAnswer += chunk;
                    setMessages(prev =>
                        prev.map(msg =>
                            msg.id === assistantMessageId
                                ? { ...msg, content: accumulatedAnswer }
                                : msg
                        )
                    );
                    scrollToBottom();
                },
                // On complete
                () => {
                    setMessages(prev =>
                        prev.map(msg =>
                            msg.id === assistantMessageId
                                ? { ...msg, isStreaming: false }
                                : msg
                        )
                    );
                    setIsLoading(false);
                    scrollToBottom();
                },
                // On error
                (error) => {
                    setMessages(prev =>
                        prev.map(msg =>
                            msg.id === assistantMessageId
                                ? {
                                    ...msg,
                                    content: `❌ Error: ${error.message}`,
                                    isStreaming: false,
                                }
                                : msg
                        )
                    );
                    setError(error.message);
                    setIsLoading(false);
                    scrollToBottom();
                }
            );
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setIsLoading(false);
        }
    }, [isLoading, scrollToBottom]);

    const clearMessages = useCallback(() => {
        setMessages([
            {
                id: '1',
                role: 'assistant',
                content: '👋 Hello! I\'m your Document AI assistant. Upload a document and ask me anything about it!',
                timestamp: new Date(),
            },
        ]);
        setError(null);
    }, []);

    return {
        messages,
        isLoading,
        error,
        sendMessage,
        clearMessages,
        messagesEndRef,
    };
}
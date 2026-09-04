'use client';

import { useChat } from '@/src/hooks/useChat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export function ChatContainer() {
    const { messages, isLoading, sendMessage } = useChat();

    return (
        <div className="flex flex-col h-[calc(100vh-64px)]">
            <MessageList messages={messages} isLoading={isLoading} />
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>
    );
}
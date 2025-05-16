import { useCallback, useState } from 'react';
import { useChatStore } from '~/stores/chatStore';
import type { Message } from 'ai';

export const useChat = () => {
  const { messages, isLoading, setMessages, setIsLoading, addMessage } = useChatStore();
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsTyping(true);
    try {
      // Add user message
      const userMessage: Message = { 
        id: crypto.randomUUID(),
        role: 'user', 
        content 
      };
      addMessage(userMessage);

      // Send to API
      const formData = new FormData();
      formData.append('message', content);

      const response = await fetch('/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Add assistant message
      const assistantMessage: Message = { 
        id: crypto.randomUUID(),
        role: 'assistant', 
        content: data.response 
      };
      addMessage(assistantMessage);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    } finally {
      setIsTyping(false);
    }
  }, [addMessage]);

  return {
    messages,
    isLoading: isLoading || isTyping,
    sendMessage,
  };
}; 
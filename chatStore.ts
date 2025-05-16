import { atom } from 'nanostores';
import type { Message } from 'ai';

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
}

export const chatStore = atom<ChatState>({
  messages: [],
  isLoading: false
});

export const useChatStore = () => {
  return {
    messages: chatStore.get().messages,
    isLoading: chatStore.get().isLoading,
    setMessages: (messages: Message[]) => {
      chatStore.set({ ...chatStore.get(), messages });
    },
    setIsLoading: (isLoading: boolean) => {
      chatStore.set({ ...chatStore.get(), isLoading });
    },
    addMessage: (message: Message) => {
      const currentMessages = chatStore.get().messages;
      chatStore.set({ ...chatStore.get(), messages: [...currentMessages, message] });
    }
  };
}; 
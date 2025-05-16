import { json } from '@remix-run/cloudflare';
import { useActionData, useNavigation } from '@remix-run/react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { BaseChat } from '~/components/chat/BaseChat';
import { useChat } from '~/hooks/useChat';
import { useThemeStore } from '~/stores/themeStore';
import { useChatStore } from '~/stores/chatStore';

interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

export async function action({ request, context }: { request: Request; context: any }) {
  const formData = await request.formData();
  const message = formData.get('message') as string;

  if (!message) {
    return json({ error: 'Message is required' }, { status: 400 });
  }

  try {
    // Get API key from environment
    const apiKey = context.env.GOOGLE_API_KEY;
    if (!apiKey) {
      throw new Error('GOOGLE_API_KEY is not set in environment variables');
    }

    // Make direct API call to Gemini 2.0 Flash
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            role: 'user',
            parts: [{ text: message }]
          }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 1000,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json() as GeminiResponse;
    return json({ response: data.candidates[0].content.parts[0].text });
  } catch (error) {
    console.error('Error generating response:', error);
    return json(
      { error: 'Failed to generate response. Please try again.' },
      { status: 500 }
    );
  }
}

export default function Chat() {
  const { messages, sendMessage, isLoading } = useChat();
  const { theme } = useThemeStore();
  const { messages: chatMessages } = useChatStore();

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messageRef = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      node.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);
  const scrollRef = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      node.scrollTop = node.scrollHeight;
    }
  }, []);
  const [input, setInput] = useState('');
  const [chatStarted, setChatStarted] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (!chatStarted) {
      setChatStarted(true);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    try {
      await sendMessage(input);
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <BaseChat
      textareaRef={textareaRef}
      messageRef={messageRef}
      scrollRef={scrollRef}
      showChat={true}
      chatStarted={chatStarted}
      isStreaming={isLoading}
      messages={messages}
      input={input}
      handleInputChange={handleInputChange}
      sendMessage={handleSendMessage}
    />
  );
} 
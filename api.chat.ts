import { json } from '@remix-run/cloudflare';
import type { ActionFunctionArgs } from '@remix-run/cloudflare';
import { streamText } from '~/lib/.server/llm/stream-text';
import type { Message } from 'ai';

interface ChatRequestBody {
  message: string;
  model?: string;
}

export async function action({ request, context }: ActionFunctionArgs) {
  // Parse JSON body instead of form data
  const body = await request.json() as ChatRequestBody;
  const message = body.message;
  const model = body.model;

  if (!message) {
    return json({ error: 'Message is required' }, { status: 400 });
  }

  try {
    const messages: Message[] = [
      { 
        id: crypto.randomUUID(),
        role: 'user', 
        content: message 
      }
    ];

    const result = await streamText({
      messages,
      temperature: 0.7,
      maxTokens: 1000
    });

    return json({ response: result });
  } catch (error) {
    console.error('Error generating response:', error);
    return json(
      { error: 'Failed to generate response. Please try again.' },
      { status: 500 }
    );
  }
}

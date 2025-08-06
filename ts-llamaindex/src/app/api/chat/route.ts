import { NextRequest } from 'next/server';
import { createDataStreamResponse, LlamaIndexAdapter, Message, ToolExecutionError } from 'ai';
// import { agentStreamEvent, agent } from '@llamaindex/workflow';
import { openai, OpenAIAgent, OpenAI } from '@llamaindex/openai';
import { ChatMessage, Settings } from 'llamaindex';
import { setAIContext } from '@auth0/ai-llamaindex';
import { withInterruptions } from '@auth0/ai-llamaindex/interrupts';
import { errorSerializer } from '@auth0/ai-vercel/interrupts';

import { serpApiTool } from '@/lib/tools/serpapi';
import { getUserInfoTool } from '@/lib/tools/user-info';
import { gmailDraftTool, gmailSearchTool } from '@/lib/tools/gmail';
import { checkUsersCalendarTool } from '@/lib/tools/google-calender';
import { shopOnlineTool } from '@/lib/tools/shop-online';
import { getContextDocumentsTool } from '@/lib/tools/context-docs';

const AGENT_SYSTEM_TEMPLATE = `You are a personal assistant named Assistant0. You are a helpful assistant that can answer questions and help with tasks. You have access to a set of tools, use the tools as needed to answer the user's question. Render the email body as a markdown block, do not wrap it in code blocks.`;

// Settings.llm = new OpenAI({ model: 'gpt-4o-mini', temperature: 0 });

/**
 * This handler initializes and calls an tool calling agent.
 */
export async function POST(req: NextRequest) {
  const { id, messages }: { id: string; messages: Message[] } = await req.json();

  const sanitizedMessages = sanitizeMessages(messages);

  setAIContext({ threadID: id });

  const tools = [
    serpApiTool,
    // getUserInfoTool,
    // gmailSearchTool,
    // gmailDraftTool,
    // checkUsersCalendarTool,
    // shopOnlineTool,
    // getContextDocumentsTool,
  ];

  //   const assistant = agent({
  //     llm: openai({ model: 'gpt-4o-mini' }),
  //     systemPrompt: AGENT_SYSTEM_TEMPLATE,
  //     tools,
  //     // chatHistory: sanitizedMessages as ChatMessage[],
  //     verbose: true,
  //   });

  const assistant = new OpenAIAgent({
    llm: openai({ model: 'gpt-4o-mini' }),
    systemPrompt: AGENT_SYSTEM_TEMPLATE,
    tools,
    chatHistory: sanitizedMessages as ChatMessage[],
    verbose: true,
  });

  //   const stream = new ReadableStream({
  //     async start(controller) {
  //       try {
  //         const context = assistant.runStream(sanitizedMessages[sanitizedMessages.length - 1].content);

  //         for await (const event of context) {
  //           if (agentStreamEvent.include(event)) {
  //             controller.enqueue(new TextEncoder().encode(event.data.delta));
  //           }
  //         }

  //         controller.close();
  //       } catch (error) {
  //         controller.error(error);
  //       }
  //     },
  //   });

  //   return new Response(stream, {
  //     headers: {
  //       'Content-Type': 'text/plain',
  //       'Transfer-Encoding': 'chunked',
  //     },
  //   });

  return createDataStreamResponse({
    execute: withInterruptions(
      async (dataStream) => {
        const stream = await assistant.chat({
          message: sanitizedMessages[sanitizedMessages.length - 1].content,
          stream: true,
        });

        LlamaIndexAdapter.mergeIntoDataStream(stream as any, { dataStream });
      },
      {
        messages: sanitizedMessages,
        errorType: ToolExecutionError,
      },
    ),
    onError: errorSerializer((err: any) => {
      console.log(err);
      return `An error occurred! ${err.message}`;
    }),
  });
}

// Vercel AI tends to get stuck when there are incomplete tool calls in messages
const sanitizeMessages = (messages: Message[]) => {
  return messages.filter(
    (message) =>
      !(
        message.role === 'assistant' &&
        message.toolInvocations &&
        message.toolInvocations.length > 0 &&
        message.content === ''
      ),
  );
};

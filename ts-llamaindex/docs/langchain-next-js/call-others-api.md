# Docs > Get Started > Call Others' APIs on User's Behalf

---

# Call Other's APIs on User's Behalf

Use Auth0 SDKs to fetch access tokens for social and enterprise identity providers from Auth0's [Token Vault](https://auth0.com/docs/secure/tokens/token-vault). Using these access tokens, AI agents integrated with the application can call third-party APIs to perform tasks on the user's behalf.

By the end of this quickstart, you should have an application integrated with Auth0 and [LangChain](https://js.langchain.com/) that can:

1. Retrieve access tokens for a Google social connection.
2. Integrate with an AI agent to call Gmail APIs.

## Prerequisites

Before getting started, make sure you have completed the following steps:

- Create an Auth0 Account and a Dev Tenant
- Create and configure a [Regular Web Application](https://auth0.com/docs/get-started/applications) to use with this quickstart.
- Complete the [User Authentication quickstart](https://auth0.com/ai/docs/user-authentication) or download a starter template.
- Configure Google Social Connection (see [Google Sign-in and Authorization](https://auth0.com/ai/docs/google-sign-in-and-auth)) and select the Gmail scope.
- Set up an [OpenAI account and API key](https://platform.openai.com/docs/libraries#create-and-export-an-api-key)

## Prepare Next.js app

**Recommended**: To use a starter template, clone the [Auth0 AI samples](https://github.com/auth0-samples/auth0-ai-samples) repository:

```bash
git clone https://github.com/auth0-samples/auth0-ai-samples.git
cd auth0-ai-samples/authenticate-users/langchain-next-js
```

## Install dependencies

In the root directory of your project, install the following dependencies:

- `@auth0/ai-langchain`: [Auth0 AI SDK for LangChain](https://github.com/auth0-lab/auth0-ai-js/tree/main/packages/ai-langchain) built for GenAI applications powered by LangChain.
- `@langchain/langgraph`: For building stateful, multi-actor applications with LLMs.
- `langchain`: The LangChain library.
- `@langchain/core`: LangChain core libraries.
- `@langchain/openai`: OpenAI provider for LangChain.
- `@langchain/community`: LangChain community integrations.
- `langgraph-nextjs-api-passthrough`: API passthrough for LangGraph.

```bash
npm install @auth0/ai-langchain@3 @langchain/community@0.3 @langchain/core@0.3 @langchain/langgraph@0.3 @langchain/openai@0.6 langchain@0.3 langgraph-nextjs-api-passthrough@0.1
```

## Get access tokens for others APIs

Use the [Auth0 AI SDK for LangChain](https://github.com/auth0-lab/auth0-ai-js/tree/main/packages/ai-langchain) to get access tokens for third-party APIs.

### Set up Token Vault for Google Social Connection

Setup Auth0 AI SDK for Google Social Connection. This will allow you to get access tokens for Google Social Connection using [Token Vault](https://auth0.com/docs/secure/tokens/token-vault).

- `connection`: pass in the name of the connection you want the user to sign up for/log into.
- `scopes`: pass in the scopes for the service you want to get access to.

Create a file at `src/lib/auth0-ai.ts` and instantiate a new Auth0 AI SDK client:

```tsx file=src/lib/auth0-ai.ts
import { Auth0AI, getAccessTokenForConnection } from '@auth0/ai-langchain';

// Get the access token for a connection via Auth0
export const getAccessToken = async () => getAccessTokenForConnection();

const auth0AI = new Auth0AI();

// Connection for Google services
export const withGoogleConnection = auth0AI.withTokenForConnection({
  connection: 'google-oauth2',
  scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
});
```

### Pass credentials to the tools

Update the `/src/lib/auth0.ts` file with the following code.

```tsx file=src/lib/auth0.ts
//...
//... existing code
// Get the refresh token from Auth0 session
export const getRefreshToken = async () => {
  const session = await auth0.getSession();
  return session?.tokenSet?.refreshToken;
};
```

Update the `/src/app/api/chat/[..._path]/route.ts` file with the following code. The `refreshToken` will be passed to your LangGraph agent so we can use it from the Auth0 AI SDK to get Google access tokens from the server.

```ts file=src/app/api/chat/[..._path]/route.ts
import { initApiPassthrough } from 'langgraph-nextjs-api-passthrough';

import { getRefreshToken } from '@/lib/auth0';

export const { GET, POST, PUT, PATCH, DELETE, OPTIONS, runtime } = initApiPassthrough({
  apiUrl: process.env.LANGGRAPH_API_URL,
  baseRoute: 'chat/',
  bodyParameters: async (req, body) => {
    if (req.nextUrl.pathname.endsWith('/runs/stream') && req.method === 'POST') {
      return {
        ...body,
        config: {
          configurable: {
            _credentials: {
              refreshToken: await getRefreshToken(),
            },
          },
        },
      };
    }

    return body;
  },
});
```

## Use access token to call APIs from a tool

Once the user is authenticated, you can fetch an access token from the Token Vault using the Auth0 AI SDK. In this example, we fetch an access token for a Google social connection. Once you've obtained the access token for a connection, you can use it with an AI agent to fetch data during a tool call and provide contextual data in its response.

In this example, we will use the `GmailSearch` from the `@langchain/community` tools. This tool will use the access token provided by Token Vault to query for emails.

```ts file=src/lib/agent.ts
//...
import { GmailSearch } from '@langchain/community/tools/gmail';

import { getAccessToken, withGoogleConnection } from './auth0-ai';

//... existing code

// Provide the access token to the Gmail tools
const gmailParams = {
  credentials: {
    accessToken: getAccessToken,
  },
};

const tools = [
  //... existing tools
  withGoogleConnection(new GmailSearch(gmailParams)),
];

//... existing code
```

You need to [obtain an API Key from OpenAI](https://platform.openai.com/api-keys) or another provider to use an LLM. Add the API key to your environment variables:

```env
# ...
# You can use any provider of your choice supported by Vercel AI
OPENAI_API_KEY="YOUR_API_KEY"
```

## Add step up authorization

Now when you try to use the tool, you will need to authorize additional scopes for Google that you have configured. We can achieve this using step up authorization.

Install Auth0 AI Components for Next.js to get the required UI components.

```bash
npx @auth0/ai-components add FederatedConnections
```

Add a new file, `src/components/auth0-ai/FederatedConnections/FederatedConnectionInterruptHandler.tsx` and add the following code:

```tsx file=src/components/auth0-ai/FederatedConnections/FederatedConnectionInterruptHandler.tsx
import { FederatedConnectionInterrupt } from '@auth0/ai/interrupts';
import type { Interrupt } from '@langchain/langgraph-sdk';

import { EnsureAPIAccess } from '@/components/auth0-ai/FederatedConnections';

interface FederatedConnectionInterruptHandlerProps {
  interrupt: Interrupt | undefined | null;
  onFinish: () => void;
}

export function FederatedConnectionInterruptHandler({ interrupt, onFinish }: FederatedConnectionInterruptHandlerProps) {
  if (!interrupt || !FederatedConnectionInterrupt.isInterrupt(interrupt.value)) {
    return null;
  }

  return (
    <div key={interrupt.ns?.join('')} className="whitespace-pre-wrap">
      <EnsureAPIAccess
        mode="popup"
        interrupt={interrupt.value}
        onFinish={onFinish}
        connectWidget={{
          title: 'Authorization Required.',
          description: interrupt.value.message,
          action: { label: 'Authorize' },
        }}
      />
    </div>
  );
}
```

Now update the `src/components/chat-window.tsx` file to include the `FederatedConnectionInterruptHandler` component:

```tsx file=src/components/chat-window.tsx
//...
import { FederatedConnectionInterruptHandler } from '@/components/auth0-ai/FederatedConnections/FederatedConnectionInterruptHandler';

//... existing code
export function ChatWindow(props: {
  //... existing code
}) {
  //... existing code
  return (
    <StickToBottom>
      <StickyToBottomContent
        className="absolute inset-0"
        contentClassName="py-8 px-2"
        content={
          chat.messages.length === 0 ? (
            <div>{props.emptyStateComponent}</div>
          ) : (
            <>
              <ChatMessages
                aiEmoji={props.emoji}
                messages={chat.messages}
                emptyStateComponent={props.emptyStateComponent}
              />
              <div className="flex flex-col max-w-[768px] mx-auto pb-12 w-full">
                <FederatedConnectionInterruptHandler interrupt={chat.interrupt} onFinish={() => chat.submit(null)} />
              </div>
            </>
          )
        }
        {/* ... existing code */}
      ></StickyToBottomContent>
    </StickToBottom>
  );
}
```

## Test your application

Start the application with `npm run all:dev`. Then, navigate to `http://localhost:3000`. If you have already logged in, make sure to log out and log in again using Google. Then, ask your AI Agent fetch emails from your Gmail account!

That's it! You successfully integrated external tool-calling into your project.

Explore [the example app on GitHub](https://github.com/auth0-samples/auth0-ai-samples/tree/main/call-apis-on-users-behalf/others-api/langchain-next-js).

## Next steps

- Learn more about Client-initiated account linking
- Learn more about how Auth0's Token Vault
- [Call your APIs on user's behalf docs](https://auth0.com/ai/docs/call-your-apis-on-users-behalf).

---

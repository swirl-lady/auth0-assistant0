# Docs > Get Started > Asynchronous Authorization

---

# Asynchronous Authorization

Auth for GenAI enables AI agents to asynchronously authorize users using the [Client-Initiated Backchannel Authentication Flow (CIBA)](https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-initiated-backchannel-authentication-flow). AI agents can work in the background, only notifying the user when needed for critical actions.

When you add secure [human-in-the-loop approvals](https://sdk.vercel.ai/cookbook/next/human-in-the-loop) to your AI agent workflows, you can use Auth0 to request the user's permission to complete an authorization request. The AI agent can render [rich authorization data](https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-initiated-backchannel-authentication-flow/user-authorization-with-ciba) in the consent prompt so the user knows exactly what they're authorizing.

By the end of this quickstart, you should have an AI agent integrated with the [Auth0 AI SDK](https://github.com/auth0-lab/auth0-ai-js) that can request to buy products from an online shop on the user's behalf.

## Prerequisites

Before getting started, make sure you have completed the following steps:

- Create an Auth0 Account and a Dev Tenant
- Create and configure a [Regular Web Application](https://auth0.com/docs/get-started/applications) to use with this quickstart.
- [Enable Guardian Push](https://auth0.com/docs/secure/multi-factor-authentication/auth0-guardian) (Multi-factor authentication with Guardian Push Notifications) for your Auth0 tenant.
- [Enroll your user to use Auth0 Guardian](https://auth0.com/docs/mfa/auth0-guardian/user-enrollment)
- Complete the [User Authentication quickstart](https://auth0.com/ai/docs/user-authentication) or download a starter template.
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
- `langgraph-nextjs-api-passthrough`: API passthrough for LangGraph.

```bash
npm install @auth0/ai-langchain@3 @langchain/core@0.3 @langchain/langgraph@0.3 @langchain/openai@0.6 langchain@0.3 langgraph-nextjs-api-passthrough@0.1
```

## Setup Human in the Loop Approvals

Integrate the Auth0 AI SDK into your application to secure your async AI agent workflow. For quickstart we will use a blocking request flow. In real use cases, often an asynchronous flow is preferred.

### Configure the Auth0 AI SDK

To require asynchronous authorization for your tool, the tool needs to be wrapped with the Async authorizer, `withAsyncUserConfirmation()`. Let's create a helper function to wrap the tool with the Async authorizer.

Create a file at `src/lib/auth0-ai.ts` and instantiate a new Auth0 AI SDK client:

```tsx file=src/lib/auth0-ai.ts
import { Auth0AI } from '@auth0/ai-langchain';
import { AccessDeniedInterrupt } from '@auth0/ai/interrupts';

const auth0AI = new Auth0AI();

// CIBA flow for user confirmation
export const withAsyncAuthorization = auth0AI.withAsyncUserConfirmation({
  userID: async (_params, config) => {
    return config?.configurable?._credentials?.user?.sub;
  },
  bindingMessage: async ({ product, qty }) => `Do you want to buy ${qty} ${product}`,
  scopes: ['openid', 'product:buy'], // add any scopes you want to use with your API
  audience: process.env['AUDIENCE']!,

  /**
   * When this flag is set to `block`, the execution of the tool awaits
   * until the user approves or rejects the request.
   *
   * Given the asynchronous nature of the CIBA flow, this mode
   * is only useful during development.
   *
   * In practice, the process that is awaiting the user confirmation
   * could crash or timeout before the user approves the request.
   */
  onAuthorizationRequest: 'block',
  onUnauthorized: async (e: Error) => {
    if (e instanceof AccessDeniedInterrupt) {
      return 'The user has denied the request';
    }
    return e.message;
  },
});
```

This will intercept the tool call to initiate a CIBA request:

- The CIBA request includes the user ID that will approve the request.
- Auth0 sends the user a mobile push notification. The AI agent polls the `/token` endpoint for a user response.
- The mobile application retrieves the `bindingMessage` containing the consent details, in this case, the details of the product to purchase.
- The user responds to the request:
  - If the request is approved, the tool execution will continue.
  - If the request is rejected, the tool execution will not continue.

![CIBA flow](https://user-images.githubusercontent.com/10214025/233876208-c8d5d0e2-e7c4-4f0a-a1c1-b0d1d4d2f1f9.png)

### Pass credentials to the tools

Next, add the following code to `src/lib/auth0.ts`:

```tsx file=src/lib/auth0.ts
//... existing code
export const getUser = async () => {
  const session = await auth0.getSession();
  return session?.user;
};
```

Update the `/src/app/api/chat/[..._path]/route.ts` file with the following code. The `user` will be passed to your LangGraph agent so we can use it from the Auth0 AI SDK to get current user.

```ts file=src/app/api/chat/[..._path]/route.ts
import { initApiPassthrough } from 'langgraph-nextjs-api-passthrough';

import { getUser } from '@/lib/auth0';

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
              user: await getUser(),
            },
          },
        },
      };
    }

    return body;
  },
});
```

### Create a tool to call your API

In this example, we use a tool that buys products on the user's behalf. When the user approves the transaction, the Auth0 AI SDK retrieves an access token to call the shop's API. Upon completing the CIBA flow, the AI agent responds with a message confirming the purchase. The Auth0 AI SDK returns an error response if the user denies the transaction.

Now, create a file `src/lib/tools/shop-online.ts` and add the following code:

```ts file=src/lib/tools/shop-online.ts
import { tool } from '@langchain/core/tools';
import { z } from 'zod';

import { getCIBACredentials } from '@auth0/ai-langchain';

export const shopOnlineTool = tool(
  async ({ product, qty, priceLimit }) => {
    console.log(`Ordering ${qty} ${product} with price limit ${priceLimit}`);

    const apiUrl = process.env['SHOP_API_URL']!;

    if (!apiUrl) {
      // No API set, mock a response
      return `Ordered ${qty} ${product}`;
    }

    const headers = {
      'Content-Type': 'application/json',
      Authorization: '',
    };
    const body = {
      product,
      qty,
      priceLimit,
    };

    const credentials = getCIBACredentials();
    const accessToken = credentials?.accessToken;

    if (accessToken) {
      headers['Authorization'] = 'Bearer ' + accessToken;
    }

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body),
    });

    return response.statusText;
  },
  {
    name: 'shop_online',
    description: 'Tool to buy products online',
    schema: z.object({
      product: z.string(),
      qty: z.number(),
      priceLimit: z.number().optional(),
    }),
  },
);
```

## Update environment variables

You need to [obtain an API Key from OpenAI](https://platform.openai.com/api-keys) or another provider to use an LLM.

If you want to use an API, it must be [registered with Auth0](https://auth0.com/docs/get-started/apis) and have a valid audience.

Update the `.env.local` file with the following variables:

```env file=.env.local
# ... existing variables
# You can use any provider of your choice supported by Vercel AI
OPENAI_API_KEY="YOUR_API_KEY"

# API
SHOP_API_URL=<your-shop-api-url>
AUDIENCE=sample-shop-api
```

## Require async authorization for your tool

Call the tool from your AI app to make purchases. Update the `src/lib/agent.ts` file with the following code:

```ts file=src/lib/agent.ts
//...
import { withAsyncAuthorization } from './auth0-ai';
import { shopOnlineTool } from './tools/shop-online';

//... existing code

const tools = [
  //... existing tools
  withAsyncAuthorization(shopOnlineTool),
];

//... existing code
```

## Test the application

Start the application with `npm run all:dev`. Then, navigate to `http://localhost:3000`.

Now ask the AI agent to buy a product, for example, "Buy an XYZ phone". Now, look for a push notification from the [Auth0 Guardian app](https://auth0.com/docs/mfa/auth0-guardian/user-enrollment) or your custom app integrated with the [Auth0 Guardian SDK](https://auth0.com/docs/secure/multi-factor-authentication/auth0-guardian) on your mobile device. Once you approve the notification, you should see the tool being executed and a response from the Agent.

Explore the [example app on GitHub](https://github.com/auth0-samples/auth0-ai-samples/tree/main/async-authorization/langchain-next-js).

## Next steps

- Async Authorization docs
- Learn more about the [Client-Initiated Backchannel Authentication Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-initiated-backchannel-authentication-flow).
- Learn how to [Configure Rich Authorization Requests](https://auth0.com/docs/get-started/apis/configure-rich-authorization-requests).

---

# Docs > Get Started > Call Your APIs on User's Behalf

---

# Call Your APIs On User's Behalf

Let your AI agent call your APIs on behalf of the authenticated user using access tokens securely issued by Auth0. Your API can be any [API that you have configured in Auth0](https://auth0.com/docs/get-started/apis).

By the end of this quickstart, you should have an application integrated with Auth0 and the [Vercel AI SDK](https://sdk.vercel.ai/docs) that can:

- Get an Auth0 access token.
- Use the Auth0 access token to make a tool call to your API endpoint, in this case, Auth0's `/userinfo` endpoint.
- Return the data to the user via an AI agent.

## Prerequisites

Before getting started, make sure you have completed the following steps:

- Create an Auth0 Account and a Dev Tenant
- Create and configure a [Regular Web Application](https://auth0.com/docs/get-started/applications) to use with this quickstart.
- Complete the [User Authentication quickstart](https://auth0.com/ai/docs/user-authentication) or download a starter template.
- Set up an [OpenAI account and API key](https://platform.openai.com/docs/libraries#create-and-export-an-api-key)

## Prepare Next.js app

**Recommended**: To use a starter template, clone the [Auth0 AI samples](https://github.com/auth0-samples/auth0-ai-samples) repository:

```bash
git clone https://github.com/auth0-samples/auth0-ai-samples.git
cd auth0-ai-samples/authenticate-users/vercel-ai-next-js
```

## Install dependencies

In the root directory of your project, install the following dependencies:

- `ai`: Core [Vercel AI SDK](https://sdk.vercel.ai/docs) module that interacts with various AI model providers.
- `@ai-sdk/openai`: [OpenAI](https://sdk.vercel.ai/providers/ai-sdk-providers/openai) provider for the Vercel AI SDK.
- `@ai-sdk/react`: [React](https://react.dev/) UI components for the Vercel AI SDK.
- `zod`: TypeScript-first schema validation library.

```bash
npm install ai@4 @ai-sdk/openai@1 @ai-sdk/react@1 zod@3
```

## Define a tool to call your API

In this step, you'll create a Vercel AI tool to make the first-party API call. The tool fetches an access token to call the API.

In this example, after taking in an Auth0 access token during user login, the tool returns the user profile of the currently logged-in user by calling the [/userinfo](https://auth0.com/docs/api/authentication/user-profile/get-user-info) endpoint.

```ts file=src/lib/tools/user-info.ts
import { tool } from 'ai';
import { z } from 'zod';

import { auth0 } from '../auth0';

export const getUserInfoTool = tool({
  description: 'Get information about the current logged in user.',
  parameters: z.object({}),
  execute: async () => {
    const session = await auth0.getSession();
    if (!session) {
      return 'There is no user logged in.';
    }

    const response = await fetch(`https://${process.env.AUTH0_DOMAIN}/userinfo`, {
      headers: {
        Authorization: `Bearer ${session.tokenSet.accessToken}`,
      },
    });

    if (response.ok) {
      return { result: await response.json() };
    }

    return "I couldn't verify your identity";
  },
});
```

## Add the tool to the AI agent

The AI agent processes and runs the user's request through the AI pipeline, including the tool call. Vercel AI simplifies this task with the `streamText()` method. Update the `/src/app/api/chat/route.ts` file with the following code:

```ts file=src/app/api/chat/route.ts
//...
import { getUserInfoTool } from '@/lib/tools/user-info';

//... existing code

export async function POST(req: NextRequest) {
  const request = await req.json();
  const messages = sanitizeMessages(request.messages);

  const tools = {
    getUserInfoTool,
  };

  return createDataStreamResponse({
    execute: async (dataStream: DataStreamWriter) => {
      const result = streamText({
        model: openai('gpt-4o-mini'),
        system: AGENT_SYSTEM_TEMPLATE,
        messages,
        maxSteps: 5,
        tools,
      });

      result.mergeIntoDataStream(dataStream, {
        sendReasoning: true,
      });
    },
    onError: (err: any) => {
      console.log(err);
      return `An error occurred! ${err.message}`;
    },
  });
}
//... existing code
```

You need an API Key from Open AI or another provider to use an LLM. Add that API key to your `.env.local` file:

```env file=.env.local
# ...
# You can use any provider of your choice supported by Vercel AI
OPENAI_API_KEY="YOUR_API_KEY"
```

If you use another provider for your LLM, adjust the variable name in `.env.local` accordingly.

## Test your application

To test the application, run `npm run dev` and navigate to `http://localhost:3000` and interact with the AI agent. You can ask questions like `"who am I?"` to trigger the tool call and test whether it successfully retrieves information about the logged-in user.

```
User: who am I?
AI: It seems that there is no user currently logged in. If you need assistance with anything else, feel free to ask!

User: who am I?
AI: You are Deepu Sasidharan. Here are your details: - .........
```

That's it! You've successfully integrated first-party tool-calling into your project.

Explore [the example app on GitHub](https://github.com/auth0-samples/auth0-ai-samples/tree/main/call-apis-on-users-behalf/your-api/vercel-ai-next-js).

## Next steps

- To set up third-party tool calling, complete the
  [Call other's APIs on user's behalf](https://auth0.com/ai/docs/call-others-apis-on-users-behalf) quickstart.
- To explore the Auth0 Next.js SDK, see the
  [Github repo](https://github.com/auth0/nextjs-auth0).
- [Call your APIs on user's behalf docs](https://auth0.com/ai/docs/call-your-apis-on-users-behalf).

---

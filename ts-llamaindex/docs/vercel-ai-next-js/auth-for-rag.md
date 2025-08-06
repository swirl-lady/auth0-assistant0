# Docs > Get Started > Authorization for RAG

---

# Authorization for RAG

Auth for GenAI leverages [Auth0 FGA](https://auth0.com/fine-grained-authorization) to provide fine-grained authorization control for AI agents. As a result, when AI agents use Retrieval Augmented Generation (RAG) to provide sophisticated, relevant responses to user queries, they only have access to authorized data.

By the end of this quickstart, you should have a Next.js application that can:

1. Retrieve authorized data as context for a RAG pipeline using Vercel AI.
2. Use Auth0 FGA to determine if the user has authorization for the data.

## Prerequisites

Before getting started, make sure you:

- [Create an Auth0 FGA account](https://dashboard.fga.dev/)
- Complete the [User Authentication quickstart](https://auth0.com/ai/docs/user-authentication) or download a starter template.
- [Set up an OpenAI account and API key](https://platform.openai.com/)

## Prepare Next.js app

**Recommended**: To use a starter template, clone the [Auth0 AI samples](https://github.com/auth0-samples/auth0-ai-samples) repository:

```bash
git clone https://github.com/auth0-samples/auth0-ai-samples.git
cd auth0-ai-samples/authenticate-users/vercel-ai-next-js
```

## Install dependencies

In the root directory of your project, install the following dependencies:

- `@auth0/ai-vercel`: [Auth0 AI SDK for Vercel AI](https://github.com/auth0-lab/auth0-ai-js/tree/main/packages/ai-vercel) built for GenAI applications powered by the Vercel AI SDK.
- `ai`: Core [Vercel AI SDK](https://sdk.vercel.ai/docs) module that interacts with various AI model providers.
- `@ai-sdk/openai`: [OpenAI](https://sdk.vercel.ai/providers/ai-sdk-providers/openai) provider for the Vercel AI SDK.
- `@ai-sdk/react`: [React](https://react.dev/) UI components for the Vercel AI SDK.
- `zod`: TypeScript-first schema validation library.

```bash
npm install @auth0/ai-vercel@3 ai@4 @ai-sdk/openai@1 @ai-sdk/react@1 zod@3
```

## Set up an FGA Store

In the [Auth0 FGA dashboard](https://dashboard.fga.dev/):

1. Navigate to **Settings**. In the **Authorized Clients** section, click **+ Create Client**.
2. Give your client a name and mark all the client permissions that are required for your use case. For the quickstart you'll only need **Read and query**.
3. Click **Create**.

![FGA Client](/public/images/fga-client.png)

Once your client is created, you'll see a modal containing Store ID, Client ID, and Client Secret. Add an `.env.local` file with the following content to the root directory of the project. Click **Continue** to see the `FGA_API_URL` and `FGA_API_AUDIENCE`.

```env file=.env.local
# You can use any provider of your choice supported by Vercel AI
OPENAI_API_KEY=<your-openai-api-key>

# Auth0 FGA
FGA_STORE_ID=<your-fga-store-id>
FGA_CLIENT_ID=<your-fga-store-client-id>
FGA_CLIENT_SECRET=<your-fga-store-client-secret>
FGA_API_URL=https://api.xxx.fga.dev
FGA_API_AUDIENCE=https://api.xxx.fga.dev/
```

Next, navigate to **Model Explorer**. Update the model information with this:

```
model
  schema 1.1

type user

type doc
  relations
    define owner: [user]
    define viewer: [user, user:*]
    define can_view: owner or viewer
```

Remember to click **Save**.

## Secure the RAG Tool

After all this configuration, secure the RAG tool using Auth0 FGA and Auth0 AI SDK.

The starter application is already configured to handle documents and embeddings.

**Document Upload and Storage**

- You can upload documents through the UI (`src/app/documents/page.tsx`)
- Uploaded documents are processed by the API route (`src/app/api/documents/upload/route.ts`)
- APIs for uploading and retrieving documents are defined in (`src/lib/actions/documents.ts`).
- Database is defined in `src/lib/db`
- FGA helpers are defined in `src/lib/fga`
- Documents are stored as embeddings in a vector database for efficient retrieval (`src/lib/rag/embedding.ts`).

**Access Control with Auth0 FGA**

- When a document is uploaded, the app automatically creates [FGA tuples](https://docs.fga.dev/fga-concepts#what-is-a-relationship-tuple) to define which users can access which documents. A tuple signifies a user's relation to a given object. For example, the below tuple implies that all users can view the `<document name>` object.
- Navigate to the **Tuple Management** section to see the tuples being added. If you want to add a tuple manually for a document, click **+ Add Tuple**. Fill in the following information:
  - **User**: `user:*`
  - **Object**: select doc and add `<document name>` in the ID field
  - **Relation**: `viewer`

### Create a RAG tool

Define a RAG tool that uses the `FGAFilter` to filter authorized data from the vector database.

```tsx file=src/lib/tools/context-docs.ts
import { tool } from 'ai';
import { z } from 'zod';
import { FGAFilter } from '@auth0/ai';

import { findRelevantContent } from '@/lib/rag/embedding';
import { auth0 } from '../auth0';

export type DocumentWithScore = {
  content: string;
  documentId: string;
  similarity: number;
};

export const getContextDocumentsTool = tool({
  description:
    'Use the tool when user asks for documents or projects or anything that is stored in the knowledge base.',
  parameters: z.object({
    question: z.string().describe('the users question'),
  }),
  execute: async ({ question }) => {
    const session = await auth0.getSession();
    const user = session?.user;

    if (!user) {
      return 'There is no user logged in.';
    }

    const retriever = FGAFilter.create({
      buildQuery: (doc: DocumentWithScore) => ({
        user: `user:${user?.email}`,
        object: `doc:${doc.documentId}`,
        relation: 'can_view',
      }),
    });

    const documents = await findRelevantContent(question, 25);
    // filter docs based on FGA authorization
    const context = await retriever.filter(documents);
    return context;
  },
});
```

### Use the RAG tool from AI agent

Call the tool from your AI agent to get data from documents. Update the `/src/app/api/chat/route.ts` file with the following code:

```ts file=src/app/api/chat/route.ts
//...
import { getContextDocumentsTool } from '@/lib/tools/context-docs';

//... existing code
export async function POST(req: NextRequest) {
  //... existing code
  const tools = {
    getContextDocumentsTool,
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
```

## Test your application

Start the database and create required tables.

```bash
# start the postgres database
docker compose up -d
# create the database schema
npm run db:migrate
```

Start the application with `npm run dev`. Then, navigate to `http://localhost:3000`.
Upload a document from the documents tab and ask your AI Agent a question about the document! You should get a response with the relevant information. Now go to an incognito window and log in as a different user and try to ask the same question. You should not get a response. Now try sharing the document from the documents page to the second user and try again. You should see the information now.

That's it! You successfully integrated RAG protected by Auth0 FGA into your project.

Explore [the example app on GitHub](https://github.com/auth0-samples/auth0-ai-samples/tree/main/authorization-for-rag/vercel-ai-next-js).

## Next steps

- [Learn how to use Auth0 FGA to create a Relationship-Based Access Control (ReBAC) authorization model.](https://auth0.com/fine-grained-authorization)
- [Learn more about OpenFGA](https://openfga.dev/docs/fga)

---

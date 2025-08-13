import { tool } from 'llamaindex';
import { z } from 'zod';
import { SerpAPI } from '@langchain/community/tools/serpapi';

const serpApi = new SerpAPI();

// Requires process.env.SERPAPI_API_KEY to be set: https://serpapi.com/
export const serpApiTool = tool({
  name: 'serpApi',
  description: serpApi.description,
  parameters: z.object({
    q: z.string().describe('The query to search the web for'),
  }),
  execute: async ({ q }) => {
    return await serpApi._call(q);
  },
});

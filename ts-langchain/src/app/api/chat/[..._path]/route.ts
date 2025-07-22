import { initApiPassthrough } from 'langgraph-nextjs-api-passthrough';

import { getRefreshToken, getAccessToken, getUser } from '@/lib/auth0';

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
              accessToken: await getAccessToken(),
              user: await getUser(),
            },
          },
        },
      };
    }

    return body;
  },
});

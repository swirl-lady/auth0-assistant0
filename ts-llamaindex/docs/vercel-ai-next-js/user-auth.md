# Docs > Get Started > User Authentication (JS/Vercel)

---

# User Authentication

Authentication is the process of proving a user's identity before granting them access to a resource. In this quickstart, you'll learn how to bring [Universal Login](https://auth0.com/docs/authenticate/login/auth0-universal-login) to your GenAI application and leverage OAuth 2.0 and OpenID Connect to securely authenticate users.

When a user authenticates with an identity provider through Auth0, Auth0 can pass user information in an ID token to an application or AI agent to deliver a personalized experience. For example, a chatbot can greet a user with their name and display relevant information based on the user's profile.

By the end of this quickstart, you should have an application that can:

- Sign up and log in using a username and password or a Google account.
- Authenticate and authorize users using OAuth 2.0 and OpenID Connect.

## Prerequisites

Before getting started, make sure you have completed the following steps:

- Create an Auth0 Account and a Dev Tenant
- Create and configure a [Regular Web Application](https://auth0.com/docs/get-started/applications) to use with this quickstart.

## Prepare Next.js app

Use a starter template or create a Next.js web application using Next.js version 15 or above.

**Recommended**: To use a starter template, clone the [Auth0 AI samples](https://github.com/auth0-samples/auth0-ai-samples) repository:

```bash
git clone https://github.com/auth0-samples/auth0-ai-samples.git
cd auth0-ai-samples/authenticate-users/vercel-ai-next-js-starter
```

Else, create a new application using [create-next-app](https://nextjs.org/docs/app/getting-started/installation):

```bash
npx create-next-app@15 --src-dir
```

## Install dependencies

In the root directory of your project, install the [Auth0 Next.js SDK](http://next.js/):

```bash
npm i @auth0/nextjs-auth0@4
```

## Add login to your application

Secure the application using the Auth0 Next.js SDK.

### Create your environment file

In the root directory of your project, create the `.env.local` file and add the following variables. If you created an application with this quickstart, Auth0 automatically populates your environment variables for you:

```env file=.env.local
AUTH0_SECRET='use [openssl rand -hex 32] to generate a 32 bytes value'
APP_BASE_URL='http://localhost:3000'
AUTH0_DOMAIN='<your-auth0-domain>'
AUTH0_CLIENT_ID='<your-auth0-application-client-id>'
AUTH0_CLIENT_SECRET='<your-auth0-application-client-secret>'
```

### Create the Auth0 client

Create a file at `src/lib/auth0.ts` and instantiate a new Auth0 client:

```ts file=src/lib/auth0.ts
import { Auth0Client } from '@auth0/nextjs-auth0/server';

// Create an Auth0 Client.
export const auth0 = new Auth0Client();
```

The Auth0 client provides methods for handling authentication, sessions, and user data.

### Add the authentication middleware

The middleware intercepts incoming requests and applies Auth0's authentication logic. Create the following file at `src/middleware.ts`:

```ts file=src/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { auth0 } from './lib/auth0';

export async function middleware(request: NextRequest) {
  const authRes = await auth0.middleware(request);

  // Authentication routes — let the Auth0 middleware handle it.
  if (request.nextUrl.pathname.startsWith('/auth')) {
    return authRes;
  }

  const { origin } = new URL(request.url);
  const session = await auth0.getSession(request);

  // User does not have a session — redirect to login.
  if (!session) {
    return NextResponse.redirect(`${origin}/auth/login`);
  }
  return authRes;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image, images (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     * - $ (root)
     */
    '/((?!_next/static|_next/image|images|favicon.[ico|png]|sitemap.xml|robots.txt|$).*)',
  ],
};
```

### Add Login and Sign up buttons

Update the `src/app/page.tsx` file to display content based on the user session:

```tsx file=src/app/page.tsx
//...
import { auth0 } from '@/lib/auth0';

export default async function Home() {
  const session = await auth0.getSession();

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] my-auto gap-4">
        <h2 className="text-xl">You are not logged in</h2>
        <div className="flex gap-4">
          <Button asChild variant="default" size="default">
            <a href="/auth/login" className="flex items-center gap-2">
              <LogIn />
              <span>Login</span>
            </a>
          </Button>
          <Button asChild variant="default" size="default">
            <a href="/auth/login?screen_hint=signup">
              <UserPlus />
              <span>Sign up</span>
            </a>
          </Button>
        </div>
      </div>
    );
  }

  //... existing code

  // applicable only if you are using the starter template
  return (
    <ChatWindow
      endpoint="api/chat"
      emoji="🤖"
      placeholder={`Hello ${session?.user?.name}, I'm your personal assistant. How can I help you today?`}
      emptyStateComponent={InfoCard}
    />
  );
}
```

The app displays the **Sign up** or **Log in** buttons without a user session. If a user session exists, the app displays a welcome message with the user's name.

## Add User Profile Dropdown (Optional)

If you are using the starter template, you can add a user profile dropdown to your application.

```tsx file=src/app/layout.tsx
//...
import { auth0 } from '@/lib/auth0';
import UserButton from '@/components/auth0/user-button';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const session = await auth0.getSession();

  return (
    <html lang="en" suppressHydrationWarning>
      {/* ... existing code */}
      <body className={publicSans.className}>
        <NuqsAdapter>
          <div className="bg-secondary grid grid-rows-[auto,1fr] h-[100dvh]">
            <div className="grid grid-cols-[1fr,auto] gap-2 p-4 bg-black/25">
              {/* ... existing code */}
              <div className="flex justify-center">
                {session && (
                  <div className="flex items-center gap-2 px-4 text-white">
                    <UserButton user={session?.user!} logoutUrl="/auth/logout" />
                  </div>
                )}
                {/* ... existing code */}
              </div>
            </div>
            {/* ... existing code */}
          </div>
          <Toaster />
        </NuqsAdapter>
      </body>
    </html>
  );
}
```

## Run your application

Run this command to start your server:

```bash
npm run dev
```

Visit the URL `http://localhost:3000` in your browser.

You will see:

- A **Sign up** and **Log in** button if the user is not authenticated.
- A welcome message and user profile dropdown if the user is authenticated.

Explore [the example app on GitHub](https://github.com/auth0-samples/auth0-ai-samples/tree/main/authenticate-users/vercel-ai-next-js).

## Next steps

- To set up first-party tool calling, complete the
  [Call your APIs on user's behalf](https://auth0.com/ai/docs/call-your-apis-on-users-behalf) quickstart.
- To set up third-party tool calling, complete the
  [Call other's APIs on user's behalf](https://auth0.com/ai/docs/call-others-apis-on-users-behalf) quickstart.
- To explore the Auth0 Next.js SDK, see the
  [Github repo](https://github.com/auth0/nextjs-auth0).
- [User Authentication for GenAI docs](https://auth0.com/ai/docs/user-authentication).

---

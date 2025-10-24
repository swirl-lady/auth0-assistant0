# Architecture Overview: auth0-assistant0

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Architectural Patterns](#architectural-patterns)
4. [Key Technologies and Frameworks](#key-technologies-and-frameworks)
5. [Implementation Variants](#implementation-variants)
6. [Core Features and Functionality](#core-features-and-functionality)
7. [Security Architecture](#security-architecture)
8. [Database Schema](#database-schema)
9. [Dependencies and Integrations](#dependencies-and-integrations)
10. [Development Workflow](#development-workflow)

---

## Project Overview

**Assistant0** is an AI personal assistant that consolidates your digital life by dynamically accessing multiple tools to help you stay organized and efficient. The project demonstrates secure AI agent implementation using Auth0's identity and authorization platform.

The repository is designed as a **monorepo** containing multiple implementations of the same AI assistant using different AI frameworks and programming languages, allowing developers to choose the stack that best fits their needs.

### Key Objectives

- Demonstrate secure tool calling in AI agents using Auth0
- Showcase multiple AI framework implementations (LangChain, LlamaIndex, Vercel AI)
- Provide production-ready patterns for AI agent authentication and authorization
- Implement fine-grained access control for AI operations using Auth0 FGA

---

## Repository Structure

```
auth0-assistant0/
├── public/                      # Shared public assets (images, documentation)
├── ts-langchain/               # TypeScript + LangGraph.js implementation
│   ├── src/
│   │   ├── app/               # Next.js App Router pages and API routes
│   │   ├── components/        # React UI components
│   │   ├── lib/              # Core business logic
│   │   │   ├── agent.ts      # LangGraph agent configuration
│   │   │   ├── auth0-ai.ts   # Auth0 AI SDK integrations
│   │   │   ├── auth0.ts      # Auth0 authentication
│   │   │   ├── tools/        # AI agent tools
│   │   │   ├── rag/          # RAG implementation with embeddings
│   │   │   ├── db/           # Database schema and migrations
│   │   │   └── fga/          # Fine-grained authorization
│   │   └── middleware.ts     # Next.js middleware for auth
│   ├── package.json
│   └── langgraph.json        # LangGraph server configuration
├── ts-vercel-ai/              # TypeScript + Vercel AI SDK implementation
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React UI components
│   │   └── lib/              # Core business logic
│   └── package.json
├── ts-llamaindex/             # TypeScript + LlamaIndex implementation
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React UI components
│   │   └── lib/              # Core business logic
│   └── package.json
├── py-langchain/              # Python + LangGraph implementation
│   ├── backend/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── agents/      # LangGraph agent definitions
│   │   │   ├── api/         # FastAPI route handlers
│   │   │   ├── core/        # Core configuration and utilities
│   │   │   └── models/      # Data models
│   │   └── pyproject.toml
│   └── frontend/            # Vite + React frontend
│       ├── src/
│       └── package.json
├── py-llamaindex/            # Python + LlamaIndex (Coming Soon)
├── README.md
└── LICENSE
```

### Directory Layout Explanation

- **Root Level**: Contains shared documentation and assets
- **Implementation Directories**: Each directory (`ts-langchain`, `ts-vercel-ai`, etc.) is a complete, standalone application
- **TypeScript Implementations**: Use Next.js 15 with App Router for both frontend and backend
- **Python Implementation**: Separates concerns with FastAPI backend and React (Vite) frontend

---

## Architectural Patterns

### 1. **AI Agent Architecture**

The project implements an **agentic AI pattern** where the LLM acts as a reasoning engine that:
- Receives user requests
- Determines which tools to use
- Executes tools in sequence or parallel
- Synthesizes results into coherent responses

```
User Input → AI Agent (LLM) → Tool Selection → Tool Execution → Response
                ↑                                      |
                └─────── Feedback Loop ───────────────┘
```

### 2. **Authentication Flow**

```
User → Next.js/FastAPI → Auth0 (Authentication)
                       → Auth0 Token Vault (Credential Management)
                       → Third-party APIs (Gmail, Calendar, etc.)
```

- **Session-based auth** for web applications
- **Token exchange** for accessing third-party APIs
- **CIBA (Client Initiated Backchannel Authentication)** for async authorization

### 3. **Authorization Pattern (FGA)**

Uses **Auth0 Fine-Grained Authorization (FGA)** based on Zanzibar model:

```
User → Action → Resource
         ↓
    FGA Check → Allow/Deny
```

Example: `user:alice → can_view → doc:project_proposal`

### 4. **RAG (Retrieval Augmented Generation) Pattern**

```
User Query → Embedding → Vector Search → FGA Filter → Context → LLM → Response
```

Documents are:
1. Split into chunks
2. Embedded using OpenAI embeddings
3. Stored in PostgreSQL with pgvector
4. Retrieved based on semantic similarity
5. Filtered by user permissions (FGA)
6. Provided as context to LLM

### 5. **Tool Calling Pattern**

AI agent tools are wrapped with security decorators:

- `withGoogleConnection`: Manages Google OAuth token exchange via Auth0 Token Vault
- `withAsyncAuthorization`: Implements human-in-the-loop confirmation for sensitive operations

---

## Key Technologies and Frameworks

### Programming Languages

| Language | Version | Usage |
|----------|---------|-------|
| TypeScript | 5.7.3 | Primary language for TS implementations |
| Python | ≥3.13 | Python implementation |
| JavaScript | ES2022+ | Runtime language for Node.js |

### Frontend Frameworks

#### TypeScript Implementations
- **Next.js 15.2.4**: Full-stack React framework with App Router
- **React 19.0.0**: UI library
- **Tailwind CSS 3.4.17**: Utility-first CSS framework
- **shadcn/ui**: Radix UI-based component library
- **Vite**: Build tool (for py-langchain frontend)

### Backend Frameworks

#### TypeScript
- **Next.js API Routes**: Serverless backend functions
- **LangGraph Server**: In-memory agent execution server

#### Python
- **FastAPI**: Modern async web framework
- **uvicorn**: ASGI server
- **LangGraph Server**: Agent execution server

### AI & ML Frameworks

| Framework | Implementation | Purpose |
|-----------|----------------|---------|
| **LangChain** | ts-langchain, py-langchain | Agent orchestration, tool calling |
| **LangGraph** | ts-langchain, py-langchain | Stateful agent workflows, checkpointing |
| **Vercel AI SDK** | ts-vercel-ai | Simplified AI agent with streaming |
| **LlamaIndex** | ts-llamaindex | Agent orchestration, RAG |
| **OpenAI** | All | LLM provider (GPT-4o-mini) |

### Authentication & Authorization

- **Auth0 Next.js SDK** (`@auth0/nextjs-auth0`): Session management for Next.js
- **Auth0 FastAPI SDK** (`auth0-fastapi`): Authentication for Python backend
- **Auth0 AI SDK**: 
  - `@auth0/ai-langchain`: LangChain integrations
  - `@auth0/ai-vercel`: Vercel AI integrations
  - `@auth0/ai-llamaindex`: LlamaIndex integrations
- **Auth0 FGA SDK** (`@openfga/sdk`): Fine-grained authorization

### Database & ORM

#### TypeScript
- **PostgreSQL 16**: Primary database
- **Drizzle ORM 0.43.1**: Type-safe ORM
- **pgvector**: Vector similarity search extension
- **Drizzle Kit**: Schema migrations

#### Python
- **PostgreSQL 16**: Primary database
- **SQLModel 0.0.24**: Pydantic + SQLAlchemy ORM
- **psycopg 3.2.9**: PostgreSQL adapter
- **langchain-postgres**: Vector store for LangChain

### Development Tools

- **Docker Compose**: Local PostgreSQL setup
- **npm-run-all**: Parallel script execution
- **tsx**: TypeScript execution for scripts
- **uv**: Fast Python package installer (Python impl)
- **ESLint**: Linting
- **Prettier**: Code formatting

---

## Implementation Variants

### 1. TypeScript + LangGraph.js (`ts-langchain/`)

**Status**: ✅ Production Ready

**Stack**:
- Framework: Next.js 15 with App Router
- AI: LangGraph.js + LangChain.js
- Database: Drizzle ORM + PostgreSQL + pgvector

**Architecture**:
- Full-stack Next.js application
- Separate LangGraph server for agent execution
- API passthrough pattern for LangGraph communication
- Real-time streaming responses

**Key Files**:
- `src/lib/agent.ts`: Agent configuration and tool setup
- `src/lib/auth0-ai.ts`: Auth0 AI SDK integrations
- `src/app/api/chat/[..._path]/route.ts`: LangGraph API passthrough

**Running**:
```bash
npm run all:dev  # Starts LangGraph server + Next.js
```

### 2. TypeScript + Vercel AI SDK (`ts-vercel-ai/`)

**Status**: ✅ Production Ready

**Stack**:
- Framework: Next.js 15 with App Router
- AI: Vercel AI SDK
- Database: Drizzle ORM + PostgreSQL + pgvector

**Architecture**:
- Simpler than LangGraph (no separate server needed)
- Built-in streaming support
- Tools defined in API route handlers
- Direct integration with AI SDK UI components

**Key Features**:
- Lightweight and Vercel-optimized
- Excellent streaming UX
- Lower bundle size

**Running**:
```bash
npm run dev
```

### 3. TypeScript + LlamaIndex (`ts-llamaindex/`)

**Status**: ✅ Production Ready

**Stack**:
- Framework: Next.js 15 with App Router
- AI: LlamaIndex.TS + Vercel AI SDK (for UI streaming)
- Database: Drizzle ORM + PostgreSQL + pgvector

**Architecture**:
- Combines LlamaIndex agent with Vercel AI SDK for UI
- Native RAG capabilities through LlamaIndex
- Tool calling via LlamaIndex function tools

**Running**:
```bash
npm run dev
```

### 4. Python + LangGraph (`py-langchain/`)

**Status**: ✅ Production Ready

**Stack**:
- Backend: FastAPI + LangGraph Python
- Frontend: Vite + React + TanStack Query
- Database: SQLModel + PostgreSQL + pgvector

**Architecture**:
- Separated backend and frontend
- FastAPI serves API and handles Auth0 authentication
- Separate LangGraph server for agent execution
- React SPA frontend with TanStack Query for state management

**Key Files**:
- `backend/app/main.py`: FastAPI application
- `backend/app/agents/`: Agent definitions
- `frontend/src/`: React application

**Running**:
```bash
# Backend
cd backend
fastapi dev app/main.py

# LangGraph server (separate terminal)
langgraph dev --port 54367 --allow-blocking

# Frontend (separate terminal)
cd frontend
npm run dev
```

### 5. Python + LlamaIndex (`py-llamaindex/`)

**Status**: 🚧 Coming Soon

---

## Core Features and Functionality

### 1. Gmail Integration

**Tools**: `GmailSearch`, `GmailCreateDraft`

**Capabilities**:
- Search inbox with natural language queries
- Summarize emails by category, urgency, or topic
- Create draft replies
- Categorize conversations

**Security**: Uses Auth0 Token Vault to securely exchange user's access token for Gmail API access

**Scopes Required**:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.compose`

### 2. Google Calendar Management

**Tools**: `GoogleCalendarViewTool`, `GoogleCalendarCreateTool`, `getCalendarEventsTool`

**Capabilities**:
- View upcoming meetings
- Check for scheduling conflicts
- Suggest time slots for new appointments
- Create calendar events

**Security**: Token exchange via Auth0 Token Vault

**Scopes Required**:
- `https://www.googleapis.com/auth/calendar.events`

### 3. User Information Retrieval

**Tool**: `getUserInfoTool`

**Capabilities**:
- Retrieve user profile information from Auth0
- Access name, email, and other profile attributes
- Personalize responses

**Source**: Auth0 user session

### 4. Online Shopping with Human-in-the-Loop

**Tool**: `shopOnlineTool`

**Capabilities**:
- Make purchase requests on behalf of the user
- Requires explicit user confirmation via Guardian Push notification
- Implements CIBA (Client Initiated Backchannel Authentication) flow

**Security**: 
- Uses Auth0 async authorization
- Binding message shown to user for approval
- Configurable expiration time
- Can interrupt agent execution pending approval

**Flow**:
```
1. User: "Buy 2 books"
2. Agent: Triggers shopOnlineTool
3. Auth0: Sends push notification to user's mobile device
4. User: Approves/denies on Guardian app
5. Agent: Receives confirmation and proceeds/aborts
```

### 5. Document Upload and RAG

**Tools**: `getContextDocumentsTool`

**Capabilities**:
- Upload PDF and text documents
- Automatic text extraction and chunking
- Vector embeddings stored in PostgreSQL
- Semantic search across documents
- Share documents with other users
- Fine-grained access control via Auth0 FGA

**Process**:
1. User uploads document via UI
2. Backend extracts text (PDF/text)
3. Text is split into chunks
4. Chunks are embedded using OpenAI embeddings
5. Embeddings stored in PostgreSQL with pgvector
6. FGA policies control who can view documents
7. Agent retrieves relevant chunks during chat

**Security**: FGA ensures users can only access documents they own or have been shared with

### 6. Web Search

**Tool**: `SerpAPI`

**Capabilities**:
- Search the web for current information
- Supplement LLM knowledge with real-time data

**Requirements**: SerpAPI API key (optional)

### 7. Calculator

**Tool**: `Calculator`

**Capabilities**:
- Perform mathematical calculations
- Parse natural language math expressions

---

## Security Architecture

### Authentication Layer

**Web Applications** (Next.js/FastAPI):
- Session-based authentication via Auth0
- OIDC (OpenID Connect) protocol
- Secure HTTP-only cookies
- PKCE (Proof Key for Code Exchange) flow

**APIs**:
- JWT bearer tokens
- Audience validation
- Scope-based permissions

### Authorization Layers

#### 1. **Application-Level Authorization**
- Route protection via middleware
- Session validation on every request
- User context passed to AI agent

#### 2. **Token Vault (Federated Token Exchange)**

**Problem**: AI agents need to call third-party APIs (Gmail, Calendar) on behalf of users without storing credentials.

**Solution**: Auth0 Token Vault

**How it works**:
```
1. User authenticates with Auth0
2. User grants OAuth consent to Google services
3. Auth0 stores Google refresh token securely
4. Agent requests access token for Google via Token Vault
5. Auth0 exchanges tokens using OAuth 2.0 Token Exchange (RFC 8693)
6. Agent receives scoped access token for Google APIs
7. Token has limited lifetime and scope
```

**Benefits**:
- No credential storage in application
- Automatic token refresh
- Scope limitation
- Centralized token management
- Audit trail

**Implementation** (TypeScript):
```typescript
export const withGoogleConnection = auth0AICustomAPI.withTokenVault({
  connection: 'google-oauth2',
  scopes: [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar.events',
  ],
  accessToken: async (_, config) => {
    return config.configurable?.langgraph_auth_user?.getRawAccessToken();
  },
  subjectTokenType: SUBJECT_TOKEN_TYPES.SUBJECT_TYPE_ACCESS_TOKEN,
});
```

#### 3. **Async Authorization (CIBA)**

**Problem**: Sensitive operations (e.g., purchases) need explicit user approval.

**Solution**: Client Initiated Backchannel Authentication (CIBA)

**Flow**:
```
1. Agent initiates sensitive operation
2. Auth0 sends push notification to user's registered device
3. User sees binding message (e.g., "Buy 2 books for $50")
4. User approves or denies on Guardian app
5. Agent receives approval status
6. Agent proceeds or aborts operation
```

**Configuration**:
- Binding message customization
- Request expiration time
- Scopes and audience
- Callback handling

**Modes**:
- **Interrupt**: Agent execution pauses until user responds (production)
- **Block**: Agent waits synchronously (development only)
- **Callback**: Custom logic on approval/denial

**Implementation** (TypeScript):
```typescript
export const withAsyncAuthorization = auth0AI.withAsyncAuthorization({
  userID: async (_params, config) => {
    return config?.configurable?._credentials?.user?.sub;
  },
  bindingMessage: async ({ product, qty }) => `Do you want to buy ${qty} ${product}`,
  scopes: ['openid', 'product:buy'],
  audience: process.env['SHOP_API_AUDIENCE'],
  onAuthorizationRequest: async (authReq, creds) => {
    // Handle request sent
  },
  onUnauthorized: async (e: Error) => {
    // Handle denial
  },
});
```

#### 4. **Fine-Grained Authorization (FGA)**

**Problem**: Control access to specific documents in RAG pipeline.

**Solution**: Auth0 FGA (based on Google Zanzibar)

**Model**:
```
type user

type doc
  relations
    define owner: [user]
    define viewer: [user]
    define can_view: owner or viewer
```

**Authorization Check**:
```typescript
const retriever = FGARetriever.create({
  retriever: vectorStore.asRetriever(),
  buildQuery: (doc) => ({
    user: `user:${user?.email}`,
    object: `doc:${doc.metadata.documentId}`,
    relation: 'can_view',
  }),
});
```

**Use Cases**:
- Document sharing
- Multi-tenant isolation
- Role-based access
- Hierarchical permissions

### Security Best Practices Demonstrated

1. **No Credential Storage**: Credentials never stored in application code or database
2. **Least Privilege**: Tokens have minimal required scopes
3. **Short-Lived Tokens**: Access tokens expire quickly
4. **User Consent**: Explicit consent required for OAuth connections
5. **Human-in-the-Loop**: Critical operations require user approval
6. **Fine-Grained Access**: Document-level access control
7. **Audit Trail**: Auth0 logs all authentication and authorization events
8. **Secure Defaults**: HTTPS, secure cookies, CSRF protection

---

## Database Schema

### PostgreSQL with pgvector Extension

The application uses PostgreSQL as the primary database with the pgvector extension for vector similarity search.

### Schema: Documents Table

**Purpose**: Store uploaded documents

```sql
CREATE TABLE documents (
  id VARCHAR(191) PRIMARY KEY,
  content BYTEA NOT NULL,                    -- Binary content of file
  file_name VARCHAR(300) NOT NULL,
  file_type VARCHAR(100) NOT NULL,           -- e.g., 'pdf', 'txt'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  user_id VARCHAR(191) NOT NULL,             -- Auth0 user ID
  user_email VARCHAR(191) NOT NULL,          -- User's email
  shared_with VARCHAR(300)[]                 -- Array of user emails
);
```

**TypeScript (Drizzle ORM)**:
```typescript
export const documents = pgTable('documents', {
  id: varchar('id', { length: 191 }).primaryKey(),
  content: bytea('content').notNull(),
  fileName: varchar('file_name', { length: 300 }).notNull(),
  fileType: varchar('file_type', { length: 100 }).notNull(),
  createdAt: timestamp('created_at').notNull().default(sql`now()`),
  updatedAt: timestamp('updated_at').notNull().default(sql`now()`),
  userId: varchar('user_id', { length: 191 }).notNull(),
  userEmail: varchar('user_email', { length: 191 }).notNull(),
  sharedWith: varchar('shared_with', { length: 300 }).array(),
});
```

### Schema: Embeddings Table

**Purpose**: Store vector embeddings for semantic search

```sql
CREATE TABLE embeddings (
  id VARCHAR(191) PRIMARY KEY,
  document_id VARCHAR(191) REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,                     -- Text chunk
  metadata JSONB NOT NULL,                   -- Chunk metadata
  embedding VECTOR(1536) NOT NULL            -- OpenAI embedding (1536 dimensions)
);

CREATE INDEX embedding_index ON embeddings 
USING hnsw (embedding vector_cosine_ops);    -- HNSW index for fast similarity search
```

**TypeScript (Drizzle ORM)**:
```typescript
export const embeddings = pgTable(
  'embeddings',
  {
    id: varchar('id', { length: 191 }).primaryKey(),
    documentId: varchar('document_id', { length: 191 })
      .references(() => documents.id, { onDelete: 'cascade' }),
    content: text('content').notNull(),
    metadata: jsonb('metadata').notNull(),
    embedding: vector('embedding', { dimensions: 1536 }).notNull(),
  },
  (table) => [
    index('embeddingIndex')
      .using('hnsw', table.embedding.op('vector_cosine_ops'))
  ]
);
```

### Vector Search

**Index Type**: HNSW (Hierarchical Navigable Small World)
- Approximate nearest neighbor search
- Trade-off between speed and accuracy
- Optimal for high-dimensional vectors

**Distance Metric**: Cosine similarity
- Measures angle between vectors
- Range: -1 (opposite) to 1 (identical)
- Standard for text embeddings

**Query Pattern**:
```typescript
const results = await db
  .select()
  .from(embeddings)
  .orderBy(sql`embedding <=> ${queryEmbedding}`)
  .limit(5);
```

---

## Dependencies and Integrations

### Core Dependencies

#### TypeScript Implementations

**AI & LLM**:
- `@langchain/core`, `langchain`: LangChain framework
- `@langchain/langgraph`: Stateful agent graphs
- `@langchain/openai`: OpenAI LLM integration
- `@langchain/community`: Community tools (Gmail, Calendar, SerpAPI)
- `ai` (Vercel AI SDK): Streaming AI responses
- `llamaindex`: LlamaIndex framework

**Auth0**:
- `@auth0/nextjs-auth0`: Next.js authentication
- `@auth0/ai-langchain`: Auth0 AI SDK for LangChain
- `@auth0/ai-vercel`: Auth0 AI SDK for Vercel AI
- `@auth0/ai-llamaindex`: Auth0 AI SDK for LlamaIndex
- `@openfga/sdk`: Fine-grained authorization

**Database**:
- `drizzle-orm`: Type-safe ORM
- `drizzle-kit`: Migration tool
- `pg`, `postgres`: PostgreSQL clients

**Frontend**:
- `react@19.0.0`: UI library
- `next@15.2.4`: Full-stack framework
- `tailwindcss`: CSS framework
- `@radix-ui/*`: Accessible UI components
- `lucide-react`: Icon library
- `react-markdown`: Markdown rendering
- `marked`: Markdown parser

**Utilities**:
- `zod`: Schema validation
- `nanoid`: ID generation
- `date-fns`: Date manipulation
- `googleapis`: Google APIs client
- `pdf-parse`: PDF text extraction

#### Python Implementation

**AI & LLM**:
- `langgraph>=0.5.4`: Stateful agent graphs
- `langchain-openai>=0.3.28`: OpenAI integration
- `langchain-postgres>=0.0.15`: PostgreSQL vector store
- `langchain-text-splitters>=0.3.0`: Text chunking

**Auth0**:
- `auth0-ai>=1.0.0b4`: Auth0 AI SDK
- `auth0-ai-langchain>=1.0.0b4`: LangChain integration
- `auth0-fastapi>=1.0.0b4`: FastAPI authentication
- `openfga-sdk>=0.9.5`: Fine-grained authorization

**Backend**:
- `fastapi[standard]>=0.115.14`: Web framework
- `uvicorn`: ASGI server
- `pydantic-settings`: Configuration management
- `httpx`: Async HTTP client

**Database**:
- `sqlmodel>=0.0.24`: SQL ORM (Pydantic + SQLAlchemy)
- `psycopg>=3.2.9`: PostgreSQL adapter
- `psycopg-binary>=3.2.9`: Binary PostgreSQL driver

**Utilities**:
- `google-api-python-client`: Google APIs
- `pypdf2`: PDF processing

**Frontend** (Vite + React):
- `react@19.1.0`: UI library
- `react-router@7.7.0`: Routing
- `@tanstack/react-query`: Async state management
- `axios`: HTTP client
- `vite`: Build tool

### External Service Integrations

| Service | Purpose | Authentication | Scope |
|---------|---------|----------------|-------|
| **OpenAI API** | LLM provider, embeddings | API key | N/A |
| **Auth0** | Identity provider | OIDC | Full platform |
| **Auth0 FGA** | Fine-grained authorization | Client credentials | Store access |
| **Gmail API** | Email operations | OAuth 2.0 via Token Vault | `gmail.readonly`, `gmail.compose` |
| **Google Calendar API** | Calendar operations | OAuth 2.0 via Token Vault | `calendar.events` |
| **SerpAPI** (optional) | Web search | API key | N/A |
| **PostgreSQL** | Database | Username/password | N/A |

### Environment Variables

**Shared across implementations**:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Auth0 Web App
AUTH0_SECRET=...
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_SCOPE=openid profile email offline_access
AUTH0_AUDIENCE=...

# Auth0 Custom API Client (for Token Vault)
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CUSTOM_API_CLIENT_ID=...
AUTH0_CUSTOM_API_CLIENT_SECRET=...

# Auth0 FGA
FGA_STORE_ID=...
FGA_CLIENT_ID=...
FGA_CLIENT_SECRET=...
FGA_API_URL=https://api.us1.fga.dev

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/assistant0

# Optional
SERPAPI_API_KEY=...

# Shopping API (for demo)
SHOP_API_AUDIENCE=https://shop-api.example.com
```

---

## Development Workflow

### Prerequisites

1. **Node.js**: ≥18.x (for TypeScript implementations)
2. **Python**: ≥3.13 (for Python implementation)
3. **Docker**: For PostgreSQL
4. **Auth0 Account**: Free tier available
5. **Auth0 FGA Account**: Free tier available
6. **OpenAI API Key**: Paid service

### Setup Steps (TypeScript Implementations)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/auth0-samples/auth0-assistant0.git
   cd auth0-assistant0/ts-langchain  # or ts-vercel-ai, ts-llamaindex
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   # or
   bun install
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your credentials
   ```

4. **Start Database**:
   ```bash
   docker compose up -d
   ```

5. **Run Migrations**:
   ```bash
   npm run db:migrate
   ```

6. **Initialize FGA**:
   ```bash
   npm run fga:init
   ```

7. **Start Development Server**:
   
   **For ts-langchain**:
   ```bash
   npm run all:dev  # Starts LangGraph server + Next.js
   ```
   
   **For ts-vercel-ai and ts-llamaindex**:
   ```bash
   npm run dev  # Just Next.js
   ```

8. **Access Application**:
   - Open http://localhost:3000
   - Login with Auth0
   - Connect Google services
   - Start chatting!

### Setup Steps (Python Implementation)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/auth0-samples/auth0-assistant0.git
   cd auth0-assistant0/py-langchain
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your credentials
   
   uv sync  # Install dependencies
   ```

3. **Start Database**:
   ```bash
   docker compose up -d
   ```

4. **Initialize FGA**:
   ```bash
   source .venv/bin/activate
   python -m app.core.fga_init
   ```

5. **Start Backend**:
   ```bash
   fastapi dev app/main.py
   ```

6. **Start LangGraph Server** (separate terminal):
   ```bash
   source .venv/bin/activate
   langgraph dev --port 54367 --allow-blocking
   ```

7. **Frontend Setup** (separate terminal):
   ```bash
   cd frontend
   cp .env.example .env.local
   # Edit if needed
   
   npm install
   npm run dev
   ```

8. **Access Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - LangGraph: http://localhost:54367

### Development Scripts

#### TypeScript

```bash
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Build and start production server
npm run lint             # Run ESLint
npm run format           # Format with Prettier
npm run db:generate      # Generate migrations
npm run db:migrate       # Run migrations
npm run db:studio        # Open Drizzle Studio
npm run fga:init         # Initialize FGA store
```

#### Python

```bash
fastapi dev app/main.py  # Start FastAPI dev server
uv sync                  # Install/update dependencies
python -m app.core.fga_init  # Initialize FGA
```

### Project Decisions & Rationale

**Why Next.js for TypeScript implementations?**
- Full-stack framework (frontend + API routes)
- Excellent developer experience
- Built-in optimizations (SSR, code splitting, image optimization)
- Vercel deployment ready
- React Server Components support

**Why separate frontend/backend for Python?**
- FastAPI for high-performance async APIs
- Vite for modern frontend build tooling
- Clear separation of concerns
- Easier to scale independently

**Why multiple implementations?**
- Demonstrate framework flexibility
- Let developers choose preferred stack
- Show Auth0 SDK works across ecosystems
- Educational: compare patterns across frameworks

**Why pgvector?**
- Native PostgreSQL extension
- No separate vector database needed
- ACID compliance
- Cost-effective
- Mature and production-ready

**Why Auth0 FGA?**
- Industry-standard authorization model (Zanzibar)
- Scales to millions of authorization checks
- Decouples authorization from application logic
- Multi-tenant ready
- Real-time updates

**Why Token Vault?**
- Eliminates credential storage
- Centralized token lifecycle management
- Reduces security risk
- Simplifies OAuth flows
- Audit trail

---

## Deployment Considerations

### Vercel Deployment (TypeScript)

All TypeScript implementations are **Vercel-optimized**:
- Next.js native deployment
- Serverless functions for API routes
- Edge middleware support
- Environment variable management
- PostgreSQL via Vercel Postgres or external

**Deploy Button**:
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/auth0-samples/auth0-assistant0)

### Production Checklist

- [ ] Environment variables configured
- [ ] Database connection pool sized appropriately
- [ ] Auth0 production tenant configured
- [ ] FGA store created and policies deployed
- [ ] CORS origins configured
- [ ] Rate limiting enabled
- [ ] Error tracking (Sentry, etc.)
- [ ] Monitoring and logging
- [ ] Secrets stored securely (never in code)
- [ ] Token Vault connections configured
- [ ] Guardian Push enrolled for async auth

### Scaling Considerations

**LangGraph Server**:
- In-memory checkpointing suitable for development
- Production: Use Redis or PostgreSQL checkpointer
- Can be deployed as separate service

**Database**:
- Connection pooling essential
- Consider read replicas for scale
- pgvector index tuning for performance

**Auth0**:
- Rate limits: Be aware of tenant limits
- Token Vault: Cached tokens, minimal latency
- FGA: Sub-millisecond authorization checks at scale

---

## Contributing

Contributions are welcome! Please refer to the main README for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Built by [Deepu K Sasidharan](https://github.com/deepu105) and other contributors.

---

## Learn More

- [Tool Calling in AI Agents: Empowering Intelligent Automation Securely](https://auth0.com/blog/genai-tool-calling-intro/)
- [Build an AI Assistant with LangGraph, Vercel, and Next.js](https://auth0.com/blog/genai-tool-calling-build-agent-that-calls-gmail-securely-with-langgraph-vercelai-nextjs/)
- [Auth for GenAI Docs](https://auth0.com/ai/docs)
- [Auth0 Token Vault](https://auth0.com/docs/secure/tokens/token-vault)
- [Auth0 Fine-Grained Authorization](https://auth0.com/fine-grained-authorization)

---

**Last Updated**: 2024-10-24

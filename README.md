# 🤖 Discord AI Personality Bot

An intelligent Discord bot that mimics your personality and communication style using AI. The bot learns from role-based configurations, message history, and your WhatsApp chat exports to respond to Discord messages as if you were typing them yourself.

## 📋 Project Description

This project is a full-stack application that combines a Discord bot with a FastAPI backend, Next.js frontend, and a background data pipeline. The bot uses Google's Gemini AI to generate personalized responses based on:

- **User-specific roles and relationships** (bestfriend, friend, colleague, etc.)
- **Personality traits and preferences** (nicknames, nature, interests)
- **Conversation history** (previous messages for context)
- **WhatsApp chat embeddings** (vector similarity from your real conversations)
- **Your personal profile** (age, interests, communication style)

The system includes a web-based **Role Management Portal** and a **Chat Upload Pipeline** that processes WhatsApp exports through an async Redis-backed worker.

---

## 🎯 What the Model Does

The AI model (Google Gemini 2.5 Flash) acts as your digital twin by:

1. **Analyzing incoming Discord messages** from different users
2. **Retrieving role-specific information** about each user from the database
3. **Fetching conversation history** to maintain context
4. **Searching vector embeddings** from your real WhatsApp chats for similar conversations
5. **Generating personalized responses** that match your communication style
6. **Adapting language and tone** based on the relationship (formal, casual, romantic, etc.)

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Discord Platform"
        A[Discord Server]
    end
    
    subgraph "Discord Bot Layer"
        B[Discord Bot Client]
    end
    
    subgraph "Backend API — FastAPI"
        C[Main API Server]
        D[Chat Service]
        E[User Service]
        F[Role Service]
        G[Message Service]
        H[Chat Upload API]
        I[Jobs API]
    end

    subgraph "Background Worker — Koyeb"
        J["RQ SimpleWorker"]
        K[Data Pipeline]
    end

    subgraph "AI / ML Layer"
        L[Google Gemini AI]
        M["SentenceTransformer<br/>(all-MiniLM-L6-v2)"]
    end

    subgraph "Data Stores"
        N[(PostgreSQL)]
        O[(Redis — Upstash)]
        P[AWS S3]
    end
    
    subgraph "Frontend — Next.js"
        Q[Role Management Portal]
        R[Chat Upload UI]
    end
    
    A -->|Messages| B
    B -->|POST /chat| C
    C --> D
    D --> E
    D --> F
    D --> G
    D -->|Prompt| L
    L -->|Response| D
    E --> N
    F --> N
    G --> N

    R -->|POST /api/upload-chat| H
    H -->|Upload .txt| P
    H -->|Enqueue job| O
    O -->|Dequeue| J
    J --> K
    K -->|Download .txt| P
    K -->|Parse + Embed| M
    K -->|Insert vectors| N
    K -->|Upload JSON| P

    I -->|Poll job status| O
    Q -->|API Calls| C
    C -->|CRUD Operations| N
```

### Component Breakdown

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Discord Bot** | discord.py | Listens to @mentions and sends AI responses |
| **Backend API** | FastAPI + SQLAlchemy | Handles business logic and data management |
| **AI Engine** | Google Gemini 2.5 Flash | Generates personalized responses |
| **Embeddings** | SentenceTransformers (all-MiniLM-L6-v2) | Encodes WhatsApp chat pairs into vector embeddings |
| **Database** | PostgreSQL (asyncpg) | Stores users, roles, messages, and chat vectors |
| **Queue** | Redis (Upstash) + RQ | Job queue for async pipeline processing |
| **Worker** | RQ SimpleWorker (Koyeb) | Processes upload jobs in the background |
| **Object Storage** | AWS S3 | Stores raw chat uploads and processed JSON |
| **Frontend Portal** | Next.js 16 + React | Web interface for role management and chat upload |

---

## 💻 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Database Driver**: asyncpg
- **AI SDK**: Google Generative AI (Gemini)
- **Embeddings**: sentence-transformers
- **Discord Library**: discord.py
- **Task Queue**: RQ (Redis Queue)
- **Object Storage**: boto3 (AWS S3)
- **Environment Management**: python-dotenv
- **Logging**: coloredlogs

### Frontend
- **Framework**: Next.js 16
- **Language**: TypeScript
- **HTTP Client**: Axios
- **Styling**: CSS

### Infrastructure
- **Database**: PostgreSQL (Render)
- **Redis**: Upstash (TLS)
- **Worker Hosting**: Koyeb
- **Object Storage**: AWS S3
- **Server**: Uvicorn (ASGI)

---

## 🔄 Data Flows

### 1. Message Processing Flow

```mermaid
sequenceDiagram
    participant U as Discord User
    participant B as Discord Bot
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant AI as Gemini AI
    
    U->>B: @mention message
    B->>API: POST /chat (payload)
    API->>DB: Fetch user roles
    DB-->>API: Return role data
    API->>DB: Fetch message history
    DB-->>API: Return previous messages
    API->>API: Build personalized prompt
    API->>AI: Send prompt
    AI-->>API: Return AI response
    API->>DB: Store message
    API-->>B: Return response JSON
    B->>U: Send reply in Discord
```

### 2. Chat Upload & Injection Pipeline

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant S3 as AWS S3
    participant RQ as Redis Queue
    participant W as RQ Worker (Koyeb)
    participant ML as SentenceTransformer
    participant DB as PostgreSQL

    U->>FE: Upload .txt + reciever info
    FE->>API: POST /api/upload-chat (multipart)
    API->>S3: Upload raw .txt
    API->>RQ: Enqueue pipeline job
    API-->>FE: Return {job_id, s3_key}

    FE->>API: GET /api/jobs/{job_id} (polling)

    RQ->>W: Dequeue job
    W->>S3: Download .txt
    W->>W: Parse WhatsApp chat into pairs
    W->>ML: Generate embeddings
    W->>DB: Insert vectors (batch commit)
    W->>S3: Upload processed JSON
    W->>RQ: Mark job finished

    FE->>API: GET /api/jobs/{job_id}
    API-->>FE: {status: "finished"}
```

### 3. Role Management Flow

```mermaid
sequenceDiagram
    participant Admin as Admin (Browser)
    participant Portal as Next.js Portal
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    
    Admin->>Portal: Open portal
    Portal->>API: GET /api/users
    API->>DB: Query all users
    DB-->>API: Return users
    API-->>Portal: Return user list
    Portal-->>Admin: Display users
    
    Admin->>Portal: Edit user role
    Portal->>API: PATCH /api/role/{user_id}
    API->>DB: Update role data
    DB-->>API: Confirm update
    API-->>Portal: Return updated role
    Portal-->>Admin: Show success
```

### 4. Database Schema

```
users                    role                     bot_messages
├── id (PK)              ├── id (PK)              ├── id (PK)
├── user_id (Unique)     ├── user_id (Unique, FK) ├── channel_id
├── username             ├── user_name            ├── user_id
├── created_at           └── role (JSONB)         ├── content
└── updated_at                                    └── dateTime

channel_messages         chat_vectors
├── id (PK)              ├── id (PK)
├── server_id            ├── user_id
├── channel_id           ├── incoming
├── user_id              ├── reply
├── content              └── embedding (vector)
└── dateTime
```

---

## 📡 API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/{user_id}` | Get user with roles |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/{user_id}` | Update user |
| DELETE | `/api/users/{user_id}` | Delete user |

### Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/role/{user_id}` | Get user's role |
| POST | `/api/role` | Create new role |
| PATCH | `/api/role/{user_id}` | Update role (partial) |
| DELETE | `/api/role/{user_id}` | Delete role |

### Admin Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin-role/{user_id}` | Get admin role |
| POST | `/api/admin-role` | Create admin role |
| PATCH | `/api/admin-role/{user_id}` | Update admin role |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Process Discord chat message |

### Chat Upload & Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-chat` | Upload WhatsApp .txt + reciever info, returns `job_id` |
| GET | `/api/jobs/{job_id}` | Poll pipeline job status (`queued` / `started` / `finished` / `failed`) |

---

## 🚀 Installation & Setup

### Prerequisites

- ✅ **Python 3.11+**
- ✅ **Node.js 18+** and npm
- ✅ **PostgreSQL 14+**
- ✅ **Redis** (or Upstash account)
- ✅ **AWS S3 Bucket** configured
- ✅ **Discord Bot Token** ([Create here](https://discord.com/developers/applications))
- ✅ **Google Gemini API Key** ([Get it here](https://aistudio.google.com/app/apikey))

### Step 1: Clone the Repository

```bash
git clone https://github.com/p2ratik/Discord-Bot
cd Discord-Bot
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# Discord Bot Token
SECRET_KEY=your_discord_bot_token

# Google Gemini API Key
LLM_API_KEY=your_gemini_api_key

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:3000
API_URL=http://localhost:8000

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name

# Redis (Upstash or local)
REDIS_URL=rediss://default:password@host:6379
```

### Step 3: Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### Step 4: Initialize Database

```bash
python init_db.py
```

---

## 🎮 Running the Application

You need to run **four separate processes**:

#### Terminal 1 — Backend API
```bash
uvicorn app.main:app --reload
```

#### Terminal 2 — RQ Worker (Pipeline)
```bash
python -m app.redis.worker
```

#### Terminal 3 — Frontend Portal
```bash
cd frontend
npm run dev
```

> **Note:** The Discord bot starts automatically as a background task when the backend launches (see `main.py` startup event). No separate terminal is needed.

---

## Breaking Changes

### Version X.Y.Z (2026-02-15)

- **Environment Variable Renamed:** `MYSQL_KEY` → `POSTGRES_PASSWORD`
- **Database Migration:** Backend now uses **PostgreSQL** instead of MySQL
- See the [Migration Guide](#migration-guide-mysql--postgresql) below

### Version X.Y.Z (2026-02-21)

- **Redis + RQ Worker added:** Chat upload pipeline now runs asynchronously via a Redis-backed worker
- **New env var required:** `REDIS_URL` (Upstash or local Redis)
- **New endpoint:** `POST /api/upload-chat` now returns a `job_id` for status polling
- **New endpoint:** `GET /api/jobs/{job_id}` for polling pipeline status
- **New packages:** `redis>=5.0.0` and `rq>=1.16.0` added to `requirements.txt`

#### Migration Guide: MySQL → PostgreSQL

1. Backup MySQL: `mysqldump -u <user> -p <database> > backup.sql`
2. Set up PostgreSQL and create a new database
3. Import with `pgloader` or `mysql2pgsql`
4. Update `.env`: set `DATABASE_URL` to your PostgreSQL connection string
5. Remove references to `MYSQL_KEY`

---

## 📁 Project Structure

```
Discord/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── admin_roles.py      #   Admin role CRUD
│   │   ├── chat.py             #   POST /chat (Discord messages)
│   │   ├── chat_upload.py      #   POST /api/upload-chat
│   │   ├── jobs.py             #   GET /api/jobs/{job_id}
│   │   ├── roles.py            #   User role CRUD
│   │   └── users.py            #   User CRUD
│   ├── aws/                    # AWS S3 integration
│   │   └── aws_service.py      #   Upload / download from S3
│   ├── db/                     # Database configuration
│   │   ├── base.py             #   SQLAlchemy Base
│   │   └── session.py          #   Async engine + session factory
│   ├── discord_bot/            # Discord bot client
│   │   └── bot.py              #   Message handler + API relay
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── admin.py            #   AdminRole model
│   │   ├── chat.py             #   ChatVector model
│   │   ├── message.py          #   BotMessage + ChannelMessage
│   │   ├── role.py             #   Role model
│   │   └── user.py             #   User model
│   ├── redis/                  # Redis Queue infrastructure
│   │   ├── queue.py            #   Named RQ queue ("pipeline")
│   │   ├── redis_conn.py       #   Shared Redis connection
│   │   └── worker.py           #   SimpleWorker entry point
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── admin.py
│   │   ├── chat.py
│   │   ├── role.py
│   │   ├── upload.py
│   │   ├── user.py
│   │   └── whatsapp_info.py
│   ├── services/               # Business logic layer
│   │   ├── admin_service.py
│   │   ├── chat_service.py
│   │   ├── embeddings.py       #   SentenceTransformer wrapper
│   │   ├── message_service.py
│   │   ├── parse_whatsapp_chats.py  # WhatsApp .txt parser
│   │   ├── pipeline.py         #   S3 → Parse → Embed → DB pipeline
│   │   ├── prompt.py           #   Gemini prompt builder
│   │   ├── role_service.py
│   │   ├── user_service.py
│   │   └── vector_store.py     #   Insert vectors into Postgres
│   ├── utils/
│   │   └── logger.py           #   Centralized logger
│   └── main.py                 # FastAPI app + startup hooks
├── frontend/                   # Next.js web portal
│   ├── app/                    #   Pages (App Router)
│   ├── components/             #   React components
│   │   ├── ChatUpload.tsx      #     File upload + reciever form
│   │   ├── RoleEditor.tsx      #     Role JSON editor
│   │   ├── AdminRoleEditor.tsx #     Admin role editor
│   │   ├── UserList.tsx        #     User listing
│   │   ├── AdminList.tsx       #     Admin listing
│   │   └── AddUserModal.tsx    #     New user modal
│   ├── lib/
│   │   ├── api.ts              #   Axios API client
│   │   └── types.ts            #   TypeScript types
│   └── package.json
├── tests/
│   ├── chats_parse_test.py     # WhatsApp parser test
│   └── injection_pipeline_test.py  # End-to-end pipeline test
├── datasets/                   # Test chat files
├── .env                        # Environment variables (NOT in git)
├── .gitignore
├── init_db.py                  # Database table initialization
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🛡️ Security Notes

> [!CAUTION]
> **Never commit your `.env` file to version control!** It contains sensitive credentials.

- The `.gitignore` file is configured to exclude `.env`
- Rotate your Discord bot token if it's exposed
- Use Koyeb / Render environment variables for production secrets
- Never hardcode API keys in source code

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check `DATABASE_URL` in `.env`, verify PostgreSQL is running |
| Bot online but not replying | Ensure "Message Content Intent" is enabled in Discord Developer Portal |
| Upload returns 500 | Verify AWS credentials and S3 bucket name in `.env` |
| Job stuck in "queued" | Ensure the RQ worker is running: `python -m app.redis.worker` |
| Worker can't connect to Redis | Check `REDIS_URL` in `.env`, verify TLS (`rediss://`) for Upstash |
| Frontend "Loading..." forever | Check backend is running, browser console for CORS errors |

---

### 📄 License

This project is for personal use. Modify and distribute as needed.

### 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Built with ❤️ using FastAPI, Discord.py, Google Gemini AI, SentenceTransformers, and Redis Queue**

# AI Meeting Assistant

AI-powered backend application for processing meeting recordings.

The application asynchronously transcribes audio using Whisper and generates meeting summaries using Mistral AI.

## Features

- User registration and JWT authentication
- Meeting creation and management
- Audio file upload
- Asynchronous meeting processing with Celery
- Redis as a message broker
- Speech-to-text transcription with Whisper
- AI-generated meeting summaries with Mistral AI
- PostgreSQL database
- Async SQLAlchemy
- Alembic database migrations
- Docker and Docker Compose
- Automatic Celery task retries
- REST API with FastAPI
- Interactive API documentation with Swagger UI

## Architecture

```text
                        ┌──────────────┐
                        │    Client    │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   FastAPI    │
                        │     API      │
                        └──────┬───────┘
                               │
                    process_meeting()
                               │
                               ▼
                        ┌──────────────┐
                        │    Redis     │
                        │ Message      │
                        │   Broker     │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Celery    │
                        │    Worker    │
                        └──────┬───────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
          ┌──────────────┐           ┌──────────────┐
          │   Whisper    │           │   Mistral    │
          │ Transcription│           │ Summarization│
          └──────┬───────┘           └──────┬───────┘
                 │                          │
                 └────────────┬─────────────┘
                              ▼
                       ┌──────────────┐
                       │  PostgreSQL  │
                       └──────────────┘
```

## Processing Flow

1. User creates a meeting.
2. User uploads an audio recording.
3. The API stores the audio file.
4. The client sends a request to process the meeting.
5. FastAPI sends a Celery task to Redis.
6. Celery Worker receives the task.
7. Whisper transcribes the audio.
8. The transcript is stored in PostgreSQL.
9. Mistral generates a summary.
10. The summary is stored in PostgreSQL.
11. Meeting status is updated to `completed`.

### Meeting Status Flow

```text
PENDING
   ↓
UPLOADED
   ↓
TRANSCRIBING
   ↓
SUMMARIZING
   ↓
COMPLETED
```

If processing fails:

```text
TRANSCRIBING / SUMMARIZING
          ↓
        FAILED
```

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- AsyncPG

### AI

- Whisper
- Mistral AI

### Background Processing

- Celery
- Redis

### Infrastructure

- Docker
- Docker Compose

### Authentication

- JWT

## Project Structure

```text
ai-meeting-assistant/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── meeting.py
│   │       └── user.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── exeptions/
│   │   └── meeting.py
│   │
│   ├── models/
│   │   ├── enum.py
│   │   ├── meeting.py
│   │   ├── summary.py
│   │   ├── transcript.py
│   │   └── user.py
│   │
│   ├── repositories/
│   │   ├── meeting.py
│   │   ├── summary.py
│   │   ├── transcript.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   └── meeting.py
│   │
│   ├── services/
│   │   ├── audio.py
│   │   ├── meeting.py
│   │   ├── user.py
│   │   │
│   │   ├── summary/
│   │   │   ├── base.py
│   │   │   └── llm.py
│   │   │
│   │   └── transcription/
│   │       ├── base.py
│   │       └── whisper.py
│   │
│   ├── worker/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   └── main.py
│
├── uploads/
│
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-meeting-assistant
```

### 2. Configure environment variables

Create `.env` from `.env.example`.

```bash
cp .env.example .env
```

Configure the required variables:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/meeting_db

MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=mistral-small-latest

WHISPER_MODEL=tiny
FFMPEG_PATH=/usr/bin/ffmpeg

SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

### 3. Start the application

```bash
docker compose up --build
```

The application starts:

- FastAPI
- PostgreSQL
- Redis
- Celery Worker

### 4. Run migrations

```bash
docker compose exec api uv run alembic upgrade head
```

## API Documentation

Once the application is running, Swagger UI is available at:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

## Example API Flow

### Register

```http
POST /auth/register
```

### Login

```http
POST /auth/login
```

### Create a meeting

```http
POST /meetings
```

### Upload audio

```http
POST /meetings/{meeting_id}/upload
```

### Start processing

```http
POST /meetings/{meeting_id}/process
```

The processing endpoint returns immediately after the Celery task is queued.

Example:

```json
{
  "meeting_id": 13,
  "status": "processing"
}
```

The actual processing happens in the background.

### Get meeting

```http
GET /meetings/{meeting_id}
```

After successful processing:

```json
{
  "id": 13,
  "title": "Team Meeting",
  "status": "completed",
  "audio_path": "uploads/audio/example.mp3",
  "created_at": "2026-08-20T12:27:38.275497Z"
}
```

## Celery

Meeting processing is handled asynchronously using Celery.

The API does not wait for transcription and summarization to finish.

```text
FastAPI
   │
   └── Celery.delay()
           │
           ▼
         Redis
           │
           ▼
     Celery Worker
           │
           ├── Whisper
           └── Mistral
```

Celery tasks support automatic retries for unexpected failures.

## Database

The application uses PostgreSQL with asynchronous SQLAlchemy.

Main entities:

```text
User
 │
 └── Meeting
       ├── Transcript
       └── Summary
```

Database schema changes are managed with Alembic.

Run migrations with:

```bash
docker compose exec api uv run alembic upgrade head
```

## Docker Services

```text
api       → FastAPI application
worker    → Celery worker
postgres  → PostgreSQL database
redis     → Celery message broker
```

Start all services:

```bash
docker compose up
```

Stop services:

```bash
docker compose down
```

Rebuild after code or dependency changes:

```bash
docker compose up --build
```

## Testing

The project uses:

- pytest
- pytest-asyncio
- HTTPX
- mocks for external AI services

The test suite covers:

- Authentication
- Meeting endpoints
- Repositories
- Services
- Celery tasks
- Error handling

## Future Improvements

- Frontend application
- Real-time processing status
- WebSocket notifications
- Speaker diarization
- Meeting action items
- Key points extraction
- Search across meeting transcripts
- Improved Celery monitoring
- Production deployment             └──────────────┘
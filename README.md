# MLOps RAG Assistant Project

A full-stack Retrieval-Augmented Generation (RAG) application with document indexing, vector search, and conversational AI capabilities using Ollama, Qdrant, and Redis.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   Webapp    │─────▶│   Backend    │─────▶│   Ollama   │
│  (Vue.js)   │      │  (FastAPI)   │      │  (LLM)     │
└─────────────┘      └──────────────┘      └────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────▼─────┐   ┌─────▼─────┐
              │  Qdrant   │   │   Redis   │
              │ (Vectors) │   │ (History) │
              └───────────┘   └───────────┘
```

## Features

- **Document Processing**: Upload and index documents with automatic chunking and embedding
- **Vector Search**: Semantic search using Qdrant vector database
- **RAG Pipeline**: Context-aware responses using retrieved documents
- **Chat History**: Conversation persistence with Redis
- **Local LLM**: Privacy-focused with Ollama (qwen3:1.7b model)
- **Modern UI**: Responsive web interface built with Vue.js

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Ollama** - Local LLM inference (qwen3:1.7b)
- **Qdrant** - Vector database for semantic search
- **Redis** - Chat history and session management
- **Sentence Transformers** - Document embeddings (BAAI/bge-small-en-v1.5)

### Frontend
- **Vue.js** - Progressive JavaScript framework
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MLOps-Project
   ```

2. **Configure environment variables**

   Create `backend/.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and update as needed:
   ```env
   OLLAMA_MODEL=qwen3:1.7b
   EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   EMBEDDING_DIMENSIONS=384
   QDRANT_COLLECTION=documents
   ALLOW_ORIGINS=*
   ```

   Create `webapp/.env`:
   ```bash
   cp webapp/.env.example webapp/.env
   ```
   
   Edit `webapp/.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

   This will:
   - Build and start the backend API (port 8000)
   - Build and start the webapp (port 80)
   - Start Redis for chat history
   - Start Qdrant vector database
   - Start Ollama LLM service
   - Automatically pull the qwen3:1.7b model

4. **Access the application**
   - Web App: http://localhost
   - API Docs: http://localhost:8000/docs
   - Qdrant Dashboard: http://localhost:6333/dashboard

5. **Check service status**
   ```bash
   docker-compose ps
   ```

6. **View logs**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f ollama-pull
   ```

## Usage

### Indexing Documents

1. Place documents in the `backend/data/` directory
2. Use the API to trigger indexing:
   ```bash
   curl -X POST http://localhost:8000/api/index
   ```

### Chatting with the Assistant

1. Open http://localhost in your browser
2. Type your questions in the chat interface
3. The assistant will search relevant documents and provide contextualized answers

### API Endpoints

- `GET /` - Health check
- `POST /api/chat` - Send chat messages (SSE stream)
- `POST /api/index` - Index documents from data directory
- `GET /api/export` - Export chat history
- `DELETE /api/sessions/{session_id}` - Clear chat session

See full API documentation at http://localhost:8000/docs

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd webapp
npm install
npm run dev
```

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama service URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | LLM model name | `qwen3:1.7b` |
| `EMBEDDING_MODEL` | Embedding model | `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSIONS` | Embedding size | `384` |
| `QDRANT_URL` | Qdrant service URL | `http://localhost:6333` |
| `QDRANT_COLLECTION` | Collection name | `documents` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `EXPORT_DIR` | Document directory | `data` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Services & Ports

| Service | Port(s) | Description |
|---------|---------|-------------|
| Backend API | 8000 | FastAPI application |
| Webapp | 80 | Vue.js frontend |
| Redis | 6379, 8001 | Cache & RedisInsight UI |
| Qdrant | 6333, 6334 | Vector DB & dashboard |
| Ollama | 11434 | LLM inference |

## Troubleshooting

### Ollama model not pulling

Check the ollama-pull service logs:
```bash
docker-compose logs ollama-pull
```

If needed, manually pull the model:
```bash
docker exec -it mlops-ollama ollama pull qwen3:1.7b
```

### Backend can't connect to services

Ensure all services are running:
```bash
docker-compose ps
```

Check backend logs for connection errors:
```bash
docker-compose logs backend
```

### Webapp can't reach backend

Verify `webapp/.env` has correct API URL:
```env
VITE_API_URL=http://localhost:8000
```

Rebuild the webapp:
```bash
docker-compose up -d --build webapp
```

### Clear all data and restart

```bash
docker-compose down -v
docker-compose up -d
```

## Project Structure

```
MLOps-Project/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api.py       # API endpoints
│   │   ├── main.py      # Application entry
│   │   ├── vector_db.py # Qdrant integration
│   │   ├── embeddings.py # Embedding generation
│   │   ├── indexing.py  # Document processing
│   │   ├── assistants/  # LLM assistant logic
│   │   └── utils/       # Helper utilities
│   ├── data/            # Document storage
│   ├── Dockerfile
│   └── pyproject.toml
├── webapp/              # Vue.js frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page views
│   │   └── api.js       # API client
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml   # Unified orchestration
```

## License

[Your License Here]

## Contributing

[Contribution guidelines]

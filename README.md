# QA Bot - Full-Stack Application with Local Embeddings Database

A comprehensive full-stack Q&A application built with FastAPI (backend) and React with TypeScript (frontend), featuring a local vector embeddings database for semantic search and document retrieval.

## Project Structure

```
qa-bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── models/         # Pydantic models
│   │   │   ├── __init__.py
│   │   │   └── qa.py
│   │   └── routers/        # API routes
│   │       ├── __init__.py
│   │       └── api.py
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container config
├── backend/                 # FastAPI backend with embeddings
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── models/         # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── qa.py       # Q&A models
│   │   │   └── document.py # Document and embedding models
│   │   ├── routers/        # API routes
│   │   │   ├── __init__.py
│   │   │   ├── api.py      # Q&A endpoints
│   │   │   └── documents.py # Document upload/query endpoints
│   │   └── services/       # Business logic services
│   │       ├── __init__.py
│   │       ├── embedding_service.py # Embedding generation
│   │       ├── vector_store.py      # FAISS vector database
│   │       └── document_processor.py # File processing
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container config
│   └── .dockerignore
├── frontend/               # React frontend with TypeScript
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx        # Main React component
│   │   ├── App.css        # Styles
│   │   ├── index.tsx      # React entry point
│   │   ├── index.css      # Global styles
│   │   └── types/
│   │       └── api.ts     # TypeScript type definitions
│   ├── package.json       # Node.js dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   ├── Dockerfile         # Frontend container config
│   └── .dockerignore
├── test_documents/        # Sample documents for testing
│   ├── sample.txt         # Sample text document
│   └── README.md          # Test documentation
├── docker-compose.yml     # Orchestration config
├── Makefile              # Development commands
└── README.md
```

## Features

### Core Functionality

- **Document Upload**: Support for .txt and .pdf files
- **Text Chunking**: Automatic document splitting with configurable size and overlap
- **Vector Embeddings**: Generate embeddings using sentence transformers
- **Local Vector Database**: FAISS-based storage for efficient similarity search
- **Semantic Search**: Query documents using natural language
- **User Management**: User-specific document isolation

### Technical Features

- **Backend**: FastAPI with auto-reload support
- **Frontend**: React with TypeScript and hot-reloading
- **Docker**: Fully containerized development environment
- **CORS**: Configured for cross-origin requests
- **Type Safety**: Full TypeScript support in frontend
- **API Documentation**: Interactive Swagger UI
- **Health Checks**: Service monitoring and status endpoints

## Quick Start

1. **Clone and navigate to the project**:

   ```bash
   cd qa-bot
   ```

2. **Start the application**:

   ```bash
   make setup
   make restart
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Backend Development

The FastAPI backend runs on port 8000 with auto-reload enabled. Any changes to Python files will automatically restart the server.

**API Endpoints**:

- `GET /` - Health check
- `GET /health` - Health status
- `GET /api/qa` - Get Q&A examples
- `POST /api/qa` - Create new Q&A pair

### Frontend Development

The React frontend runs on port 3000 with hot-reloading enabled. Any changes to TypeScript/CSS files will automatically refresh the browser.

**Features**:

- Add new questions
- View existing Q&A pairs
- Real-time updates
- Responsive design

### Docker Services

- **backend**: FastAPI service with uvicorn --reload
- **frontend**: React service with npm start (hot-reload)
- **Network**: Both services communicate via `qa-bot-network`
- **Volumes**: Persistent storage for vector database

### Volume Mounts

- Source code is mounted as volumes for both services
- Changes are reflected immediately without rebuilding containers
- `node_modules` is excluded from frontend volume to prevent conflicts
- `vector_data` volume persists FAISS index and metadata

### Health Checks

- Backend includes health check endpoint monitoring
- Frontend waits for backend to be healthy before starting

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_documents/sample.txt" \
  -F "user_id=test_user"
```

### Query Documents

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the technical stack?",
    "user_id": "test_user",
    "top_k": 3,
    "similarity_threshold": 0.7
  }'
```

### Get User Documents

```bash
curl -X GET "http://localhost:8000/api/documents/test_user"
```

### System Statistics

```bash
curl -X GET "http://localhost:8000/stats"
```

## Development Commands

The project includes a comprehensive Makefile for easy development:

```bash
# Setup and start the project
make setup

# Build all services
make build

# Start services
make start

# Stop services
make stop

# Restart services
make restart

# View logs
make logs

# Test API endpoints
make test

# Clean up everything
make clean

# Get help
make help
```

## Configuration

### Environment Variables

- `PYTHONPATH=/app` - Python path for the backend
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `CHOKIDAR_USEPOLLING=true` - File watching for frontend
- `REACT_APP_API_URL=http://localhost:8000` - API URL for frontend

### Vector Database Configuration

- **Storage**: FAISS index stored in `/app/data/vector_store/`
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Chunk Size**: 500 tokens (configurable)
- **Chunk Overlap**: 50 tokens (configurable)

## Architecture

### Backend Services

1. **EmbeddingService**: Generates embeddings using sentence transformers
2. **VectorStore**: Manages FAISS index and metadata storage
3. **DocumentProcessor**: Handles file uploads and text chunking
4. **FastAPI Router**: Exposes RESTful endpoints

### Data Flow

1. **Upload**: File → Text Extraction → Chunking → Embedding → FAISS Storage
2. **Query**: Text → Embedding → FAISS Search → Similarity Ranking → Results

### Storage Structure

```
data/vector_store/
├── faiss_index.bin    # FAISS vector index
└── metadata.pkl       # Document metadata
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Memory issues**: FAISS and sentence transformers require sufficient RAM
3. **File permissions**: Check Docker volume permissions
4. **Model download**: First run may take time to download embedding model

### Debugging

```bash
# Check service logs
make logs-backend
make logs-frontend

# Check service health
curl http://localhost:8000/health

# Check system stats
curl http://localhost:8000/stats
```

## Performance Considerations

- **Embedding Model**: `all-MiniLM-L6-v2` balances speed and quality
- **Chunk Size**: 500 tokens provides good context while maintaining performance
- **FAISS Index**: Uses IndexFlatIP for exact similarity search
- **Memory Usage**: Each embedding is 384 dimensions (float32)

## Security Notes

- User data is isolated by `user_id`
- No authentication implemented (add as needed)
- File uploads are validated by extension
- Temporary files are cleaned up after processing

## Next Steps

- Add user authentication and authorization
- Implement database persistence for metadata
- Add support for more file types (docx, html, etc.)
- Implement advanced chunking strategies
- Add embedding model fine-tuning capabilities
- Deploy to production with proper scaling

## Stopping the Application

```bash
docker-compose down
```

## Troubleshooting

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Permission issues**: On Linux/macOS, you might need to adjust file permissions
3. **Node modules**: If frontend issues occur, try rebuilding: `docker-compose up --build --force-recreate frontend`

## Next Steps

- Add a database (PostgreSQL, MongoDB, etc.)
- Implement user authentication
- Add more sophisticated Q&A features
- Deploy to production (Docker Swarm, Kubernetes, etc.)

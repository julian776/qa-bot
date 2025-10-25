# QA Bot - Full-Stack Application with PostgreSQL and Hugging Face Embeddings

A comprehensive full-stack Q&A application built with FastAPI (backend) and React with TypeScript (frontend), featuring PostgreSQL database with vector operations and Hugging Face embeddings API for semantic search and document retrieval.

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
- **Vector Embeddings**: Generate embeddings using Hugging Face API (all-MiniLM-L6-v2)
- **PostgreSQL Database**: Real database with vector operations for efficient similarity search
- **Semantic Search**: Query documents using natural language
- **User Management**: User-specific document isolation
- **Query Logging**: Track and analyze user queries

### Technical Features

- **Backend**: FastAPI with auto-reload support
- **Frontend**: React with TypeScript and hot-reloading
- **Database**: PostgreSQL with vector similarity operations
- **Embeddings**: Hugging Face API integration
- **Docker**: Fully containerized development environment
- **CORS**: Configured for cross-origin requests
- **Type Safety**: Full TypeScript support in frontend
- **API Documentation**: Interactive Swagger UI
- **Health Checks**: Service monitoring and status endpoints

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Hugging Face account and API key

### Setup Instructions

1. **Get your Hugging Face API key**:

   - Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a new token
   - Copy the token

2. **Run the setup script**:

   ```bash
   ./setup.sh
   ```

   The script will:

   - Create a `.env` file from the template
   - Prompt you to add your Hugging Face API key
   - Build and start all services
   - Initialize the PostgreSQL database
   - Verify all services are running

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Create environment file**:

   ```bash
   cp env.template .env
   ```

2. **Edit `.env` file**:

   - Replace `your_huggingface_api_key_here` with your actual Hugging Face API key

3. **Start services**:
   ```bash
   docker-compose up --build -d
   ```

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

- `HUGGINGFACE_API_KEY` - Your Hugging Face API key (required)
- `DATABASE_URL` - PostgreSQL connection string (auto-configured)
- `PYTHONPATH=/app` - Python path for the backend
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `CHOKIDAR_USEPOLLING=true` - File watching for frontend
- `REACT_APP_API_URL=http://localhost:8000` - API URL for frontend

### Database Configuration

- **Database**: PostgreSQL 15
- **Host**: localhost:5432 (or postgres:5432 in Docker)
- **Database Name**: qa_bot
- **Username**: qa_bot_user
- **Password**: qa_bot_password
- **Vector Operations**: Uses PostgreSQL's built-in vector similarity operators

### Embedding Configuration

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **API**: Hugging Face Inference API
- **Chunk Size**: 500 tokens (configurable)
- **Chunk Overlap**: 50 tokens (configurable)

## Architecture

### Backend Services

1. **EmbeddingService**: Generates embeddings using Hugging Face API
2. **VectorStore**: Manages PostgreSQL database with vector operations
3. **DocumentProcessor**: Handles file uploads and text chunking
4. **Database Models**: SQLAlchemy models for data persistence
5. **FastAPI Router**: Exposes RESTful endpoints

### Data Flow

1. **Upload**: File → Text Extraction → Chunking → Embedding (HF API) → PostgreSQL Storage
2. **Query**: Text → Embedding (HF API) → PostgreSQL Vector Search → Similarity Ranking → Results

### Database Schema

```sql
-- Document chunks table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    document_name VARCHAR(500) NOT NULL,
    chunk_index INTEGER NOT NULL,
    text_chunk TEXT NOT NULL,
    chunk_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSON
);

-- Embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    chunk_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    document_name VARCHAR(500) NOT NULL,
    embedding_vector FLOAT[] NOT NULL,  -- PostgreSQL array
    embedding_dimension INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Query logs table
CREATE TABLE query_logs (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    query_embedding FLOAT[],
    results_count INTEGER DEFAULT 0,
    processing_time FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `HUGGINGFACE_API_KEY` is set in your `.env` file
2. **Database Connection**: Check if PostgreSQL container is running and healthy
3. **Port conflicts**: Ensure ports 3000, 8000, and 5432 are available
4. **API Rate Limits**: Hugging Face API has rate limits; consider upgrading if needed
5. **Memory issues**: PostgreSQL and embeddings require sufficient RAM

### Debugging

```bash
# Check service logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f frontend

# Check service health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres psql -U qa_bot_user -d qa_bot -c "SELECT 1;"

# Check system stats
curl http://localhost:8000/stats
```

## Performance Considerations

- **Embedding Model**: `all-MiniLM-L6-v2` balances speed and quality (384 dimensions)
- **Chunk Size**: 500 tokens provides good context while maintaining performance
- **PostgreSQL Vector Operations**: Uses native vector similarity operators for efficiency
- **API Calls**: Hugging Face API handles model loading and caching
- **Database Indexing**: Proper indexes on user_id, document_name, and embedding vectors
- **Memory Usage**: Each embedding is 384 dimensions (float32)

## Security Notes

- User data is isolated by `user_id`
- No authentication implemented (add as needed)
- File uploads are validated by extension
- Temporary files are cleaned up after processing

## Next Steps

- Add user authentication and authorization
- Implement advanced chunking strategies (semantic chunking)
- Add support for more file types (docx, html, markdown, etc.)
- Implement embedding model fine-tuning capabilities
- Add query analytics and insights dashboard
- Implement document versioning and updates
- Add batch processing for large document collections
- Deploy to production with proper scaling and monitoring

## Stopping the Application

```bash
docker-compose down
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs -f`
3. Verify your Hugging Face API key is valid
4. Ensure all required ports are available

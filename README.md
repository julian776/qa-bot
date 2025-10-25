# QA Bot - Production-Ready Chatbot with MongoDB, Qdrant, and OpenAI

A comprehensive, production-ready question-answering chatbot system built with FastAPI (backend) and React with TypeScript (frontend), featuring MongoDB for metadata storage, Qdrant vector database for embeddings, and OpenAI API for semantic search and document retrieval.

## 🏗️ Architecture Overview

This system implements a modern, scalable chatbot architecture with the following components:

- **Backend**: FastAPI with async/await support
- **Database**: MongoDB for document metadata and user data
- **Vector Database**: Qdrant for high-performance similarity search
- **Embeddings**: OpenAI API for generating high-quality embeddings
- **Frontend**: React with TypeScript for modern UI
- **Containerization**: Docker Compose for easy deployment

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Setup Instructions

1. **Get your OpenAI API key**:

   - Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key

2. **Run the setup script**:

   ```bash
   ./setup.sh
   ```

   The script will:

   - Create a `.env` file from the template
   - Prompt you to add your OpenAI API key
   - Build and start all services
   - Initialize the databases
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

   - Replace `your_openai_api_key_here` with your actual OpenAI API key

3. **Start services**:
   ```bash
   docker-compose up --build -d
   ```

## 📁 Project Structure

```
qa-bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── database.py     # MongoDB connection setup
│   │   ├── models/         # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py  # MongoDB models
│   │   │   └── document.py # Document models
│   │   ├── routers/        # API routes
│   │   │   ├── __init__.py
│   │   │   ├── api.py      # Q&A endpoints
│   │   │   └── documents.py # Document upload/query endpoints
│   │   └── services/       # Business logic services
│   │       ├── __init__.py
│   │       ├── embedding_service.py # OpenAI embeddings
│   │       ├── qdrant_store.py      # Qdrant vector database
│   │       └── document_processor.py # File processing
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container config
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
├── scripts/               # Utility scripts
│   ├── mongo-init.js      # MongoDB initialization
│   ├── migrate_postgres_to_mongodb.py # Migration script
│   └── test_qa_bot.py     # Test script
├── test_documents/        # Sample documents for testing
│   ├── ai_ml_overview.txt
│   ├── docker_guide.txt
│   ├── python_best_practices.txt
│   └── README.md
├── docker-compose.yml     # Orchestration config
├── env.template           # Environment template
├── setup.sh              # Setup script
└── README.md
```

## 🔧 Features

### Core Functionality

- **Document Upload**: Support for .txt and .pdf files
- **Text Chunking**: Automatic document splitting with configurable size and overlap
- **Vector Embeddings**: Generate embeddings using OpenAI API (text-embedding-3-small)
- **Vector Database**: Qdrant for high-performance similarity search
- **Metadata Storage**: MongoDB for document metadata and user data
- **Semantic Search**: Query documents using natural language
- **User Management**: User-specific document isolation
- **Query Logging**: Track and analyze user queries

### Technical Features

- **Backend**: FastAPI with async/await support
- **Frontend**: React with TypeScript and hot-reloading
- **Database**: MongoDB with proper indexing
- **Vector Database**: Qdrant with cosine similarity
- **Embeddings**: OpenAI API integration
- **Docker**: Fully containerized development environment
- **CORS**: Configured for cross-origin requests
- **Type Safety**: Full TypeScript support in frontend
- **API Documentation**: Interactive Swagger UI
- **Health Checks**: Service monitoring and status endpoints

## 🗄️ Database Architecture

### MongoDB Collections

```javascript
// Documents collection
{
  "_id": ObjectId,
  "user_id": "string",
  "filename": "string",
  "original_filename": "string",
  "file_type": "string",
  "file_size": "number",
  "status": "uploaded|processing|completed|failed",
  "total_chunks": "number",
  "total_tokens": "number",
  "processing_time": "number",
  "created_at": "datetime",
  "updated_at": "datetime",
  "metadata": "object"
}

// Chunks collection
{
  "_id": ObjectId,
  "document_id": ObjectId,
  "user_id": "string",
  "chunk_index": "number",
  "text_chunk": "string",
  "chunk_size": "number",
  "token_count": "number",
  "created_at": "datetime",
  "metadata": "object"
}

// Queries collection
{
  "_id": ObjectId,
  "user_id": "string",
  "query_text": "string",
  "results_count": "number",
  "processing_time": "number",
  "created_at": "datetime",
  "metadata": "object"
}
```

### Qdrant Vector Database

- **Collection**: `qa_bot_embeddings`
- **Vector Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Distance Metric**: Cosine similarity
- **Payload**: Document metadata for filtering and display

## 🔌 API Endpoints

### Document Management

- `POST /api/upload` - Upload documents
- `GET /api/documents/{user_id}` - Get user documents
- `DELETE /api/documents/{user_id}/{document_id}` - Delete document

### Query Interface

- `POST /api/query` - Query documents
- `GET /api/stats` - Get system statistics
- `GET /health` - Health check

### Example API Usage

```bash
# Upload a document
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_documents/ai_ml_overview.txt" \
  -F "user_id=test_user"

# Query documents
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "user_id": "test_user",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'

# Get system stats
curl -X GET "http://localhost:8000/stats"
```

## 🧪 Testing

### Automated Testing

Run the comprehensive test script:

```bash
python scripts/test_qa_bot.py
```

This script will:

- Test API health
- Upload sample documents
- Test various queries
- Verify system functionality

### Manual Testing

1. **Upload Documents**: Use the web interface or API
2. **Test Queries**: Try different types of questions
3. **Check Results**: Verify relevance and accuracy
4. **Monitor Performance**: Check response times and resource usage

## 🔄 Migration from PostgreSQL

If you have existing data in PostgreSQL, use the migration script:

```bash
python scripts/migrate_postgres_to_mongodb.py
```

This script will:

- Connect to PostgreSQL and extract data
- Transform data to MongoDB format
- Store embeddings in Qdrant
- Verify migration success

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `MONGODB_URL` - MongoDB connection string (auto-configured)
- `QDRANT_URL` - Qdrant connection string (auto-configured)
- `PYTHONPATH=/app` - Python path for the backend
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `CHOKIDAR_USEPOLLING=true` - File watching for frontend
- `REACT_APP_API_URL=http://localhost:8000` - API URL for frontend

### Database Configuration

- **MongoDB**: Port 27017, Database: qa_bot, Username: admin, Password: password123
- **Qdrant**: Port 6333, Collection: qa_bot_embeddings
- **Embedding Model**: text-embedding-3-small (1536 dimensions)

## 🚀 Production Deployment

### Docker Compose

The system is designed to run with a single command:

```bash
docker-compose up -d
```

### Scaling Considerations

- **MongoDB**: Use replica sets for high availability
- **Qdrant**: Use cluster mode for large-scale deployments
- **Backend**: Use multiple replicas behind a load balancer
- **Frontend**: Use CDN for static assets

### Monitoring

- **Health Checks**: Built-in health endpoints
- **Logging**: Structured logging with different levels
- **Metrics**: Track query performance and system usage
- **Alerts**: Set up monitoring for service failures

## 🔒 Security Considerations

- **API Keys**: Store securely in environment variables
- **Input Validation**: All inputs are validated and sanitized
- **User Isolation**: Data is properly isolated by user_id
- **Rate Limiting**: Consider implementing rate limiting for production
- **Authentication**: Add authentication layer for production use

## 🛠️ Development

### Backend Development

The FastAPI backend runs on port 8000 with auto-reload enabled. Any changes to Python files will automatically restart the server.

### Frontend Development

The React frontend runs on port 3000 with hot-reloading enabled. Any changes to TypeScript/CSS files will automatically refresh the browser.

### Database Development

- **MongoDB**: Use MongoDB Compass for database management
- **Qdrant**: Use Qdrant dashboard at http://localhost:6333/dashboard

## 📊 Performance Considerations

- **Embedding Model**: text-embedding-3-small balances speed and quality
- **Chunk Size**: 500 tokens provides good context while maintaining performance
- **Vector Search**: Qdrant provides sub-millisecond search times
- **Database Indexing**: Proper indexes on user_id, document_name, and timestamps
- **Caching**: Consider implementing Redis for query result caching

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `OPENAI_API_KEY` is set in your `.env` file
2. **Database Connection**: Check if MongoDB and Qdrant containers are running
3. **Port Conflicts**: Ensure ports 3000, 8000, 27017, and 6333 are available
4. **API Rate Limits**: OpenAI API has rate limits; consider upgrading if needed
5. **Memory Issues**: Ensure sufficient RAM for all services

### Debugging

```bash
# Check service logs
docker-compose logs -f backend
docker-compose logs -f mongodb
docker-compose logs -f qdrant
docker-compose logs -f frontend

# Check service health
curl http://localhost:8000/health

# Check database connections
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
curl http://localhost:6333/health

# Check system stats
curl http://localhost:8000/stats
```

## 🔮 Future Enhancements

- **Authentication**: Add user authentication and authorization
- **Advanced Chunking**: Implement semantic chunking strategies
- **More File Types**: Support for docx, html, markdown, etc.
- **Fine-tuning**: Custom embedding model fine-tuning
- **Analytics**: Query analytics and insights dashboard
- **Versioning**: Document versioning and updates
- **Batch Processing**: Large document collection processing
- **Multi-language**: Support for multiple languages

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs -f`
3. Verify your OpenAI API key is valid
4. Ensure all required ports are available
5. Check the API documentation at http://localhost:8000/docs

## 🛑 Stopping the Application

```bash
docker-compose down
```

To remove all data:

```bash
docker-compose down -v
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using FastAPI, React, MongoDB, Qdrant, and OpenAI**

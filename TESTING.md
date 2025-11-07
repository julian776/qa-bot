# Testing Guide - QA Bot with Multi-Language Support

This guide provides instructions for testing the complete QA Bot system with multi-language support (English/Spanish).

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- `jq` installed for JSON parsing (optional but recommended)

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Start all services:**
   ```bash
   docker compose up --build
   ```

3. **Wait for services to be ready:**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - Qdrant Dashboard: http://localhost:6333/dashboard

4. **Run automated tests:**
   ```bash
   ./test_flow.sh
   ```

## Manual Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_store": {
    "total_vectors": 0,
    "embedding_dimension": 1536,
    "collection_name": "qa_bot_embeddings"
  },
  "mongodb": {
    "connected": true
  }
}
```

### 2. Upload Documents

**English Document:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@samples/test_en.txt" \
  -F "user_id=test_user"
```

**Spanish Document:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@samples/test_es.txt" \
  -F "user_id=test_user"
```

Expected response:
```json
{
  "user_id": "test_user",
  "document_name": "test_en.txt",
  "total_chunks": 5,
  "total_tokens": 450,
  "processing_time": 1.234,
  "status": "success"
}
```

### 3. Create Session

```bash
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user"}'
```

Expected response:
```json
{
  "session_id": "uuid-here",
  "user_id": "test_user",
  "created_at": "2025-11-06T21:00:00"
}
```

### 4. Query with LLM (English)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?",
    "session_id": "your-session-id",
    "user_id": "test_user",
    "top_k": 5
  }'
```

Expected response:
```json
{
  "session_id": "uuid-here",
  "prompt": "What is machine learning?",
  "answer": "Machine learning is a branch of artificial intelligence...",
  "language": "en",
  "sources": [
    {
      "text_chunk": "Machine learning is...",
      "document_name": "test_en.txt",
      "chunk_index": 0,
      "score": 0.95,
      "metadata": {"language": "en"}
    }
  ],
  "processing_time": 2.345
}
```

### 5. Query with LLM (Spanish)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Qué es la inteligencia artificial?",
    "session_id": "your-session-id",
    "user_id": "test_user",
    "top_k": 5
  }'
```

Expected response includes Spanish answer with Spanish sources.

### 6. Get Session Messages

```bash
curl http://localhost:8000/api/session/{session_id}/messages
```

Expected response:
```json
{
  "session_id": "uuid-here",
  "messages": [
    {
      "role": "user",
      "content": "What is machine learning?",
      "language": "en",
      "sources": null,
      "created_at": "2025-11-06T21:00:00"
    },
    {
      "role": "assistant",
      "content": "Machine learning is...",
      "language": "en",
      "sources": [...],
      "created_at": "2025-11-06T21:00:01"
    }
  ],
  "total_messages": 2
}
```

### 7. Get User Sessions

```bash
curl http://localhost:8000/api/sessions/test_user
```

### 8. Admin Endpoints

**Get System Stats:**
```bash
curl http://localhost:8000/api/admin/stats
```

**Clear All Data:**
```bash
curl -X POST http://localhost:8000/api/admin/clear
```

**Clear User Data:**
```bash
curl -X POST http://localhost:8000/api/admin/clear/user/test_user
```

## Testing Language Detection

The system automatically detects the language of:
1. Uploaded documents (stored in metadata)
2. User queries (used for filtering)

**Test Language Detection:**

1. Upload English document → should detect "en"
2. Upload Spanish document → should detect "es"
3. Query in English → should search only English documents
4. Query in Spanish → should search only Spanish documents

## Testing Chat History

1. Create a session
2. Send multiple queries with the same session_id
3. Retrieve messages using `/api/session/{session_id}/messages`
4. Verify all messages are saved with correct roles and timestamps

## Verifying Data Stores

### MongoDB

```bash
# Connect to MongoDB
docker exec -it qa-bot-mongodb mongosh -u admin -p password123 --authenticationDatabase admin

# Switch to qa_bot database
use qa_bot

# Check collections
show collections

# Count documents
db.documents.countDocuments()
db.chunks.countDocuments()
db.sessions.countDocuments()
db.messages.countDocuments()

# View sample session
db.sessions.findOne()

# View sample messages
db.messages.find().limit(5)
```

### Qdrant

1. Open http://localhost:6333/dashboard
2. Check collection "qa_bot_embeddings"
3. Verify vectors are stored with language metadata
4. Test vector search in the UI

## Common Issues

### Issue: "OPENAI_API_KEY not set"
**Solution:** Make sure you've created `.env` file with your API key

### Issue: "MongoDB connection failed"
**Solution:** Wait for MongoDB to fully start (check with `docker compose logs mongodb`)

### Issue: "Qdrant connection failed"
**Solution:** Verify Qdrant is running (`docker compose ps`)

### Issue: "Language detection returns wrong language"
**Solution:** Ensure document has enough text for accurate detection (at least a few sentences)

## Performance Benchmarks

Expected performance on typical hardware:

- Document upload (1 page PDF): 1-3 seconds
- Query with LLM response: 2-5 seconds
- Language detection: < 0.1 seconds
- Vector search: < 0.5 seconds

## API Documentation

Full interactive API documentation is available at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Logs

View service logs:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f mongodb
docker compose logs -f qdrant
```

## Stopping Services

```bash
# Stop services
docker compose down

# Stop and remove volumes (deletes all data)
docker compose down -v
```

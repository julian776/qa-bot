# Deployment Guide - Chat & Document History Management Updates

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (running locally or remote)
- Qdrant (running locally or remote)
- OpenAI API key

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Make sure your `.env` file has all required variables:

```bash
# .env
OPENAI_API_KEY=your_api_key_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=qa_bot
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=documents
```

### 3. Database Migration (Optional)

If you have existing data, no migration is needed! The new fields are optional:
- `Session.title` defaults to `None`
- `Session.document_ids` defaults to `[]`

Your existing sessions will work without modification.

### 4. Start the Backend

```bash
# Development
cd backend
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify Backend

Test the new endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Test session creation
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'

# Test session listing
curl http://localhost:8000/api/sessions/default_user
```

## Frontend Deployment

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Update `frontend/.env` if needed:

```bash
VITE_API_BASE=http://localhost:8000
```

For production:

```bash
VITE_API_BASE=https://your-backend-domain.com
```

### 3. Development Server

```bash
cd frontend
npm run dev
```

Access at: `http://localhost:5173`

### 4. Production Build

```bash
cd frontend
npm run build

# Serve the dist folder with your preferred web server
# Example with serve:
npx serve -s dist -p 3000
```

## Testing the New Features

### 1. Session Management

#### Create a Session
```bash
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default_user"}'
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "default_user",
  "created_at": "2025-11-07T12:00:00"
}
```

#### Rename a Session
```bash
SESSION_ID="your-session-id"

curl -X PATCH http://localhost:8000/api/session/$SESSION_ID/title \
  -H "Content-Type: application/json" \
  -d '{"title": "My Important Chat"}'
```

#### Delete a Session
```bash
curl -X DELETE http://localhost:8000/api/session/$SESSION_ID
```

Response:
```json
{
  "success": true,
  "session_id": "550e8400-...",
  "messages_deleted": 10,
  "session_deleted": true
}
```

### 2. Document Management

#### Upload Document with Session Link
```bash
SESSION_ID="your-session-id"

curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_document.pdf" \
  -F "user_id=default_user" \
  -F "session_id=$SESSION_ID"
```

#### Get Session Documents
```bash
curl http://localhost:8000/api/session/$SESSION_ID/documents
```

Response:
```json
{
  "session_id": "550e8400-...",
  "documents": [
    {
      "id": "doc123",
      "filename": "test_document.pdf",
      "original_filename": "test_document.pdf",
      "file_type": ".pdf",
      "file_size": 102400,
      "status": "completed",
      "total_chunks": 45,
      "created_at": "2025-11-07T12:00:00"
    }
  ],
  "total_documents": 1
}
```

#### Delete a Document
```bash
DOCUMENT_ID="doc123"

curl -X DELETE http://localhost:8000/api/document/$DOCUMENT_ID
```

### 3. Frontend Testing

Open `http://localhost:5173` and test:

1. **Create New Chat**
   - Click "+ Nuevo" button
   - Verify new chat appears in sidebar

2. **Upload Document**
   - Select or create a chat
   - Click attachment button
   - Upload a PDF or TXT file
   - Verify document is linked (📎 badge appears)

3. **Rename Chat**
   - Double-click on chat title in sidebar
   - OR click the ✏️ edit button
   - Type new name and press Enter
   - Verify name updates immediately

4. **View Documents**
   - Click "📎 Documentos" button in topbar
   - Document panel slides in from right
   - Verify documents for current session appear

5. **Delete Document**
   - In documents panel, click 🗑️ on a document
   - Confirm deletion
   - Verify document removed from panel and badge updated

6. **Delete Chat**
   - Click 🗑️ button on chat in sidebar
   - Confirm deletion
   - Verify chat removed from sidebar
   - If active chat, verify view clears

## Troubleshooting

### Backend Issues

**Issue: ModuleNotFoundError**
```bash
# Solution: Install dependencies
cd backend
pip install -r requirements.txt
```

**Issue: MongoDB connection failed**
```bash
# Solution: Start MongoDB
# macOS with Homebrew:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod

# Verify connection:
mongosh
```

**Issue: Qdrant connection failed**
```bash
# Solution: Start Qdrant
# Using Docker:
docker run -p 6333:6333 qdrant/qdrant

# Verify connection:
curl http://localhost:6333/collections
```

**Issue: "Session not found" when deleting**
```bash
# Solution: Verify session exists
curl http://localhost:8000/api/sessions/default_user

# Check session_id is correct (not conversationId from frontend)
```

### Frontend Issues

**Issue: API calls failing**
```bash
# Check VITE_API_BASE in .env
# Verify backend is running
curl http://localhost:8000/health

# Check browser console for CORS errors
# Ensure backend has CORS enabled (should be in main.py)
```

**Issue: Rename not persisting**
```bash
# Check browser console for errors
# Verify PATCH endpoint working:
curl -X PATCH http://localhost:8000/api/session/SESSION_ID/title \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```

**Issue: Document count not updating**
```bash
# Refresh the page (localStorage sync)
# OR click on another chat and back

# Verify document is linked in backend:
curl http://localhost:8000/api/session/SESSION_ID/documents
```

## Database Schema Reference

### Sessions Collection
```javascript
{
  _id: ObjectId("..."),
  session_id: "uuid-string",
  user_id: "default_user",
  title: "My Chat" | null,  // NEW
  document_ids: ["doc1", "doc2"],  // NEW
  created_at: ISODate("..."),
  updated_at: ISODate("..."),
  message_count: 10
}
```

### Messages Collection
```javascript
{
  _id: ObjectId("..."),
  session_id: "uuid-string",
  role: "user" | "assistant",
  content: "message text",
  language: "en" | "es" | null,
  sources: [{ text_chunk: "...", document_name: "...", ... }],
  created_at: ISODate("...")
}
```

### Documents Collection
```javascript
{
  _id: ObjectId("..."),
  user_id: "default_user",
  filename: "document.pdf",
  original_filename: "document.pdf",
  file_type: ".pdf",
  file_size: 102400,
  status: "completed",
  total_chunks: 45,
  total_tokens: 2000,
  processing_time: 2.5,
  created_at: ISODate("..."),
  updated_at: ISODate("..."),
  metadata: { language: "en" }
}
```

### Chunks Collection
```javascript
{
  _id: ObjectId("..."),
  document_id: "doc-id",
  user_id: "default_user",
  chunk_index: 0,
  text_chunk: "content...",
  chunk_size: 512,
  token_count: 128,
  created_at: ISODate("..."),
  metadata: {}
}
```

## Performance Monitoring

### Backend Metrics

Check endpoint performance:
```bash
# Session operations
time curl http://localhost:8000/api/sessions/default_user

# Document operations
time curl http://localhost:8000/api/session/SESSION_ID/documents

# Delete operations
time curl -X DELETE http://localhost:8000/api/session/SESSION_ID
```

### Database Queries

Monitor slow queries in MongoDB:
```javascript
// Enable profiling
db.setProfilingLevel(2)

// Check slow queries
db.system.profile.find().sort({ts: -1}).limit(10)

// Add indexes for better performance
db.sessions.createIndex({ user_id: 1, updated_at: -1 })
db.documents.createIndex({ user_id: 1, created_at: -1 })
db.messages.createIndex({ session_id: 1, created_at: 1 })
```

## Backup and Recovery

### MongoDB Backup
```bash
# Backup all collections
mongodump --db qa_bot --out /backup/qa_bot_backup

# Restore
mongorestore --db qa_bot /backup/qa_bot_backup/qa_bot
```

### Qdrant Backup
```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/documents/snapshots

# List snapshots
curl http://localhost:6333/collections/documents/snapshots

# Download snapshot
curl http://localhost:6333/collections/documents/snapshots/SNAPSHOT_NAME \
  --output snapshot.tar
```

## Production Checklist

- [ ] Backend running with production WSGI server (gunicorn/uvicorn)
- [ ] Frontend built and served via nginx/CDN
- [ ] MongoDB with authentication enabled
- [ ] Qdrant with API key protection
- [ ] Environment variables secured (not in code)
- [ ] HTTPS enabled for API and frontend
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring setup (Sentry, DataDog, etc.)
- [ ] Backups automated
- [ ] Health checks configured
- [ ] Documentation updated

## Support

For issues or questions:
1. Check the logs: `backend/logs/` or browser console
2. Review the implementation summary: `IMPLEMENTATION_SUMMARY.md`
3. Test individual endpoints with curl
4. Check database state with mongosh
5. Verify environment variables are set correctly

## Next Steps

After deployment, consider:
1. Setting up automated tests
2. Implementing pagination for large datasets
3. Adding user authentication
4. Implementing role-based access control
5. Adding analytics and usage tracking
6. Setting up CI/CD pipeline

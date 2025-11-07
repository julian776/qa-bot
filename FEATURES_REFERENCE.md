# Quick Reference - New Features

## 🎯 What's New

### ✅ Complete Session Management
- Delete sessions (backend + frontend sync)
- Rename sessions (inline editing)
- View session details
- Track documents per session

### ✅ Complete Document Management
- Upload documents to sessions
- View documents per session
- Delete specific documents
- Document metadata display

### ✅ Better UX
- Document count badges on sessions
- Inline rename (double-click or button)
- Document panel (toggle on/off)
- Confirmation modals for safety

---

## 🎨 User Interface Guide

### Session Sidebar

```
┌─────────────────────────────┐
│ Historial      [+ Nuevo]    │
├─────────────────────────────┤
│ 📝 My Chat 📎 2      ✏️ 🗑️  │  ← Double-click title to edit
│    2025-11-07 12:30         │
├─────────────────────────────┤
│ 📝 Session abcd1234  ✏️ 🗑️  │
│    2025-11-06 10:15         │
└─────────────────────────────┘

Legend:
📎 2    = 2 documents linked
✏️      = Edit button
🗑️      = Delete button
```

### Document Panel

```
┌─────────────────────────────┐
│ Documentos            [✕]   │
├─────────────────────────────┤
│ 📄 document.pdf             │
│    45 chunks • .pdf • 100KB │
│    2025-11-07 12:00   [🗑️]  │
├─────────────────────────────┤
│ 📄 notes.txt                │
│    10 chunks • .txt • 5KB   │
│    2025-11-07 11:30   [🗑️]  │
└─────────────────────────────┘
```

### Top Bar

```
┌──────────────────────────────────────────┐
│ 🤖 Interfaz de Chat  [📎 Documentos] [🌙] │
└──────────────────────────────────────────┘

Buttons:
📎 Documentos = Toggle document panel
🌙           = Dark mode toggle
```

---

## ⌨️ Keyboard Shortcuts

### Rename Session
1. **Double-click** on session title
2. **OR** click ✏️ edit button
3. Type new name
4. Press **Enter** to save
5. Press **Escape** to cancel

### Navigate
- Click session to open
- Click 🗑️ to delete (with confirmation)
- Click "📎 Documentos" to show/hide panel

---

## 🔌 API Quick Reference

### Sessions

| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| Create | POST | `/api/session/create` | `{"user_id": "..."}` |
| List | GET | `/api/sessions/{user_id}` | - |
| Delete | DELETE | `/api/session/{session_id}` | - |
| Rename | PATCH | `/api/session/{session_id}/title` | `{"title": "..."}` |
| Get Docs | GET | `/api/session/{session_id}/documents` | - |
| Get Messages | GET | `/api/session/{session_id}/messages` | - |

### Documents

| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| Upload | POST | `/api/upload` | `FormData(file, user_id, session_id?)` |
| List | GET | `/api/documents/{user_id}` | - |
| Delete | DELETE | `/api/document/{document_id}` | - |
| Delete All | DELETE | `/api/documents/{user_id}` | - |

### Messages

| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| Query | POST | `/api/query` | `{"prompt": "...", "session_id": "...", ...}` |

---

## 💡 Usage Examples

### Example 1: Create Session and Upload Document

```bash
# 1. Create session
SESSION_ID=$(curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default_user"}' | jq -r '.session_id')

# 2. Upload document to session
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf" \
  -F "user_id=default_user" \
  -F "session_id=$SESSION_ID"

# 3. Rename session
curl -X PATCH http://localhost:8000/api/session/$SESSION_ID/title \
  -H "Content-Type: application/json" \
  -d '{"title": "My Document Chat"}'

# 4. View documents
curl http://localhost:8000/api/session/$SESSION_ID/documents
```

### Example 2: Frontend Usage

```javascript
// Create session
const { conversationId } = await api.newConversation();

// Upload files to session
await api.uploadFiles(files, conversationId);

// Rename session
await api.renameConversation(conversationId, "New Title");

// Get session documents
const docs = await api.getSessionDocuments(conversationId);

// Delete session
await api.deleteConversation(conversationId);

// Delete document
await api.deleteDocument(documentId);
```

---

## 📊 Data Model

### Session
```typescript
interface Session {
  session_id: string;
  user_id: string;
  title?: string;              // NEW
  document_ids: string[];      // NEW
  created_at: Date;
  updated_at: Date;
  message_count: number;
}
```

### Document
```typescript
interface Document {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  total_chunks: number;
  total_tokens: number;
  processing_time?: number;
  created_at: Date;
  updated_at: Date;
  metadata?: {
    language?: string;
  };
}
```

---

## 🔍 Common Tasks

### How to rename a chat?
1. **Option A**: Double-click the chat title in sidebar
2. **Option B**: Click the ✏️ edit button
3. Type new name
4. Press Enter or click outside to save

### How to see documents in a chat?
1. Click the "📎 Documentos" button in the top bar
2. Document panel slides in from the right
3. Shows all documents linked to current session

### How to upload a document?
1. Open or create a chat
2. Click the 📎 attachment button at bottom
3. Select file(s)
4. Type a message and send
5. Document will be automatically linked to the session

### How to delete a chat?
1. Click the 🗑️ button next to the chat in sidebar
2. Confirm deletion in the modal
3. Chat and all messages are deleted from backend

### How to delete a document?
1. Open the document panel (📎 Documentos button)
2. Click 🗑️ button next to the document
3. Confirm deletion
4. Document is removed from all sessions and backend

---

## ⚠️ Important Notes

### Deletion Behavior
- **Delete Session**: Deletes the session AND all its messages (permanent)
- **Delete Document**: Deletes the document from ALL sessions and backend (permanent)
- **Delete All Documents**: Deletes all documents for a user (permanent)

### Confirmation Modals
Always appear for:
- ✅ Deleting a session
- ✅ Deleting a document
- ✅ Deleting all documents

### Auto-Linking
When you upload a file while in a session:
- ✅ File is processed and saved
- ✅ Document ID is added to session's `document_ids`
- ✅ Document count badge updates automatically

### Session Titles
- Default: `"Session {first-8-chars-of-uuid}"`
- Custom: Whatever you set via rename
- Empty: Falls back to default format

---

## 🎓 Best Practices

### For Users
1. **Name your chats**: Give meaningful titles for easy navigation
2. **Link documents**: Upload files during chat for better tracking
3. **Clean up**: Delete old chats/documents you no longer need
4. **Check documents**: Use document panel to verify what's linked

### For Developers
1. **Always link documents**: Pass `session_id` when uploading
2. **Handle errors**: All API calls can fail, handle gracefully
3. **Update UI**: Refresh session list after operations
4. **Confirm deletions**: Always ask user to confirm destructive actions

---

## 🐛 Quick Troubleshooting

### "Session not found"
- Make sure you're using `session_id` not `conversationId`
- Check session exists: `GET /api/sessions/{user_id}`

### Document count not updating
- Refresh the page
- Click on another chat and back
- Check backend: `GET /api/session/{session_id}/documents`

### Rename not working
- Check browser console for errors
- Verify backend is running
- Test endpoint: `PATCH /api/session/{session_id}/title`

### Delete not working
- Check browser console for errors
- Verify you confirmed the modal
- Test endpoint: `DELETE /api/session/{session_id}`

---

## 📚 Related Documentation

- `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `DEPLOYMENT_GUIDE.md` - Deployment and testing guide
- `README.md` - Project overview and setup
- `TESTING.md` - Testing documentation

---

## 🆘 Need Help?

1. Check the browser console for frontend errors
2. Check backend logs for API errors
3. Test endpoints individually with curl
4. Verify MongoDB and Qdrant are running
5. Check environment variables are set
6. Review the deployment guide

---

## ✨ Feature Highlights

### Before
- ❌ Deletes only happened in localStorage
- ❌ No way to rename chats
- ❌ No document management UI
- ❌ No way to know which docs are in which chat
- ❌ Inconsistent state between frontend and backend

### After
- ✅ Full CRUD for sessions (backend sync)
- ✅ Inline rename with keyboard support
- ✅ Dedicated document management panel
- ✅ Visual badges showing document counts
- ✅ Complete state consistency
- ✅ Confirmation modals for safety
- ✅ Auto-linking of documents to sessions

---

**Last Updated**: 2025-11-07
**Version**: 1.0.0

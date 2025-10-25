# Test Documents

This directory contains sample documents for testing the embeddings database functionality.

## Available Test Files

- `sample.txt` - A comprehensive description of the QA Bot system
- `README.md` - This file

## How to Test

1. Start the system: `make setup`
2. Upload a document:

   ```bash
   curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample.txt" \
     -F "user_id=test_user"
   ```

3. Query the documents:

   ```bash
   curl -X POST "http://localhost:8000/api/query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the technical stack?", "user_id": "test_user", "top_k": 3}'
   ```

4. Or use the convenient test command: `make test`

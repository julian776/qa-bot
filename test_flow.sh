#!/bin/bash

# Test script for QA Bot with multi-language support
# This script tests the complete flow of the application

set -e

API_URL="http://localhost:8000"
USER_ID="test_user"
SESSION_ID=""

echo "============================================"
echo "QA Bot Multi-Language Test Script"
echo "============================================"
echo ""

# Check if backend is running
echo "1. Checking backend health..."
curl -s "${API_URL}/health" | jq '.'
echo ""

# Clear all data for clean test
echo "2. Clearing all data..."
curl -s -X POST "${API_URL}/api/admin/clear" | jq '.'
echo ""

# Upload English document
echo "3. Uploading English document..."
curl -s -X POST "${API_URL}/api/upload" \
  -F "file=@samples/test_en.txt" \
  -F "user_id=${USER_ID}" | jq '.'
echo ""

# Upload Spanish document
echo "4. Uploading Spanish document..."
curl -s -X POST "${API_URL}/api/upload" \
  -F "file=@samples/test_es.txt" \
  -F "user_id=${USER_ID}" | jq '.'
echo ""

# Create a new session
echo "5. Creating new session..."
SESSION_RESPONSE=$(curl -s -X POST "${API_URL}/api/session/create" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"${USER_ID}\"}")
echo "$SESSION_RESPONSE" | jq '.'
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
echo ""

# Query in English
echo "6. Querying in English..."
curl -s -X POST "${API_URL}/api/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"What is machine learning?\",
    \"session_id\": \"${SESSION_ID}\",
    \"user_id\": \"${USER_ID}\",
    \"top_k\": 3
  }" | jq '.'
echo ""

# Query in Spanish
echo "7. Querying in Spanish..."
curl -s -X POST "${API_URL}/api/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"¿Qué es la inteligencia artificial?\",
    \"session_id\": \"${SESSION_ID}\",
    \"user_id\": \"${USER_ID}\",
    \"top_k\": 3
  }" | jq '.'
echo ""

# Get session messages
echo "8. Getting session messages..."
curl -s "${API_URL}/api/session/${SESSION_ID}/messages" | jq '.'
echo ""

# Get user sessions
echo "9. Getting all user sessions..."
curl -s "${API_URL}/api/sessions/${USER_ID}" | jq '.'
echo ""

# Get system stats
echo "10. Getting system statistics..."
curl -s "${API_URL}/api/admin/stats" | jq '.'
echo ""

echo "============================================"
echo "Test completed successfully!"
echo "============================================"

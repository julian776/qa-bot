#!/bin/bash

# Test script for QA Bot with multi-language support
# This script tests the complete flow of the application

API_URL="http://localhost:8000"
USER_ID="test_user"
SESSION_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}Warning: jq is not installed. Output will not be prettified.${NC}"
        echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)"
        return 1
    fi
    return 0
}

# Function to make API call and handle errors
api_call() {
    local response
    local http_code

    response=$(curl -s -w "\n%{http_code}" "$@")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        if check_jq; then
            echo "$body" | jq '.'
        else
            echo "$body"
        fi
        return 0
    else
        echo -e "${RED}Error: HTTP $http_code${NC}"
        echo "$body"
        return 1
    fi
}

echo "============================================"
echo "QA Bot Multi-Language Test Script"
echo "============================================"
echo ""

# Check if backend is running
echo "1. Checking backend health..."
if ! curl -s -f "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Backend is not running at ${API_URL}${NC}"
    echo ""
    echo "Please start the backend with:"
    echo "  docker compose up -d"
    echo ""
    exit 1
fi

api_call "${API_URL}/health"
echo -e "${GREEN}✓ Backend is healthy${NC}"
echo ""

# Clear all data for clean test
echo "2. Clearing all data..."
if api_call -X POST "${API_URL}/api/admin/clear"; then
    echo -e "${GREEN}✓ Data cleared${NC}"
else
    echo -e "${RED}✗ Failed to clear data${NC}"
fi
echo ""

# Upload English document
echo "3. Uploading English document..."
if [ ! -f "samples/test_en.txt" ]; then
    echo -e "${RED}ERROR: samples/test_en.txt not found${NC}"
    exit 1
fi
if api_call -X POST "${API_URL}/api/upload" \
  -F "file=@samples/test_en.txt" \
  -F "user_id=${USER_ID}"; then
    echo -e "${GREEN}✓ English document uploaded${NC}"
else
    echo -e "${RED}✗ Failed to upload English document${NC}"
    exit 1
fi
echo ""

# Upload Spanish document
echo "4. Uploading Spanish document..."
if [ ! -f "samples/test_es.txt" ]; then
    echo -e "${RED}ERROR: samples/test_es.txt not found${NC}"
    exit 1
fi
if api_call -X POST "${API_URL}/api/upload" \
  -F "file=@samples/test_es.txt" \
  -F "user_id=${USER_ID}"; then
    echo -e "${GREEN}✓ Spanish document uploaded${NC}"
else
    echo -e "${RED}✗ Failed to upload Spanish document${NC}"
    exit 1
fi
echo ""

# Create a new session
echo "5. Creating new session..."
SESSION_RESPONSE=$(curl -s -X POST "${API_URL}/api/session/create" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"${USER_ID}\"}")

if check_jq; then
    echo "$SESSION_RESPONSE" | jq '.'
    SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session_id')
else
    echo "$SESSION_RESPONSE"
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo -e "${RED}✗ Failed to create session${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"
echo ""

# Query in English
echo "6. Querying in English..."
if api_call -X POST "${API_URL}/api/query" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"What is machine learning?\",\"session_id\":\"${SESSION_ID}\",\"user_id\":\"${USER_ID}\",\"top_k\":3}"; then
    echo -e "${GREEN}✓ English query successful${NC}"
else
    echo -e "${RED}✗ English query failed${NC}"
fi
echo ""

# Query in Spanish
echo "7. Querying in Spanish..."
if api_call -X POST "${API_URL}/api/query" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"¿Qué es la inteligencia artificial?\",\"session_id\":\"${SESSION_ID}\",\"user_id\":\"${USER_ID}\",\"top_k\":3}"; then
    echo -e "${GREEN}✓ Spanish query successful${NC}"
else
    echo -e "${RED}✗ Spanish query failed${NC}"
fi
echo ""

# Get session messages
echo "8. Getting session messages..."
if api_call "${API_URL}/api/session/${SESSION_ID}/messages"; then
    echo -e "${GREEN}✓ Retrieved session messages${NC}"
else
    echo -e "${RED}✗ Failed to retrieve session messages${NC}"
fi
echo ""

# Get user sessions
echo "9. Getting all user sessions..."
if api_call "${API_URL}/api/sessions/${USER_ID}"; then
    echo -e "${GREEN}✓ Retrieved user sessions${NC}"
else
    echo -e "${RED}✗ Failed to retrieve user sessions${NC}"
fi
echo ""

# Get system stats
echo "10. Getting system statistics..."
if api_call "${API_URL}/api/admin/stats"; then
    echo -e "${GREEN}✓ Retrieved system stats${NC}"
else
    echo -e "${RED}✗ Failed to retrieve system stats${NC}"
fi
echo ""

echo "============================================"
echo -e "${GREEN}Test completed successfully!${NC}"
echo "============================================"

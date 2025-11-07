#!/bin/bash

# QA Bot - Setup Verification Script
# This script verifies that all components are properly configured

echo "🔍 QA Bot Setup Verification"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0

check_pass() {
  echo -e "${GREEN}✓${NC} $1"
  ((PASS++))
}

check_fail() {
  echo -e "${RED}✗${NC} $1"
  ((FAIL++))
}

check_warn() {
  echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Docker
echo "1️⃣  Checking Docker..."
if command -v docker &> /dev/null; then
  check_pass "Docker is installed"
  if docker info &> /dev/null; then
    check_pass "Docker daemon is running"
  else
    check_fail "Docker daemon is not running"
  fi
else
  check_fail "Docker is not installed"
fi
echo ""

# 2. Check environment files
echo "2️⃣  Checking environment files..."
if [ -f ".env" ]; then
  check_pass "Backend .env exists"
  if grep -q "OPENAI_API_KEY=sk-" .env; then
    check_pass "OpenAI API key is configured"
  else
    check_fail "OpenAI API key not found in .env"
  fi
else
  check_fail "Backend .env file missing"
fi

if [ -f "frontend/.env" ]; then
  check_pass "Frontend .env exists"
  if grep -q "VITE_API_BASE" frontend/.env; then
    check_pass "VITE_API_BASE is configured"
  else
    check_fail "VITE_API_BASE not found in frontend/.env"
  fi
else
  check_fail "Frontend .env file missing (should be created)"
fi
echo ""

# 3. Check if containers are running
echo "3️⃣  Checking Docker containers..."
if docker ps | grep -q "qa-bot-backend"; then
  check_pass "Backend container is running"
else
  check_warn "Backend container not running (run: docker-compose up)"
fi

if docker ps | grep -q "qa-bot-frontend"; then
  check_pass "Frontend container is running"
else
  check_warn "Frontend container not running (run: docker-compose up)"
fi

if docker ps | grep -q "qa-bot-mongodb"; then
  check_pass "MongoDB container is running"
else
  check_warn "MongoDB container not running (run: docker-compose up)"
fi

if docker ps | grep -q "qa-bot-qdrant"; then
  check_pass "Qdrant container is running"
else
  check_warn "Qdrant container not running (run: docker-compose up)"
fi
echo ""

# 4. Check backend health
echo "4️⃣  Checking backend health..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  HEALTH=$(curl -s http://localhost:8000/api/health)
  if echo "$HEALTH" | grep -q '"status":"ok"'; then
    check_pass "Backend health check passed"
    echo "   Response: $HEALTH"
  else
    check_fail "Backend health check failed"
    echo "   Response: $HEALTH"
  fi
else
  check_warn "Backend not reachable at http://localhost:8000"
fi
echo ""

# 5. Check CORS configuration
echo "5️⃣  Checking CORS configuration..."
if grep -q "allow_origins=\[" backend/app/main.py; then
  if grep -q "localhost:3000" backend/app/main.py; then
    check_pass "CORS allows localhost:3000"
  else
    check_fail "CORS does not allow localhost:3000"
  fi
else
  check_warn "CORS configuration not found"
fi
echo ""

# 6. Check frontend API configuration
echo "6️⃣  Checking frontend API configuration..."
if grep -q "API_BASE.*import.meta.env.VITE_API_BASE" frontend/src/services/api.js; then
  check_pass "Frontend uses VITE_API_BASE environment variable"
else
  check_fail "Frontend API configuration issue"
fi

if grep -q "USE_MOCK = false" frontend/src/services/api.js; then
  check_pass "Frontend connected to real backend (USE_MOCK=false)"
else
  check_warn "Frontend may be using mock mode"
fi
echo ""

# 7. Check upload progress features
echo "7️⃣  Checking upload progress features..."
if grep -q "uploading.*useState" frontend/src/App.jsx; then
  check_pass "Upload state management added to App.jsx"
else
  check_fail "Upload state not found in App.jsx"
fi

if grep -q "disabled.*=.*false" frontend/src/components/ChatInput.jsx; then
  check_pass "ChatInput handles disabled state"
else
  check_fail "ChatInput disabled state not implemented"
fi

if grep -q "Procesando documentos" frontend/src/components/MessageList.jsx; then
  check_pass "Upload indicator in MessageList"
else
  check_fail "Upload indicator not found in MessageList"
fi
echo ""

# 8. Check system message support
echo "8️⃣  Checking system message support..."
if grep -q 'role.*===.*"system"' frontend/src/components/MessageBubble.jsx; then
  check_pass "MessageBubble supports system messages"
else
  check_fail "System message support not found in MessageBubble"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Summary"
echo "=============================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}🎉 All checks passed! System is ready.${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. If containers aren't running: docker-compose up --build"
  echo "  2. Open browser: http://localhost:3000"
  echo "  3. Follow E2E_TESTING_GUIDE.md for complete testing"
  exit 0
else
  echo -e "${RED}⚠️  Some checks failed. Review the output above.${NC}"
  echo ""
  echo "Common fixes:"
  echo "  • Missing .env files: Copy from .env.example"
  echo "  • Containers not running: docker-compose up --build"
  echo "  • Backend not reachable: Check Docker logs"
  exit 1
fi

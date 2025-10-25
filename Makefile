.PHONY: setup build start stop restart clean logs test

# Default target
all: setup

# Setup the project (build and start)
setup: build start

# Build all services
build:
	docker-compose build

# Start all services
start:
	docker-compose up -d

# Stop all services
stop:
	docker-compose down

# Restart all services
restart: stop start

# Clean up containers and volumes
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# View logs
logs:
	docker-compose logs -f

# View logs for specific service
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Test the API endpoints
test:
	@echo "Testing API endpoints..."
	@echo "1. Health check:"
	curl -s http://localhost:8000/health | jq .
	@echo "\n2. Upload test file:"
	curl -X POST "http://localhost:8000/upload" \
		-H "accept: application/json" \
		-H "Content-Type: multipart/form-data" \
		-F "file=@README.md" \
		-F "user_id=test_user" | jq .
	@echo "\n3. Query test:"
	curl -X POST "http://localhost:8000/query" \
		-H "accept: application/json" \
		-H "Content-Type: application/json" \
		-d '{"query": "What is this project about?", "user_id": "test_user", "top_k": 3}' | jq .

# Install dependencies locally (for development)
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# Run backend locally (for development)
run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally (for development)
run-frontend:
	cd frontend && npm start

# Help
help:
	@echo "Available commands:"
	@echo "  setup     - Build and start all services"
	@echo "  build     - Build all Docker images"
	@echo "  start     - Start all services"
	@echo "  stop      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  logs      - View logs for all services"
	@echo "  logs-backend - View backend logs"
	@echo "  logs-frontend - View frontend logs"
	@echo "  test      - Test API endpoints"
	@echo "  install-backend - Install backend dependencies locally"
	@echo "  install-frontend - Install frontend dependencies locally"
	@echo "  run-backend - Run backend locally"
	@echo "  run-frontend - Run frontend locally"
	@echo "  help      - Show this help message"
# QA Bot - Full-Stack Application

A full-stack Q&A application built with FastAPI (backend) and React with TypeScript (frontend), orchestrated with Docker Compose.

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
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Orchestration config
└── README.md
```

## Features

- **Backend**: FastAPI with auto-reload support
- **Frontend**: React with TypeScript and hot-reloading
- **Docker**: Containerized development environment
- **CORS**: Configured for cross-origin requests
- **API**: RESTful endpoints for Q&A management
- **TypeScript**: Full type safety in the frontend

## Quick Start

1. **Clone and navigate to the project**:

   ```bash
   cd qa-bot
   ```

2. **Start the application**:

   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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

### Volume Mounts

- Source code is mounted as volumes for both services
- Changes are reflected immediately without rebuilding containers
- `node_modules` is excluded from frontend volume to prevent conflicts

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## Stopping the Application

```bash
docker-compose down
```

## Troubleshooting

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Permission issues**: On Linux/macOS, you might need to adjust file permissions
3. **Node modules**: If frontend issues occur, try rebuilding: `docker-compose up --build --force-recreate frontend`

## Next Steps

- Add a database (PostgreSQL, MongoDB, etc.)
- Implement user authentication
- Add more sophisticated Q&A features
- Deploy to production (Docker Swarm, Kubernetes, etc.)

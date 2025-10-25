#!/bin/bash

# QA Bot Setup Script
# This script helps you set up the QA Bot with PostgreSQL and Hugging Face API

set -e

echo "🚀 QA Bot Setup Script"
echo "======================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your Hugging Face API key:"
    echo "   1. Go to https://huggingface.co/settings/tokens"
    echo "   2. Create a new token"
    echo "   3. Copy the token and paste it in .env file replacing 'your_huggingface_api_key_here'"
    echo ""
    echo "Press Enter when you've added your API key..."
    read
fi

# Check if API key is set
if grep -q "your_huggingface_api_key_here" .env; then
    echo "❌ Please add your Hugging Face API key to the .env file first!"
    echo "   Edit .env and replace 'your_huggingface_api_key_here' with your actual API key"
    exit 1
fi

echo "🔧 Building and starting services..."
echo "   This will:"
echo "   - Build the backend and frontend containers"
echo "   - Start PostgreSQL database"
echo "   - Initialize database tables"
echo "   - Start the QA Bot application"
echo ""

# Build and start services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U qa_bot_user -d qa_bot > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not ready"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access your QA Bot:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Database Info:"
echo "   Host: localhost:5432"
echo "   Database: qa_bot"
echo "   Username: qa_bot_user"
echo "   Password: qa_bot_password"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Rebuild: docker-compose up --build"
echo ""
echo "📚 Next steps:"
echo "   1. Upload some documents via the web interface"
echo "   2. Ask questions about your documents"
echo "   3. Check the API documentation at http://localhost:8000/docs"

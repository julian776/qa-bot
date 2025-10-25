#!/bin/bash

# QA Bot Setup Script
# This script helps you set up the QA Bot with MongoDB, Qdrant, and OpenAI API

set -e

echo "🚀 QA Bot Setup Script"
echo "======================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your OpenAI API key:"
    echo "   1. Go to https://platform.openai.com/api-keys"
    echo "   2. Create a new API key"
    echo "   3. Copy the key and paste it in .env file replacing 'your_openai_api_key_here'"
    echo ""
    echo "Press Enter when you've added your API key..."
    read
fi

# Check if API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Please add your OpenAI API key to the .env file first!"
    echo "   Edit .env and replace 'your_openai_api_key_here' with your actual API key"
    exit 1
fi

echo "🔧 Building and starting services..."
echo "   This will:"
echo "   - Build the backend and frontend containers"
echo "   - Start MongoDB database"
echo "   - Start Qdrant vector database"
echo "   - Initialize database collections"
echo "   - Start the QA Bot application"
echo ""

# Build and start services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if services are running
echo "🔍 Checking service health..."

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is ready"
else
    echo "❌ MongoDB is not ready"
fi

# Check Qdrant
if curl -f http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant is ready"
else
    echo "❌ Qdrant is not ready"
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
echo "   MongoDB: localhost:27017"
echo "   Database: qa_bot"
echo "   Username: admin"
echo "   Password: password123"
echo ""
echo "   Qdrant: http://localhost:6333"
echo "   Collection: qa_bot_embeddings"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Rebuild: docker-compose up --build"
echo ""
echo "🧪 Test the system:"
echo "   python scripts/test_qa_bot.py"
echo ""
echo "📚 Next steps:"
echo "   1. Upload some documents via the web interface"
echo "   2. Ask questions about your documents"
echo "   3. Check the API documentation at http://localhost:8000/docs"
echo "   4. Run the test script to verify everything works"

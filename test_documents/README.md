# Example Dataset for QA Bot Testing

This directory contains sample documents and test queries for the QA Bot system.

## Sample Documents

### 1. AI and Machine Learning Overview

**File**: `ai_ml_overview.txt`
**Content**: Comprehensive overview of artificial intelligence and machine learning concepts, including definitions, applications, and future trends.

### 2. Docker and Containerization

**File**: `docker_guide.txt`
**Content**: Complete guide to Docker containerization, including installation, basic commands, Dockerfile creation, and best practices.

### 3. Python Programming Best Practices

**File**: `python_best_practices.txt`
**Content**: Essential Python programming best practices, code style guidelines, performance optimization tips, and common patterns.

### 4. Database Design Principles

**File**: `database_design.txt`
**Content**: Fundamental database design principles, normalization, indexing strategies, and performance optimization techniques.

### 5. API Development with FastAPI

**File**: `fastapi_guide.txt`
**Content**: Comprehensive guide to building REST APIs with FastAPI, including authentication, validation, testing, and deployment.

## Test Queries

### Basic Questions

- "What is machine learning?"
- "How do I create a Docker container?"
- "What are Python best practices?"
- "How do I design a database?"
- "What is FastAPI?"

### Advanced Questions

- "Explain the difference between supervised and unsupervised learning"
- "How do I optimize Docker image size?"
- "What are the benefits of using type hints in Python?"
- "What is database normalization and why is it important?"
- "How do I implement authentication in FastAPI?"

### Specific Technical Questions

- "What are the steps to create a Dockerfile?"
- "How do I handle errors in Python?"
- "What are the different types of database indexes?"
- "How do I validate request data in FastAPI?"
- "What are the advantages of containerization?"

## Usage Instructions

1. **Upload Documents**: Use the `/api/upload` endpoint to upload the sample documents
2. **Test Queries**: Use the `/api/query` endpoint to test the sample queries
3. **Verify Results**: Check that the system returns relevant chunks from the uploaded documents

## Expected Behavior

- Documents should be processed and chunked automatically
- Embeddings should be generated using OpenAI API
- Vectors should be stored in Qdrant
- Metadata should be stored in MongoDB
- Queries should return semantically similar chunks with similarity scores
- Results should be ranked by relevance

## Performance Testing

- Test with different similarity thresholds (0.5, 0.7, 0.9)
- Test with different top_k values (3, 5, 10)
- Test with various query lengths and complexities
- Monitor response times and accuracy

// MongoDB initialization script for QA Bot
// This script creates the necessary collections and indexes

// Switch to the qa_bot database
db = db.getSiblingDB('qa_bot');

// Create collections
db.createCollection('documents');
db.createCollection('chunks');
db.createCollection('queries');
db.createCollection('users');

// Create indexes for better performance
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "created_at": -1 });
db.documents.createIndex({ "user_id": 1, "created_at": -1 });

db.chunks.createIndex({ "user_id": 1 });
db.chunks.createIndex({ "document_id": 1 });
db.chunks.createIndex({ "chunk_index": 1 });
db.chunks.createIndex({ "user_id": 1, "document_id": 1 });

db.queries.createIndex({ "user_id": 1 });
db.queries.createIndex({ "created_at": -1 });
db.queries.createIndex({ "user_id": 1, "created_at": -1 });

db.users.createIndex({ "user_id": 1 }, { unique: true });

// Insert a sample user for testing
db.users.insertOne({
    "user_id": "demo_user",
    "username": "Demo User",
    "email": "demo@example.com",
    "created_at": new Date(),
    "settings": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "similarity_threshold": 0.7
    }
});

print("MongoDB initialization completed successfully!");

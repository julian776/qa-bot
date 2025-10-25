#!/usr/bin/env python3
"""
Test script for QA Bot API
This script demonstrates how to use the QA Bot API endpoints
"""

import requests
import json
import time
import os
from typing import List, Dict, Any

class QABotTester:
    """Test client for QA Bot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.user_id = "test_user"
    
    def test_health(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API is healthy")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to API: {e}")
            return False
    
    def upload_document(self, file_path: str) -> Dict[str, Any]:
        """Upload a document to the API"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'user_id': self.user_id}
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Document uploaded successfully: {result['filename']}")
                    print(f"Chunks: {result['total_chunks']}, Tokens: {result['total_tokens']}")
                    return result
                else:
                    print(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return {}
                    
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return {}
    
    def query_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query documents using the API"""
        try:
            payload = {
                "query": query,
                "user_id": self.user_id,
                "top_k": top_k,
                "similarity_threshold": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/api/query",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query successful: '{query}'")
                print(f"Found {result['total_results']} results in {result['processing_time']:.2f}s")
                
                for i, res in enumerate(result['results'], 1):
                    print(f"\n{i}. Score: {res['similarity_score']:.3f}")
                    print(f"   Document: {res['document_name']}")
                    print(f"   Text: {res['text_chunk'][:100]}...")
                
                return result['results']
            else:
                print(f"❌ Query failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                print("✅ System Statistics:")
                print(f"Vector Store: {stats['vector_store']['total_vectors']} vectors")
                print(f"Embedding Model: {stats['embedding_model']}")
                print(f"Embedding Dimension: {stats['embedding_dimension']}")
                print(f"MongoDB Connected: {stats['mongodb_connected']}")
                return stats
            else:
                print(f"❌ Stats request failed: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of the QA Bot system"""
        print("🚀 Starting QA Bot Comprehensive Test")
        print("=" * 50)
        
        # Test 1: Health Check
        print("\n1. Testing API Health...")
        if not self.test_health():
            print("❌ Health check failed, stopping tests")
            return
        
        # Test 2: Upload Sample Documents
        print("\n2. Uploading Sample Documents...")
        test_docs = [
            "test_documents/ai_ml_overview.txt",
            "test_documents/docker_guide.txt",
            "test_documents/python_best_practices.txt"
        ]
        
        uploaded_docs = []
        for doc_path in test_docs:
            if os.path.exists(doc_path):
                result = self.upload_document(doc_path)
                if result:
                    uploaded_docs.append(result)
                time.sleep(1)  # Small delay between uploads
            else:
                print(f"⚠️ Document not found: {doc_path}")
        
        if not uploaded_docs:
            print("❌ No documents uploaded, stopping tests")
            return
        
        # Test 3: System Statistics
        print("\n3. Checking System Statistics...")
        self.get_stats()
        
        # Test 4: Query Tests
        print("\n4. Testing Query Functionality...")
        test_queries = [
            "What is machine learning?",
            "How do I create a Docker container?",
            "What are Python best practices?",
            "Explain supervised learning",
            "How do I optimize Docker images?",
            "What is type hinting in Python?"
        ]
        
        for query in test_queries:
            print(f"\n--- Testing Query: '{query}' ---")
            results = self.query_documents(query)
            if results:
                print(f"✅ Query returned {len(results)} results")
            else:
                print("❌ Query returned no results")
            time.sleep(1)  # Small delay between queries
        
        # Test 5: Edge Cases
        print("\n5. Testing Edge Cases...")
        
        # Empty query
        print("Testing empty query...")
        self.query_documents("")
        
        # Very specific query
        print("Testing very specific query...")
        self.query_documents("What is the difference between supervised and unsupervised learning in machine learning?")
        
        # Non-existent topic
        print("Testing non-existent topic...")
        self.query_documents("How to build a spaceship?")
        
        print("\n🎉 Comprehensive test completed!")
        print("=" * 50)

def main():
    """Main function to run the tests"""
    tester = QABotTester()
    
    # Check if API is running
    if not tester.test_health():
        print("\n❌ QA Bot API is not running!")
        print("Please start the services with: docker-compose up")
        return
    
    # Run comprehensive test
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()

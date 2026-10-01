"""
WEAVIATE VECTOR DATABASE
Real vector database with free tier
"""
import weaviate
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class WeaviateDB:
    def __init__(self):
        # Connect to Weaviate Cloud
        self.client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL"),
            auth_client_secret=weaviate.AuthApiKey(os.getenv("WEAVIATE_API_KEY"))
        )
        
        # Create schema if it doesn't exist
        self._create_schema()
    
    def _create_schema(self):
        """Create the data schema for documents"""
        schema = {
            "classes": [
                {
                    "class": "Document",
                    "description": "A document in our knowledge base",
                    "vectorizer": "none",
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "The document text"
                        },
                        {
                            "name": "source",
                            "dataType": ["string"],
                            "description": "Document source/id"
                        }
                    ]
                }
            ]
        }
        
        try:
            self.client.schema.create(schema)
            print("Schema created")
        except Exception as e:
            print(f"Schema already exists or error: {e}")
    
    def add_document(self, doc_id: str, text: str, embedding: List[float]):
        """Add document with embedding to Weaviate"""
        self.client.data_object.create(
            class_name="Document",
            data_object={
                "content": text,
                "source": doc_id
            },
            vector=embedding
        )
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Search by embedding similarity"""
        results = self.client.query.get(
            "Document",
            ["content", "source", "_additional {distance}"]
        ).with_near_vector({
            "vector": query_embedding
        }).with_limit(k).do()
        
        # Format results
        documents = []
        for result in results.get("data", {}).get("Get", {}).get("Document", []):
            documents.append({
                'id': result['source'],
                'text': result['content'],
                'metadata': {'source': result['source']},
                'score': 1 - result['_additional']['distance']
            })
        
        return documents

"""Vector store service for code template retrieval"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Handle vector embeddings and similarity search for code templates"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="code_templates",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("Vector store initialized")
    
    def add_template(
        self,
        template_id: str,
        code: str,
        metadata: Dict,
        description: str = ""
    ):
        """Add a code template to the vector store"""
        try:
            # Create searchable text
            searchable_text = f"{description} {code}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text).tolist()
            
            # Add to collection
            self.collection.add(
                ids=[template_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[code]
            )
            
            logger.info(f"Added template {template_id} to vector store")
        except Exception as e:
            logger.error(f"Error adding template to vector store: {e}")
            raise
    
    def add_templates_batch(
        self,
        template_ids: List[str],
        codes: List[str],
        metadatas: List[Dict],
        descriptions: List[str]
    ):
        """Add multiple templates in batch"""
        try:
            # Create searchable texts
            searchable_texts = [
                f"{desc} {code}" 
                for desc, code in zip(descriptions, codes)
            ]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(searchable_texts).tolist()
            
            # Add to collection
            self.collection.add(
                ids=template_ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=codes
            )
            
            logger.info(f"Added {len(template_ids)} templates to vector store")
        except Exception as e:
            logger.error(f"Error adding templates batch: {e}")
            raise
    
    def search_similar_templates(
        self,
        query: str,
        n_results: int = 5,
        framework_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for similar code templates
        Returns: List of templates with code, metadata, and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build where filter
            where_filter = {}
            if framework_filter:
                where_filter["framework"] = framework_filter
            if category_filter:
                where_filter["category"] = category_filter
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            templates = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    templates.append({
                        'id': results['ids'][0][i],
                        'code': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            logger.info(f"Found {len(templates)} similar templates for query")
            return templates
            
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            return []
    
    def update_template(
        self,
        template_id: str,
        code: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None
    ):
        """Update a template in the vector store"""
        try:
            # Get existing template
            existing = self.collection.get(ids=[template_id])
            
            if not existing['ids']:
                logger.warning(f"Template {template_id} not found")
                return
            
            # Update fields
            new_code = code if code is not None else existing['documents'][0]
            new_metadata = metadata if metadata is not None else existing['metadatas'][0]
            new_description = description if description is not None else ""
            
            # Regenerate embedding
            searchable_text = f"{new_description} {new_code}"
            embedding = self.embedding_model.encode(searchable_text).tolist()
            
            # Update in collection
            self.collection.update(
                ids=[template_id],
                embeddings=[embedding],
                metadatas=[new_metadata],
                documents=[new_code]
            )
            
            logger.info(f"Updated template {template_id}")
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise
    
    def delete_template(self, template_id: str):
        """Delete a template from the vector store"""
        try:
            self.collection.delete(ids=[template_id])
            logger.info(f"Deleted template {template_id}")
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            raise
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID"""
        try:
            result = self.collection.get(ids=[template_id])
            
            if result['ids'] and len(result['ids']) > 0:
                return {
                    'id': result['ids'][0],
                    'code': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    def count_templates(self) -> int:
        """Get total number of templates"""
        return self.collection.count()

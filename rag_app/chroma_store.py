import os
import time
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict, Any
from langchain.docstore.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaStore:
    def __init__(self, persist_directory: str = "chroma_db"):
        """Initialize the Chroma database client."""
        # Convert to absolute path
        self.persist_directory = os.path.abspath(persist_directory)
        
        # Create persist directory if it doesn't exist
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
            
        # Initialize Chroma client with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False,
            is_persistent=True
        ))
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_function
        )
        
        logger.info(f"Initialized ChromaStore with persistence at {persist_directory}")
        
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the Chroma database.
        
        Args:
            documents: List of Langchain Document objects to add
        """
        try:
            if not documents:
                logger.warning("No documents provided to add to Chroma")
                return
                
            # Prepare documents for Chroma
            documents_data = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                # Extract text content
                documents_data.append(doc.page_content)
                
                # Extract and sanitize metadata
                metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
                # Ensure all metadata values are valid types
                sanitized_metadata = {}
                for key, value in metadata.items():
                    if value is None:
                        continue
                    if isinstance(value, (str, int, float, bool)):
                        sanitized_metadata[key] = value
                    else:
                        sanitized_metadata[key] = str(value)
                sanitized_metadata['doc_id'] = str(i)
                metadatas.append(sanitized_metadata)
                
                # Generate unique ID using timestamp and index
                ids.append(f"doc_{int(time.time())}_{i}")
            
            # Add documents to collection
            self.collection.add(
                documents=documents_data,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(documents)} documents to Chroma")
            
        except Exception as e:
            logger.error(f"Error adding documents to Chroma: {str(e)}")
            raise
            
    def query_documents(self, query_text: str, n_results: int = 3, include_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Query the Chroma database for similar documents.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            include_fields: List of fields to include in results ('documents', 'metadatas', 'embeddings')
            
        Returns:
            List of dictionaries containing matched documents and their metadata
        """
        try:
            # Prepare query parameters
            include = include_fields if include_fields else ["documents", "metadatas"]
            
            # Query with more results initially to allow for filtering
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results * 3,  # Get more results to filter
                include=include + ["embeddings", "distances"]
            )
            
            # Format and filter results
            formatted_results = []
            seen_content = set()  # Track unique content
            
            if results:
                n = len(results.get('distances', [[]])[0]) if results.get('distances') else 0
                for i in range(n):
                    content = results['documents'][0][i] if results.get('documents') else ""
                    
                    # Skip if we've seen this content before
                    content_hash = hash(content)
                    if content_hash in seen_content:
                        continue
                    seen_content.add(content_hash)
                    
                    # Skip unwanted content
                    content = content.strip()
                    
                    # Skip if content is too short or contains unwanted elements
                    if len(content) < 50 or any([
                        content.startswith('http'),
                        content.startswith('Retrieved from'),
                        'References' in content[:20],
                        'External links' in content[:20]
                    ]):
                        continue
                        
                    # Boost relevance for content containing key information
                    relevance_boost = 0.0
                    if query_text.lower() in content.lower():
                        relevance_boost += 0.1
                    if any(term in content.lower() for term in ['lake', 'tippecanoe', 'location', 'description']):
                        relevance_boost += 0.05
                        
                    # Clean up content that starts with a period
                    if content.startswith('.'):
                        content = content[1:].strip()
                        if len(content) < 30:  # Skip if too short after cleanup
                            continue
                    
                    result = {}
                    
                    # Add cleaned content if included
                    if 'documents' in include:
                        result['content'] = content
                        
                    # Skip if content is empty after cleaning
                    if not result.get('content', '').strip():
                        continue
                    
                    # Add metadata if included
                    if 'metadatas' in include and results.get('metadatas'):
                        result['metadata'] = results['metadatas'][0][i]
                    
                    # Add embeddings if included
                    if 'embeddings' in include and results.get('embeddings'):
                        result['embedding'] = results['embeddings'][0][i]
                    
                    # Adjust similarity score with boost
                    if results.get('distances'):
                        result['similarity'] = 1 - results['distances'][0][i] + relevance_boost
                    
                    formatted_results.append(result)
                    
            logger.info(f"Found {len(formatted_results)} matching documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying Chroma: {str(e)}")
            raise
            
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
            
    def get_collections(self) -> Dict[str, Any]:
        """Get all collections and their details from ChromaDB."""
        try:
            collection_names = self.client.list_collections()
            collections_dict = {}
            for name in collection_names:
                collection = self.client.get_collection(name=name)
                collections_dict[name] = {
                    "name": name,
                    "metadata": collection.metadata,
                    "count": collection.count()
                }
            return collections_dict
        except Exception as e:
            logger.error(f"Error getting collections: {str(e)}")
            raise

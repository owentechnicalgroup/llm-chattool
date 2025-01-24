import os
import chromadb
from chromadb.config import Settings
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
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
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
                
                # Extract metadata
                metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
                metadata['doc_id'] = str(i)
                metadatas.append(metadata)
                
                # Generate unique ID
                ids.append(f"doc_{i}")
            
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
            
    def query_documents(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the Chroma database for similar documents.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            
        Returns:
            List of dictionaries containing matched documents and their metadata
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': 1 - distance  # Convert distance to similarity score
                    })
                    
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
